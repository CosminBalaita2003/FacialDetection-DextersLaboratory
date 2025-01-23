from Parameters import *
import numpy as np
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
import glob
import cv2 as cv

import pdb
import pickle
import ntpath
from copy import deepcopy
import timeit
from skimage.feature import hog
from joblib import Parallel, delayed


class FacialDetector:
    def __init__(self, params:Parameters):
        self.params = params
        self.best_model = None

    # def detect_on_pyramid(self, image, model, window_size, step_size, score_threshold, fixed_scales):
    #     """
    #     Detecteaza fete folosind redimensionari fixe ale imaginii.
    #     :param image: Imaginea originala (in tonuri de gri).
    #     :param model: Modelul antrenat (SVM).
    #     :param window_size: Dimensiunea ferestrei glisante (lațime, înalțime).
    #     :param step_size: Pasul ferestrei glisante.
    #     :param score_threshold: Pragul de scor pentru a accepta o detectare.
    #     :param fixed_scales: Lista de scale predefinite pentru redimensionarea imaginii.
    #     :return: Lista de detectari si scoruri.
    #     """
    #     detections = []
    #     scores = []
    #     level = 0

    #     for scale in fixed_scales:
    #         resized_image = cv.resize(image, None, fx=scale, fy=scale, interpolation=cv.INTER_LINEAR)
    #         print(f"Processing scale {level} with image shape {resized_image.shape}...")

    #         for y in range(0, resized_image.shape[0] - window_size[1] + 1, step_size):
    #             for x in range(0, resized_image.shape[1] - window_size[0] + 1, step_size):
    #                 patch = resized_image[y:y + window_size[1], x:x + window_size[0]]
    #                 if patch.shape[:2] != window_size:
    #                     continue

    #                 # Extragem descriptorii HOG
    #                 features = hog(patch,
    #                                pixels_per_cell=(self.params.dim_hog_cell, self.params.dim_hog_cell),
    #                                cells_per_block=(2, 2),
    #                                feature_vector=True)

    #                 # Prezicem scorul
    #                 score = model.decision_function([features])[0]
    #                 if score > score_threshold:
    #                     x_orig = int(x / scale)
    #                     y_orig = int(y / scale)
    #                     w_orig = int(window_size[0] / scale)
    #                     h_orig = int(window_size[1] / scale)
    #                     detections.append((x_orig, y_orig, x_orig + w_orig, y_orig + h_orig))
    #                     scores.append(score)

    #         level += 1

    #     return np.array(detections), np.array(scores)
    def detect_on_pyramid(self, image, model, window_size, step_size, score_threshold, fixed_scales):
        """
        Detecteaza fete folosind redimensionari fixe ale imaginii, cu procesare paralela.
        """


        def process_window(x, y, resized_image, model, window_size, scale, dim_hog_cell):
            patch = resized_image[y:y + window_size[1], x:x + window_size[0]]
            if patch.shape[:2] != window_size:
                return None  # Ignoram ferestrele incomplete

            # Extragem descriptorii HOG
            features = hog(
                patch,
                pixels_per_cell=(dim_hog_cell, dim_hog_cell),
                cells_per_block=(2, 2),
                feature_vector=True
            )

            # Prezicem scorul
            score = model.decision_function([features])[0]
            if score > 0:  # Consideram doar scoruri pozitive
                x_orig = int(x / scale)
                y_orig = int(y / scale)
                w_orig = int(window_size[0] / scale)
                h_orig = int(window_size[1] / scale)
                return (x_orig, y_orig, x_orig + w_orig, y_orig + h_orig), score
            return None

        detections = []
        scores = []
        level = 0

        for scale in fixed_scales:
            resized_image = cv.resize(image, None, fx=scale, fy=scale, interpolation=cv.INTER_LINEAR)
            print(f"Processing scale {level} with image shape {resized_image.shape}...")

            # Procesare paralela a ferestrelor glisante
            results = Parallel(n_jobs=-1)(
                delayed(process_window)(x, y, resized_image, model, window_size, scale, self.params.dim_hog_cell)
                for y in range(0, resized_image.shape[0] - window_size[1] + 1, step_size)
                for x in range(0, resized_image.shape[1] - window_size[0] + 1, step_size)
            )

            # Filtram rezultatele None si separam detectarile de scoruri
            for result in results:
                if result is not None:
                    det, score = result
                    if score > score_threshold:  # Aplicam pragul de scor
                        detections.append(det)
                        scores.append(score)

            level += 1

        return np.array(detections), np.array(scores)


    def get_positive_descriptors(self):
        # in aceasta functie calculam descriptorii pozitivi
        # vom returna un numpy array de dimensiuni NXD
        # unde N - numar exemplelor pozitive
        # iar D - dimensiunea descriptorului
        # D = (params.dim_window/params.dim_hog_cell - 1) ^ 2 * params.dim_descriptor_cell (fetele sunt patrate)

        images_path = os.path.join(self.params.dir_pos_examples, '*.jpg')
        files = glob.glob(images_path)
        num_images = len(files)
        positive_descriptors = []
        print('Calculam descriptorii pt %d imagini pozitive...' % num_images)
        for i in range(num_images):
            print('Procesam exemplul pozitiv numarul %d...' % i)
            img = cv.imread(files[i], cv.IMREAD_GRAYSCALE)
            # TODO: sterge
            features = hog(img, pixels_per_cell=(self.params.dim_hog_cell, self.params.dim_hog_cell),
                           cells_per_block=(2, 2), feature_vector=True)
            print(len(features))

            positive_descriptors.append(features)
            if self.params.use_flip_images:
                features = hog(np.fliplr(img), pixels_per_cell=(self.params.dim_hog_cell, self.params.dim_hog_cell),
                               cells_per_block=(2, 2), feature_vector=True)
                positive_descriptors.append(features)

        positive_descriptors = np.array(positive_descriptors)
        return positive_descriptors

    # def get_negative_descriptors(self):
    #     # in aceasta functie calculam descriptorii negativi
    #     # vom returna un numpy array de dimensiuni NXD
    #     # unde N - numar exemplelor negative
    #     # iar D - dimensiunea descriptorului
    #     # avem 274 de imagini negative, vream sa avem self.params.number_negative_examples (setat implicit cu 10000)
    #     # de exemple negative, din fiecare imagine vom genera aleator self.params.number_negative_examples // 274
    #     # patch-uri de dimensiune 36x36 pe care le vom considera exemple negative

    #     images_path = os.path.join(self.params.dir_neg_examples, '*.jpg')
    #     files = glob.glob(images_path)
    #     num_images = len(files)
    #     num_negative_per_image = self.params.number_negative_examples // num_images
    #     negative_descriptors = []
    #     print('Calculam descriptorii pt %d imagini negative' % num_images)
    #     for i in range(num_images):
    #         print('Procesam exemplul negativ numarul %d...' % i)
    #         img = cv.imread(files[i], cv.IMREAD_GRAYSCALE)
    #         # TODO: completati codul functiei in continuare
    #         num_rows = img.shape[0]
    #         num_cols = img.shape[1]
    #         x = np.random.randint(low=0, high=num_cols - self.params.dim_window, size=num_negative_per_image)
    #         y = np.random.randint(low=0, high=num_rows - self.params.dim_window, size=num_negative_per_image)

    #         for idx in range(len(y)):
    #             patch = img[y[idx]: y[idx] + self.params.dim_window, x[idx]: x[idx] + self.params.dim_window]
    #             descr = hog(patch, pixels_per_cell=(self.params.dim_hog_cell, self.params.dim_hog_cell),
    #                         cells_per_block=(2, 2), feature_vector=False)
    #             negative_descriptors.append(descr.flatten())

    #     negative_descriptors = np.array(negative_descriptors)
    #     return negative_descriptors

    def get_negative_descriptors(self):
        """
        Calculam descriptorii pentru imaginile negative deja salvate.
        Returnam un numpy array de dimensiuni N x D, unde:
            N = numarul total de exemple negative
            D = dimensiunea unui descriptor HOG
        """
        images_path = os.path.join(self.params.dir_neg_examples, '*.jpg')
        files = glob.glob(images_path)
        num_images = len(files)
        negative_descriptors = []

        print(f"Calculam descriptorii pentru {num_images} imagini negative...")

        for i, file_path in enumerate(files):
            print(f"Procesam imaginea negativa numarul {i + 1}/{num_images} ({file_path})...")
            img = cv.imread(file_path, cv.IMREAD_GRAYSCALE)

            # Verificam dimensiunea imaginii
            if img.shape[0] < self.params.dim_window or img.shape[1] < self.params.dim_window:
                print(f"Imaginea {file_path} este prea mică pentru a calcula descriptorii (dimensiune: {img.shape}).")
                continue

            # Calculam descriptorul HOG pentru intreaga imagine
            descr = hog(
                img,
                pixels_per_cell=(self.params.dim_hog_cell, self.params.dim_hog_cell),
                cells_per_block=(2, 2),
                feature_vector=True  # Calculam un vector caracteristic unic pentru intreaga imagine
            )

            negative_descriptors.append(descr)

        negative_descriptors = np.array(negative_descriptors)

        print(f"Am calculat {len(negative_descriptors)} descriptori negativi.")
        return negative_descriptors


    def train_classifier(self, training_examples, train_labels):
        svm_file_name = os.path.join(self.params.dir_save_files, 'best_model_%d_%d_%d' %
                                     (self.params.dim_hog_cell, self.params.number_negative_examples,
                                      self.params.number_positive_examples))
        if os.path.exists(svm_file_name):
            self.best_model = pickle.load(open(svm_file_name, 'rb'))
            return

        best_accuracy = 0
        best_c = 0
        best_model = None
        Cs = [10 ** -5, 10 ** -4,  10 ** -3,  10 ** -2, 10 ** -1, 10 ** 0]
        for c in Cs:
            print('Antrenam un clasificator pentru c=%f' % c)
            model = LinearSVC(C=c)
            model.fit(training_examples, train_labels)
            acc = model.score(training_examples, train_labels)
            print(acc)
            if acc > best_accuracy:
                best_accuracy = acc
                best_c = c
                best_model = deepcopy(model)

        print('Performanta clasificatorului optim pt c = %f' % best_c)
        # salveaza clasificatorul
        pickle.dump(best_model, open(svm_file_name, 'wb'))

        # vizualizeaza cat de bine sunt separate exemplele pozitive de cele negative dupa antrenare
        # ideal ar fi ca exemplele pozitive sa primeasca scoruri > 0, iar exemplele negative sa primeasca scoruri < 0
        scores = best_model.decision_function(training_examples)
        self.best_model = best_model
        positive_scores = scores[train_labels > 0]
        negative_scores = scores[train_labels <= 0]


        plt.plot(np.sort(positive_scores))
        plt.plot(np.zeros(len(positive_scores)+len(negative_scores)))

        plt.plot(np.sort(negative_scores))
        plt.xlabel('Nr example antrenare')
        plt.ylabel('Scor clasificator')
        plt.title('Distributia scorurilor clasificatorului pe exemplele de antrenare')
        plt.legend(['Scoruri exemple pozitive', '0', 'Scoruri exemple negative'])
        plt.show()



    def intersection_over_union(self, bbox_a, bbox_b):
        x_a = max(bbox_a[0], bbox_b[0])
        y_a = max(bbox_a[1], bbox_b[1])
        x_b = min(bbox_a[2], bbox_b[2])
        y_b = min(bbox_a[3], bbox_b[3])

        inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)

        box_a_area = (bbox_a[2] - bbox_a[0] + 1) * (bbox_a[3] - bbox_a[1] + 1)
        box_b_area = (bbox_b[2] - bbox_b[0] + 1) * (bbox_b[3] - bbox_b[1] + 1)

        iou = inter_area / float(box_a_area + box_b_area - inter_area)

        return iou

    def non_maximal_suppression(self, image_detections, image_scores, image_size):
        """
        Detectiile cu scor mare suprima detectiile ce se suprapun cu acestea dar au scor mai mic.
        Detectiile se pot suprapune partial, dar centrul unei detectii nu poate
        fi in interiorul celeilalte detectii.
        :param image_detections:  numpy array de dimensiune NX4, unde N este numarul de detectii.
        :param image_scores: numpy array de dimensiune N
        :param image_size: tuplu, dimensiunea imaginii
        :return: image_detections si image_scores care sunt maximale.
        """

        # xmin, ymin, xmax, ymax
        x_out_of_bounds = np.where(image_detections[:, 2] > image_size[1])[0]
        y_out_of_bounds = np.where(image_detections[:, 3] > image_size[0])[0]
        print(x_out_of_bounds, y_out_of_bounds)
        image_detections[x_out_of_bounds, 2] = image_size[1]
        image_detections[y_out_of_bounds, 3] = image_size[0]
        sorted_indices = np.flipud(np.argsort(image_scores))
        sorted_image_detections = image_detections[sorted_indices]
        sorted_scores = image_scores[sorted_indices]

        is_maximal = np.ones(len(image_detections)).astype(bool)
        iou_threshold = 0.3
        for i in range(len(sorted_image_detections) - 1):
            if is_maximal[i] == True:
                for j in range(i + 1, len(sorted_image_detections)):
                    if is_maximal[j] == True:
                        if self.intersection_over_union(sorted_image_detections[i],sorted_image_detections[j]) > iou_threshold:is_maximal[j] = False
                        else:  # verificam daca centrul detectiei este in mijlocul detectiei cu scor mai mare
                            c_x = (sorted_image_detections[j][0] + sorted_image_detections[j][2]) / 2
                            c_y = (sorted_image_detections[j][1] + sorted_image_detections[j][3]) / 2
                            if sorted_image_detections[i][0] <= c_x <= sorted_image_detections[i][2] and \
                                    sorted_image_detections[i][1] <= c_y <= sorted_image_detections[i][3]:
                                is_maximal[j] = False
        return sorted_image_detections[is_maximal], sorted_scores[is_maximal]

    def run(self):
        """
        Rulare detecție pe toate imaginile de test folosind o piramida de scale, cu suprimare a suprapunerilor.
        """
        test_images_path = os.path.join(self.params.dir_test_examples, '*.jpg')
        test_files = glob.glob(test_images_path)
        all_detections = []
        all_scores = []
        all_file_names = []

        print(f'Processing {len(test_files)} test images...')

        total_detections = 0  # Contor pentru toate detectarile

        for i, test_file in enumerate(test_files):
            img = cv.imread(test_file, cv.IMREAD_GRAYSCALE)
            print(f'Processing image {i + 1}/{len(test_files)}: {test_file}')
            # fixed_scales = [1.0, 0.7, 0.3, 0.1]
            fixed_scales = [1.0, 0.8, 0.6, 0.4, 0.2, 0.05]  # Scale fixe
            detections, scores = self.detect_on_pyramid(
                image=img,
                model=self.best_model,
                window_size=(self.params.dim_window, self.params.dim_window),
                step_size=self.params.dim_hog_cell,
                score_threshold=self.params.threshold,
                fixed_scales=fixed_scales
            )

            print(f'Found {len(detections)} detections in image {test_file}')

            # Aplicam suprimarea non-maximala pentru aceasta imagine
            if len(detections) > 0:
                detections, scores = self.non_maximal_suppression(
                    np.array(detections),
                    np.array(scores),
                    img.shape
                )

            print(f'After NMS: {len(detections)} detections remain.')

            total_detections += len(detections)

            # Adăugam detectarile si scorurile
            all_detections.extend(detections)
            all_scores.extend(scores)
            all_file_names.extend([os.path.basename(test_file)] * len(detections))

        print(f'Total detections across all images after NMS: {total_detections}')

        # Salveaza rezultatele în fișierele specificate
        detections_file = os.path.join(self.params.dir_save_solution, "detections_all_faces.npy")

        scores_file = os.path.join(self.params.dir_save_solution, "scores_all_faces.npy")

        file_names_file = os.path.join(self.params.dir_save_solution, "file_names_all_faces.npy")

        np.save(detections_file, all_detections)
        np.save(scores_file, all_scores)
        np.save(file_names_file, all_file_names)

        print(f"Saved detections to {detections_file}")
        print(f"Saved scores to {scores_file}")
        print(f"Saved file names to {file_names_file}")
        return np.array(all_detections), np.array(all_scores), np.array(all_file_names)

    def compute_average_precision(self, rec, prec):
        # functie adaptata din 2010 Pascal VOC development kit
        m_rec = np.concatenate(([0], rec, [1]))
        m_pre = np.concatenate(([0], prec, [0]))
        for i in range(len(m_pre) - 1, -1, 1):
            m_pre[i] = max(m_pre[i], m_pre[i + 1])
        m_rec = np.array(m_rec)
        i = np.where(m_rec[1:] != m_rec[:-1])[0] + 1
        average_precision = np.sum((m_rec[i] - m_rec[i - 1]) * m_pre[i])
        return average_precision

    def eval_detections(self, detections, scores, file_names):
        if detections is None:
            print("Eroare: detections este None!")
            return  # Sau poti sa arunci o excepție, depinde de context

        ground_truth_file = np.loadtxt(self.params.path_annotations, dtype='str')
        ground_truth_file_names = np.array(ground_truth_file[:, 0])
        ground_truth_detections = np.array(ground_truth_file[:, 1:], np.int32)

        num_gt_detections = len(ground_truth_detections)  # numar total de adevarat pozitive
        gt_exists_detection = np.zeros(num_gt_detections)
        # sorteazam detectiile dupa scorul lor
        sorted_indices = np.argsort(scores)[::-1]
        file_names = file_names[sorted_indices]
        scores = scores[sorted_indices]
        detections = detections[sorted_indices]

        num_detections = len(detections)
        true_positive = np.zeros(num_detections)
        false_positive = np.zeros(num_detections)
        duplicated_detections = np.zeros(num_detections)

        for detection_idx in range(num_detections):
            indices_detections_on_image = np.where(ground_truth_file_names == file_names[detection_idx])[0]

            gt_detections_on_image = ground_truth_detections[indices_detections_on_image]
            bbox = detections[detection_idx]
            max_overlap = -1
            index_max_overlap_bbox = -1
            for gt_idx, gt_bbox in enumerate(gt_detections_on_image):
                overlap = self.intersection_over_union(bbox, gt_bbox)
                if overlap > max_overlap:
                    max_overlap = overlap
                    index_max_overlap_bbox = indices_detections_on_image[gt_idx]

            # clasifica o detectie ca fiind adevarat pozitiva / fals pozitiva
            if max_overlap >= 0.3:
                if gt_exists_detection[index_max_overlap_bbox] == 0:
                    true_positive[detection_idx] = 1
                    gt_exists_detection[index_max_overlap_bbox] = 1
                else:
                    false_positive[detection_idx] = 1
                    duplicated_detections[detection_idx] = 1
            else:
                false_positive[detection_idx] = 1

        cum_false_positive = np.cumsum(false_positive)
        cum_true_positive = np.cumsum(true_positive)

        rec = cum_true_positive / num_gt_detections
        prec = cum_true_positive / (cum_true_positive + cum_false_positive)
        average_precision = self.compute_average_precision(rec, prec)
        plt.plot(rec, prec, '-')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Average precision %.3f' % average_precision)
        plt.savefig(os.path.join(self.params.dir_save_files, 'precizie_medie.png'))
        plt.show()
