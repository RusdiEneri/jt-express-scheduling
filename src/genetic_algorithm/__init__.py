class GeneticAlgorithm:
    def __init__(self, 
                 df_karyawan: pd.DataFrame,
                 bobot_matrix: np.ndarray,
                 karyawan_setiap_hari: pd.DataFrame,
                 population_size: int = 100,
                 generations: int = 500,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 min_piket_per_hari: int = 5,
                 piket_per_minggu: int = 1,  # 🔥 BARU
                 piket_per_bulan: int = 4):   # 🔥 BARU
        
        # ... (kode existing)
        self.min_piket_per_hari = min_piket_per_hari
        self.piket_per_minggu = piket_per_minggu
        self.piket_per_bulan = piket_per_bulan