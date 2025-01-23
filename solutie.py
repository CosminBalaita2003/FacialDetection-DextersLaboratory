# # import cv2 as cv
# # import os
# # import glob
# #
# # def resize_test_images(input_dir, output_dir, target_size=(450, 350)):
# #     """
# #     Redimensionează toate imaginile din input_dir la dimensiunea specificată și le salvează în output_dir.
# #     :param input_dir: Directorul de intrare cu imaginile originale.
# #     :param output_dir: Directorul de ieșire pentru imaginile redimensionate.
# #     :param target_size: Dimensiunea țintă pentru imaginile redimensionate (lățime, înălțime).
# #     """
# #     if not os.path.exists(output_dir):
# #         os.makedirs(output_dir)
# #         print(f"Created output directory: {output_dir}")
# #
# #     image_files = glob.glob(os.path.join(input_dir, '*.jpg'))
# #     print(f"Found {len(image_files)} images in {input_dir}.")
# #
# #     for i, image_file in enumerate(image_files):
# #         img = cv.imread(image_file)
# #         if img is None:
# #             print(f"Skipping {image_file}: Could not read image.")
# #             continue
# #
# #         resized_img = cv.resize(img, target_size, interpolation=cv.INTER_LINEAR)
# #         output_file = os.path.join(output_dir, os.path.basename(image_file))
# #         cv.imwrite(output_file, resized_img)
# #         print(f"Resized and saved image {i + 1}/{len(image_files)}: {output_file}")
# #
# #     print("Image resizing complete.")
# #
# # # Exemplu de utilizare
# # input_directory = 'poze_negative91/square'  # Directorul cu imaginile originale
# # output_directory = 'imagini_negative/square'  # Directorul pentru imaginile redimensionate
# # resize_test_images(input_directory, output_directory, target_size=(100,100))
# # # #
# import os
# import cv2
# import random
#
# # Setări directoare
# input_dir = "antrenare/deedee"  # Directorul cu imaginile originale
# annotation_file = "antrenare/deedee_annotations.txt"  # Fișierul cu adnotări
# output_dir = "poze_negative91"  # Directorul pentru imaginile negative
#
#
#
# # Creează directoarele pentru imaginile negative
#
# os.makedirs(os.path.join(output_dir), exist_ok=True)
#
# # Funcție pentru încărcarea adnotărilor
# def incarca_adnotari(annotation_file):
#     adnotari = {}
#     if not os.path.exists(annotation_file):
#         print(f"Fișierul de adnotări {annotation_file} nu există.")
#         return adnotari
#     with open(annotation_file, "r") as f:
#         for linie in f:
#             nume_imagine, xmin, ymin, xmax, ymax, _ = linie.strip().split()
#             xmin, ymin, xmax, ymax = map(int, [xmin, ymin, xmax, ymax])
#             if nume_imagine not in adnotari:
#                 adnotari[nume_imagine] = []
#             adnotari[nume_imagine].append((xmin, ymin, xmax, ymax))
#     return adnotari
#
# # Verifică dacă un dreptunghi se suprapune cu o față existentă
# def se_suprapune(rect, adnotari):
#     x1, y1, x2, y2 = rect
#     for (xmin, ymin, xmax, ymax) in adnotari:
#         if not (x2 < xmin or x1 > xmax or y2 < ymin or y1 > ymax):
#             return True
#     return False
#
# # Încărcare adnotări
# adnotari = incarca_adnotari(annotation_file)
#
# # Procesare imagini
# for imagine_nume in os.listdir(input_dir):
#     imagine_cale = os.path.join(input_dir, imagine_nume)
#
#     # Ignoră fișierele care nu sunt imagini
#     if not imagine_nume.endswith((".jpg", ".png")):
#         continue
#
#     imagine = cv2.imread(imagine_cale)
#     if imagine is None:
#         print(f"Nu am putut încărca {imagine_cale}, o sar.")
#         continue
#
#     inaltime, latime = imagine.shape[:2]
#     adnotari_imagine = adnotari.get(imagine_nume, [])
#
#     numar_decupaje = 0
#     incercari_max = 100  # Număr maxim de încercări pentru a găsi decupaje valide
#
#     while numar_decupaje < 6 and incercari_max > 0:
#         # Alege o categorie aleatoare și dimensiunile asociate
#
#         w, h = 100,100
#
#         # Generează coordonate aleatoare
#         x1 = random.randint(0, latime - w)
#         y1 = random.randint(0, inaltime - h)
#         x2 = x1 + w
#         y2 = y1 + h
#
#         # Verifică dacă dreptunghiul nu se suprapune cu vreo față
#         if not se_suprapune((x1, y1, x2, y2), adnotari_imagine):
#             # Decupează și salvează
#             decupaj = imagine[y1:y2, x1:x2]
#             nume_salveaza = f"deedee-{os.path.splitext(imagine_nume)[0]}_{x1}_{y1}.jpg"
#             cale_salveaza = os.path.join(output_dir, nume_salveaza)
#             cv2.imwrite(cale_salveaza, decupaj)
#             print(f"Salvat {cale_salveaza}")
#             numar_decupaje += 1
#         incercari_max -= 1  # Scade numărul de încercări
#
#     # Verificare dacă nu s-au generat suficiente cadrane
#     if numar_decupaje < 6:
#         print(f"Nu s-au putut genera toate cadranele pentru {imagine_nume}. S-au generat {numar_decupaje}.")
# # import os
# # # import cv2
# # #
# # # def redimensioneaza_la_dimensiune_fixa(imagine, dimensiune):
# # #     """
# # #     Redimensionează imaginea la o dimensiune fixă (dimensiune x dimensiune).
# # #     """
# # #     imagine_redimensionata = cv2.resize(imagine, (dimensiune, dimensiune))
# # #     return imagine_redimensionata
# # #
# # # def proceseaza_imagini(director_input, director_output, dimensiune=256):
# # #     """
# # #     Parcurge imaginile din structura simplificată `teste_pozitive/[nume_pers]`,
# # #     le redimensionează la dimensiunea fixă și le salvează într-un director de output.
# # #     """
# # #
# # #
# # #
# # #
# # #     # Cream structura directorului de output
# # #     cale_output = os.path.join(director_output)
# # #     os.makedirs(cale_output, exist_ok=True)
# # #
# # #
# # #     for fisier in os.listdir(director_input):
# # #         if fisier.endswith(('.jpg', '.png')):  # Doar imagini
# # #             cale_imagine = os.path.join(director_input, fisier)
# # #             imagine = cv2.imread(cale_imagine)
# # #
# # #             if imagine is None:
# # #                 print(f"Nu s-a putut încărca imaginea {cale_imagine}.")
# # #                 continue
# # #
# # #             # Redimensionăm imaginea la dimensiunea fixă
# # #             imagine_redimensionata = redimensioneaza_la_dimensiune_fixa(imagine, dimensiune)
# # #             #redenumire fisier adauga "neg" inainte de nume
# # #             fisier = "neg" + fisier
# # #             # Salvează imaginea în directorul de output
# # #             cale_salveaza = os.path.join(cale_output, fisier)
# # #             cv2.imwrite(cale_salveaza, imagine_redimensionata,)
# # #             print(f"Salvat: {cale_salveaza}")
# # #
# # # # Exemplu de utilizare
# # # director_input = "imgneg91"  # Înlocuiește cu calea către imaginile tale
# # # director_output = "Img-neg-sq"  # Înlocuiește cu calea unde vrei să salvezi imaginile redimensionate
# # #
# # # proceseaza_imagini(director_input, director_output, dimensiune=50)
import os
import cv2
import random


