import os
import cv2
from sklearn.svm import SVC
from skimage.feature import hog
import numpy as np
from joblib import dump, load
import argparse

# Setări directoare
pozitive_dirs = {
    "square": "teste_poz_pe_formw_redim/square",
    "horizontal": "teste_poz_pe_formw_redim/horizontal",
    "vertical": "teste_poz_pe_formw_redim/vertical"
}

negative_dirs = {
    "square": "output_negatives_redim_bun/square",
    "horizontal": "output_negatives_redim_bun/horizontal",
    "vertical": "output_negatives_redim_bun/vertical"
}

test_dir = "test_validare_primele_poze/"
output_dir = "output_detectii"
os.makedirs(output_dir, exist_ok=True)

dimensiuni = {
    "square": (50, 50),
    "horizontal": (75, 50),
    "vertical": (50, 75)
}

def extrage_caracteristici(imagine, dimensiune):
    imagine_redimensionata = cv2.resize(imagine, dimensiune)
    imagine_gri = cv2.cvtColor(imagine_redimensionata, cv2.COLOR_BGR2GRAY)
    caracteristici = hog(imagine_gri, orientations=9, pixels_per_cell=(8, 8),
                         cells_per_block=(2, 2), block_norm="L2-Hys", visualize=False)
    return caracteristici

def incarca_si_antreneaza_model(tip, pozitii_dir, negative_dir, dimensiune):
    X, y = [], []

    for imagine_nume in os.listdir(pozitii_dir):
        cale_imagine = os.path.join(pozitii_dir, imagine_nume)
        imagine = cv2.imread(cale_imagine)
        if imagine is not None:
            caracteristici = extrage_caracteristici(imagine, dimensiune)
            X.append(caracteristici)
            y.append(1)

    for imagine_nume in os.listdir(negative_dir):
        cale_imagine = os.path.join(negative_dir, imagine_nume)
        imagine = cv2.imread(cale_imagine)
        if imagine is not None:
            caracteristici = extrage_caracteristici(imagine, dimensiune)
            X.append(caracteristici)
            y.append(0)

    X, y = np.array(X), np.array(y)
    model = SVC(kernel='linear', probability=True)
    model.fit(X, y)
    dump(model, f"model_{tip}.joblib")
    print(f"Modelul pentru {tip} salvat în model_{tip}.joblib")
    return model

def nms(detectii, scoruri, prag_suprapunere):
    if len(detectii) == 0:
        return []

    detectii = np.array(detectii)
    scoruri = np.array(scoruri)

    x1 = detectii[:, 0]
    y1 = detectii[:, 1]
    x2 = x1 + detectii[:, 2]
    y2 = y1 + detectii[:, 3]

    arii = (x2 - x1 + 1) * (y2 - y1 + 1)
    ordonare = np.argsort(scoruri)[::-1]

    detectii_finale = []

    while len(ordonare) > 0:
        i = ordonare[0]
        detectii_finale.append(i)

        xx1 = np.maximum(x1[i], x1[ordonare[1:]])
        yy1 = np.maximum(y1[i], y1[ordonare[1:]])
        xx2 = np.minimum(x2[i], x2[ordonare[1:]])
        yy2 = np.minimum(y2[i], y2[ordonare[1:]])

        latime = np.maximum(0, xx2 - xx1 + 1)
        inaltime = np.maximum(0, yy2 - yy1 + 1)
        suprapunere = (latime * inaltime) / arii[ordonare[1:]]

        ordonare = ordonare[1:][suprapunere <= prag_suprapunere]

    return detectii[detectii_finale]

def detecteaza_pe_piramida(imagine, model, dimensiune, pas, prag_scor, scale):
    detectii, scoruri = [], []
    nivel = 0

    while imagine.shape[0] >= dimensiune[1] and imagine.shape[1] >= dimensiune[0]:
        for y in range(0, imagine.shape[0] - dimensiune[1] + 1, pas):
            for x in range(0, imagine.shape[1] - dimensiune[0] + 1, pas):
                patch = imagine[y:y + dimensiune[1], x:x + dimensiune[0]]
                patch_gri = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
                caracteristici = hog(patch_gri, orientations=9, pixels_per_cell=(8, 8),
                                     cells_per_block=(2, 2), block_norm="L2-Hys", visualize=False)
                scor = model.predict_proba([caracteristici])[0, 1]
                if scor > prag_scor:
                    x_orig = int(x * (scale ** nivel))
                    y_orig = int(y * (scale ** nivel))
                    w_orig = int(dimensiune[0] * (scale ** nivel))
                    h_orig = int(dimensiune[1] * (scale ** nivel))
                    detectii.append((x_orig, y_orig, w_orig, h_orig))
                    scoruri.append(scor)

        imagine = cv2.resize(imagine, (int(imagine.shape[1] / scale), int(imagine.shape[0] / scale)))
        nivel += 1

    return detectii, scoruri

# Parametri
prag_scor = 0.975
prag_suprapunere = 0
scale = 1.4

modele = {}
for tip, dim in dimensiuni.items():
    modele[tip] = incarca_si_antreneaza_model(tip, pozitive_dirs[tip], negative_dirs[tip], dim)

for imagine_nume in os.listdir(test_dir):
    cale_imagine = os.path.join(test_dir, imagine_nume)
    imagine_originala = cv2.imread(cale_imagine)
    if imagine_originala is None:
        print(f"Imaginea {cale_imagine} nu a putut fi încărcată. O sar.")
        continue

    detectii_finale = []
    scoruri_finale = []

    for tip, model in modele.items():
        detectii, scoruri = detecteaza_pe_piramida(imagine_originala, model, dimensiuni[tip], pas=10, prag_scor=prag_scor, scale=scale)
        detectii_finale.extend(detectii)
        scoruri_finale.extend(scoruri)

    detectii_nms = nms(detectii_finale, scoruri_finale, prag_suprapunere)

    for (x, y, w, h) in detectii_nms:
        cv2.rectangle(imagine_originala, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cale_salveaza = os.path.join(output_dir, imagine_nume)
    cv2.imwrite(cale_salveaza, imagine_originala)
    print(f"Salvată imaginea cu detectări: {cale_salveaza}")
