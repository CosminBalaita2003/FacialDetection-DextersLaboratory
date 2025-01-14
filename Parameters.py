import os

class Parameters:
    def __init__(self):
        self.base_dir = ''
        self.dir_pos_examples = os.path.join(self.base_dir, 'teste_poz_pe_formw_redim/square')
        self.dir_neg_examples = os.path.join(self.base_dir, 'output_negatives_redim_bun/square')
        self.dir_test_examples = os.path.join(self.base_dir,'validare/validare')  # 'exempleTest/CursVA'   'exempleTest/CMU+MIT'
        self.path_annotations = os.path.join(self.base_dir, 'validare/task1_gt_validare.txt')
        self.dir_save_files = os.path.join(self.base_dir, 'salveazaFisiere')
        if not os.path.exists(self.dir_save_files):
            os.makedirs(self.dir_save_files)
            print('directory created: {} '.format(self.dir_save_files))
        else:
            print('directory {} exists '.format(self.dir_save_files))

        # set the parameters
        self.dim_window = 50  # exemplele pozitive (fete de oameni cropate) au 36x36 pixeli
        self.dim_hog_cell = 8  # dimensiunea celulei
        self.dim_descriptor_cell = 50  # dimensiunea descriptorului unei celule
        self.overlap = 0.3
        self.number_positive_examples = 2666  # numarul exemplelor pozitive
        self.number_negative_examples = 9304  # numarul exemplelor negative
        self.overlap = 0.3
        self.has_annotations = False
        self.threshold = 0
