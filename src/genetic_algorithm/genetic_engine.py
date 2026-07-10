import numpy as np
import random
from typing import List, Tuple, Dict
import pandas as pd

class Chromosome:
    """
    Representasi Kromosom untuk Penjadwalan
    """
    def __init__(self, n_karyawan: int, n_hari: int = 7):
        self.n_karyawan = n_karyawan
        self.n_hari = n_hari
        self.schedule = np.zeros((n_karyawan, n_hari), dtype=int)
        self.fitness = 0.0
        
    def initialize_random(self):
        """Inisialisasi kromosom secara acak dengan 2 hari libur per karyawan"""
        for i in range(self.n_karyawan):
            libur_days = random.sample(range(self.n_hari), 2)
            for day in libur_days:
                self.schedule[i, day] = 1
        return self
    
    def clone(self):
        """Membuat salinan kromosom"""
        new_chrom = Chromosome(self.n_karyawan, self.n_hari)
        new_chrom.schedule = self.schedule.copy()
        new_chrom.fitness = self.fitness
        return new_chrom


class GeneticAlgorithm:
    def __init__(self, 
                 df_karyawan: pd.DataFrame,
                 bobot_matrix: np.ndarray,
                 karyawan_setiap_hari: pd.DataFrame,
                 population_size: int = 100,
                 generations: int = 500,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 min_piket_per_hari: int = 5):
        
        self.df_karyawan = df_karyawan
        self.bobot_matrix = bobot_matrix
        self.karyawan_setiap_hari = karyawan_setiap_hari
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.min_piket_per_hari = min_piket_per_hari
        
        self.n_karyawan = len(df_karyawan)
        self.n_hari = 7
        
        self.population = []
        self.best_chromosome = None
        self.best_fitness = -float('inf')
        
        # 🔥 PENTING: Inisialisasi list untuk menyimpan history konvergensi
        self.history = [] 
        
    def create_initial_population(self):
        """Membuat populasi awal secara acak"""
        self.population = []
        for _ in range(self.population_size):
            chrom = Chromosome(self.n_karyawan, self.n_hari)
            chrom.initialize_random()
            self.population.append(chrom)
            
    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """Fungsi Fitness dengan Hard dan Soft Constraints"""
        fitness = 0.0
        
        # 1. HARD CONSTRAINT: Cek jumlah hari libur per karyawan (harus = 2)
        for i in range(self.n_karyawan):
            total_libur = np.sum(chromosome.schedule[i, :])
            if total_libur == 2:
                fitness += 100
            else:
                fitness -= abs(total_libur - 2) * 50
        
        # 2. HARD CONSTRAINT: Cek minimum piket per hari
        for day in range(self.n_hari):
            n_piket = np.sum(chromosome.schedule[:, day] == 0)
            n_piket += len(self.karyawan_setiap_hari)
            
            if n_piket >= self.min_piket_per_hari:
                fitness += 50
            else:
                fitness -= (self.min_piket_per_hari - n_piket) * 100
        
        # 3. SOFT CONSTRAINT: Preferensi libur karyawan
        for i in range(self.n_karyawan):
            for day in range(self.n_hari):
                if chromosome.schedule[i, day] == 1:
                    fitness += self.bobot_matrix[i, day] * 30
        
        # 4. BONUS: Distribusi libur yang merata
        for day in range(self.n_hari):
            n_libur = np.sum(chromosome.schedule[:, day])
            ideal_libur = self.n_karyawan * 2 / 7
            deviation = abs(n_libur - ideal_libur)
            if deviation < 3:
                fitness += 10
        
        return fitness
    
    def selection(self) -> Chromosome:
        """Tournament Selection"""
        tournament_size = 5
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Uniform Crossover"""
        if random.random() > self.crossover_rate:
            return parent1.clone(), parent2.clone()
        
        child1 = Chromosome(self.n_karyawan, self.n_hari)
        child2 = Chromosome(self.n_karyawan, self.n_hari)
        
        for i in range(self.n_karyawan):
            for day in range(self.n_hari):
                if random.random() < 0.5:
                    child1.schedule[i, day] = parent1.schedule[i, day]
                    child2.schedule[i, day] = parent2.schedule[i, day]
                else:
                    child1.schedule[i, day] = parent2.schedule[i, day]
                    child2.schedule[i, day] = parent1.schedule[i, day]
        
        child1 = self.repair_chromosome(child1)
        child2 = self.repair_chromosome(child2)
        
        return child1, child2
    
    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """Swap Mutation"""
        mutated = chromosome.clone()
        
        for i in range(self.n_karyawan):
            if random.random() < self.mutation_rate:
                libur_days = np.where(mutated.schedule[i, :] == 1)[0].tolist()
                
                if len(libur_days) == 2:
                    day_to_swap = random.choice(libur_days)
                    available_days = [d for d in range(self.n_hari) if d not in libur_days]
                    if available_days:
                        new_day = random.choice(available_days)
                        mutated.schedule[i, day_to_swap] = 0
                        mutated.schedule[i, new_day] = 1
        
        return mutated
    
    def repair_chromosome(self, chromosome: Chromosome) -> Chromosome:
        """Repair chromosome agar setiap karyawan tetap punya 2 hari libur"""
        repaired = chromosome.clone()
        
        for i in range(self.n_karyawan):
            libur_days = np.where(repaired.schedule[i, :] == 1)[0].tolist()
            n_libur = len(libur_days)
            
            if n_libur > 2:
                excess = n_libur - 2
                days_to_remove = random.sample(libur_days, excess)
                for day in days_to_remove:
                    repaired.schedule[i, day] = 0
            elif n_libur < 2:
                available_days = [d for d in range(self.n_hari) if d not in libur_days]
                days_to_add = random.sample(available_days, 2 - n_libur)
                for day in days_to_add:
                    repaired.schedule[i, day] = 1
        
        return repaired
    
    def run(self, callback=None) -> Chromosome:
        """Main loop Genetic Algorithm"""
        print("🔬 Memulai Genetic Algorithm...")
        print(f"📊 Populasi: {self.population_size}, Generasi: {self.generations}")
        print(f"👥 Karyawan: {self.n_karyawan} (+ {len(self.karyawan_setiap_hari)} locked)")
        
        # Inisialisasi populasi
        self.create_initial_population()
        
        # Evaluasi fitness awal
        for chrom in self.population:
            chrom.fitness = self.calculate_fitness(chrom)
            if chrom.fitness > self.best_fitness:
                self.best_fitness = chrom.fitness
                self.best_chromosome = chrom.clone()
        
        # 🔥 Reset history internal sebelum mulai evolusi
        self.history = []
        
        # Evolusi
        for generation in range(self.generations):
            new_population = []
            
            # Elitism
            new_population.append(self.best_chromosome.clone())
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.selection()
                parent2 = self.selection()
                
                child1, child2 = self.crossover(parent1, parent2)
                
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                child1.fitness = self.calculate_fitness(child1)
                child2.fitness = self.calculate_fitness(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Replace population
            self.population = new_population
            
            # Update best
            for chrom in self.population:
                if chrom.fitness > self.best_fitness:
                    self.best_fitness = chrom.fitness
                    self.best_chromosome = chrom.clone()
            
            # 🔥 Record history ke internal GA
            avg_fitness = np.mean([c.fitness for c in self.population])
            self.history.append({
                'generation': generation + 1,
                'best_fitness': self.best_fitness,
                'avg_fitness': avg_fitness
            })
            
            # Progress callback
            if callback and generation % 10 == 0:
                callback(generation + 1, self.best_fitness, avg_fitness)
            
            # Print progress
            if (generation + 1) % 50 == 0:
                print(f"Gen {generation + 1}/{self.generations} | "
                      f"Best: {self.best_fitness:.2f} | Avg: {avg_fitness:.2f}")
        
        print(f"\n✅ Selesai! Best Fitness: {self.best_fitness:.2f}")
        
        # 🔥 Return harus sejajar dengan 'for generation' (di dalam method run)
        return self.best_chromosome
    
    def get_schedule_dataframe(self, chromosome: Chromosome) -> pd.DataFrame:
        """Mengubah kromosom hasil menjadi DataFrame"""
        hari_nama = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        
        result_df = self.df_karyawan.copy()
        
        for day_idx, day_name in enumerate(hari_nama):
            status = []
            for i in range(self.n_karyawan):
                if chromosome.schedule[i, day_idx] == 1:
                    status.append("LIBUR")
                else:
                    status.append("PIKET")
            result_df[day_name] = status
        
        # Tambahkan karyawan "SETIAP HARI"
        for _, row in self.karyawan_setiap_hari.iterrows():
            new_row = row.to_dict()
            for day_name in hari_nama:
                new_row[day_name] = "PIKET (LOCKED)"
            result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        
        return result_df