# Funcție pentru a calcula Intersection over Union (IoU)
def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    # Calculează aria de suprapunere
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)

    # Calculează aria totală combinată
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0


# Funcție pentru a genera imagini negative fără suprapunere
def extract_non_overlapping_patches(annotation_file, images_folder, output_folder, patch_size=100, patches_per_image=6,
                                    iou_threshold=0.0):
    with open(annotation_file, 'r') as file:
        lines = file.readlines()

    # Creează folderul pentru imaginile negative
    negative_folder = os.path.join(output_folder, "imagini_negative100")
    os.makedirs(negative_folder, exist_ok=True)

    # Grupare adnotări pe imagini
    annotations = {}
    for line in lines:
        parts = line.strip().split()
        img_name, xmin, ymin, xmax, ymax, label = parts
        if img_name not in annotations:
            annotations[img_name] = []
        annotations[img_name].append((int(xmin), int(ymin), int(xmax), int(ymax)))

    # Procesare imagini
    for img_name, bboxes in annotations.items():
        img_path = os.path.join(images_folder, img_name)
        if not os.path.exists(img_path):
            print(f"Imaginea {img_path} nu există!")
            continue

        image = cv2.imread(img_path)
        if image is None:
            print(f"Eroare la citirea imaginii {img_path}")
            continue

        img_h, img_w, _ = image.shape

        if img_h < patch_size or img_w < patch_size:
            print(f"Imaginea {img_name} este prea mică pentru a genera patch-uri de {patch_size}x{patch_size}.")
            continue
        extracted_patches = 0
        existing_patches = []  # Lista cu patch-uri deja extrase

        max_attempts = 100  # Limită de încercări pentru a genera un patch valid

        while extracted_patches < patches_per_image and max_attempts > 0:
            # Generează coordonate aleatorii pentru un patch
            x1 = random.randint(0, img_w - patch_size)
            y1 = random.randint(0, img_h - patch_size)
            x2 = x1 + patch_size
            y2 = y1 + patch_size

            new_patch = (x1, y1, x2, y2)

            # Verifică dacă patch-ul se suprapune (IoU > iou_threshold) cu chenarele fețelor sau alte patch-uri existente
            overlap_with_bboxes = any(calculate_iou(new_patch, bbox) > iou_threshold for bbox in bboxes)
            overlap_with_patches = any(calculate_iou(new_patch, patch) > iou_threshold for patch in existing_patches)

            if not overlap_with_bboxes and not overlap_with_patches:
                # Adaugă patch-ul la lista existentă
                existing_patches.append(new_patch)

                # Decupează și salvează patch-ul
                patch = image[y1:y2, x1:x2]
                patch_name = f"{img_name.split('.')[0]}{x1}{y1}_neg.jpg"
                patch_path = os.path.join(negative_folder, patch_name)
                cv2.imwrite(patch_path, patch)
                print(f"Salvat patch negativ: {patch_path}")
                extracted_patches += 1
            else:
                print("Patch suprapus găsit, încercăm din nou.")

            max_attempts -= 1

        if extracted_patches < patches_per_image:
            print(f"Nu s-au putut genera suficiente patch-uri pentru {img_name}. S-au extras doar {extracted_patches}.")

# Parametrii
annotation_file = "antrenare/deedee_annotations.txt"  # Fișierul de adnotări
images_folder = "antrenare/deedee"            # Folderul cu imaginile
output_folder = "antrenare"  # Folderul pentru imaginile negative
# Rulează scriptul
extract_non_overlapping_patches(annotation_file, images_folder, output_folder)