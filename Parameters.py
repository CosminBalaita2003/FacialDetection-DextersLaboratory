import os

class Parameters:
    def __init__(self):
        self.base_dir = ''
        self.dir_pos_examples = os.path.join(self.base_dir, 'imagini_pozitive')
        self.dir_neg_examples = os.path.join(self.base_dir, 'imagini_negative') # imgneg91 -> 0.491
        self.dir_test_examples = os.path.join(self.base_dir,'validare/validare')  # 'exempleTest/CursVA'   'exempleTest/CMU+MIT'
        self.path_annotations = os.path.join(self.base_dir, 'validare/task1_gt_validare.txt')
        self.dir_save_files = os.path.join(self.base_dir, 'salveazaFisiere')
        if not os.path.exists(self.dir_save_files):
            os.makedirs(self.dir_save_files)
            print('directory created: {} '.format(self.dir_save_files))
        else:
            print('directory {} exists '.format(self.dir_save_files))
        self.dir_save_solution = os.path.join(self.base_dir, 'evaluare/fisiere_solutie/341_Balaita_Cosmin/task1')
        if not os.path.exists(self.dir_save_solution):
            os.makedirs(self.dir_save_solution)
            print(f"Directory created: {self.dir_save_solution}")
        else:
            print(f"Directory {self.dir_save_solution} exists")

        # set the parameters
        self.dim_window = 100 # exemplele pozitive (fete de oameni cropate) au 36x36 pixeli
        self.dim_hog_cell = 8  # dimensiunea celulei
        self.dim_descriptor_cell = 100  # dimensiunea descriptorului unei celule
        self.overlap = 0.3
        self.number_positive_examples = 5813  # numarul exemplelor pozitive
        self.number_negative_examples = 23357  # numarul exemplelor negative 23357 imagini_negative/square
        self.overlap = 0.3
        self.has_annotations = False
        self.threshold = 2.5