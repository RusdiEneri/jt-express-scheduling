import pandas as pd
import numpy as np

class MatrixBuilder:
    def __init__(self, df_karyawan):
        self.df = df_karyawan.copy()
        self.hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
        
        # 1. Pisahkan karyawan "SETIAP HARI" (Gene Locking)
        # Mereka tidak ikut proses GA, tapi akan kita masukkan lagi di hasil akhir
        self.karyawan_setiap_hari = self.df[self.df['Req Libur'] == 'SETIAP HARI']
        self.df_ga = self.df[self.df['Req Libur'] != 'SETIAP HARI'].reset_index(drop=True)
        
    def build_preference_matrix(self):
        """
        Mengubah kolom 'Req Libur' menjadi Matriks Bobot Preferensi.
        Jika karyawan minta libur hari X, bobotnya 1. Selain itu 0.
        Jika 'Bebas', semua bobot 0 (atau bisa diberi nilai kecil jika mau).
        """
        n_karyawan = len(self.df_ga)
        n_hari = len(self.hari)
        
        # Inisialisasi matriks bobot dengan nilai 0
        bobot_matrix = np.zeros((n_karyawan, n_hari))
        
        for i, row in self.df_ga.iterrows():
            req = row['Req Libur'].upper()
            if req in self.hari:
                idx_hari = self.hari.index(req)
                bobot_matrix[i, idx_hari] = 1.0 # Bobot 1 untuk hari yang diminta
            # Jika 'Bebas', biarkan 0 (netral)
            
        return self.df_ga, bobot_matrix, self.karyawan_setiap_hari

    def get_total_karyawan_ga(self):
        return len(self.df_ga)