import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def generate_jadwal_off_and_piket(df_jadwal):
    """
    Memformat dataframe hasil GA menjadi 2 tabel:
    1. Tabel Jadwal OFF (berisi nama yang libur, dikelompokkan per TIM)
    2. Tabel Jadwal Piket (Setiap karyawan hanya muncul 1x, dibagi seimbang)
    """
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    df = df_jadwal.copy()
    
    # Filter hanya karyawan reguler (bukan 'SETIAP HARI' / LOCKED)
    df_reguler = df[~df['Senin'].str.contains('LOCKED', na=False)].copy()
    
    # Assign TIM (A-G) secara berurutan
    tim_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    df_reguler['TIM'] = [tim_list[i % 7] for i in range(len(df_reguler))]

    # ==========================================
    # TABEL 1: JADWAL OFF (LIBUR) PER TIM
    # ==========================================
    off_matrix = pd.DataFrame(index=tim_list, columns=days).fillna('')
    
    for _, row in df_reguler.iterrows():
        for day in days:
            val = str(row[day]).strip()
            if val == 'LIBUR':
                current_val = off_matrix.loc[row['TIM'], day]
                if current_val == '':
                    off_matrix.loc[row['TIM'], day] = row['Nama']
                else:
                    off_matrix.loc[row['TIM'], day] = f"{current_val}, {row['Nama']}"

    # ==========================================
    # TABEL 2: JADWAL PIKET (BALANCED ASSIGNMENT)
    # ==========================================
    # Logika: Setiap karyawan hanya ditugaskan 1 hari piket untuk tabel ini.
    # Kita pilih hari di mana mereka PIKET, dan hari tersebut masih sedikit orangnya.
    
    piket_assignment = {day: [] for day in days}
    day_counts = {day: 0 for day in days} # Untuk melacak jumlah orang per hari
    
    for _, row in df_reguler.iterrows():
        # Cari hari-hari dimana karyawan ini benar-benar PIKET
        available_days = [day for day in days if str(row[day]).strip() == 'PIKET']
        
        if available_days:
            # Pilih hari yang paling sedikit orangnya saat ini (Greedy balancing)
            best_day = min(available_days, key=lambda d: day_counts[d])
            
            # Masukkan ke hari tersebut
            piket_assignment[best_day].append(row['Nama'])
            day_counts[best_day] += 1

    # Buat DataFrame untuk tabel piket
    max_piket_per_day = max(len(names) for names in piket_assignment.values()) if any(piket_assignment.values()) else 1
    piket_matrix = pd.DataFrame(index=range(max_piket_per_day), columns=days).fillna('')
    
    for day in days:
        # Masukkan nama-nama yang sudah dibagi seimbang
        for i, name in enumerate(piket_assignment[day]):
            piket_matrix.loc[i, day] = name
    
    return off_matrix, piket_matrix
    
def export_to_excel(df, filepath="results/schedules/jadwal_piket_jt_express.xlsx"):
    """Export jadwal ke Excel dengan formatting yang menarik"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils.dataframe import dataframe_to_rows
    import os
    
    # Pastikan folder ada
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Buat workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Jadwal Piket J&T"
    
    # Definisi warna dan style
    header_fill = PatternFill(start_color="1f4e79", end_color="1f4e79", fill_type="solid")  # Biru gelap
    header_font = Font(color="FFFFFF", bold=True, size=12)  # Putih, bold
    libur_fill = PatternFill(start_color="ffcccc", end_color="ffcccc", fill_type="solid")  # Merah muda
    piket_fill = PatternFill(start_color="ccffcc", end_color="ccffcc", fill_type="solid")  # Hijau muda
    locked_fill = PatternFill(start_color="e0e0e0", end_color="e0e0e0", fill_type="solid")  # Abu-abu
    libur_font = Font(color="FF0000", bold=True)  # Merah, bold
    piket_font = Font(color="008000")  # Hijau
    locked_font = Font(color="808080", italic=True)  # Abu-abu
    
    # Border tipis
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Tulis header
    for col_num, header in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    
    # Tulis data
    for row_num, row in enumerate(df.values, 2):
        for col_num, value in enumerate(row, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
            
            # Apply formatting berdasarkan nilai
            if value == 'LIBUR':
                cell.fill = libur_fill
                cell.font = libur_font
            elif value == 'PIKET':
                cell.fill = piket_fill
                cell.font = piket_font
            elif 'LOCKED' in str(value):
                cell.fill = locked_fill
                cell.font = locked_font
    
    # Auto-width columns
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    # Simpan file
    wb.save(filepath)
    return filepath

def save_to_csv(df, filepath="data/raw/dataset.csv"):
    """Menyimpan DataFrame ke file CSV secara permanen"""
    try:
        # Pastikan folder ada
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan file: {str(e)}")
        return False

# --- KONFIGURASI PATH AGAR IMPORT BERHASIL ---
# Menambahkan root folder ke sys.path agar bisa mengimport modul dari folder src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing.matrix_builder import MatrixBuilder
from src.genetic_algorithm.genetic_engine import GeneticAlgorithm

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Automatic Scheduling J&T Express",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INISIALISASI SESSION STATE ---
if "df_karyawan" not in st.session_state:
    st.session_state.df_karyawan = pd.DataFrame()
if "hasil_jadwal" not in st.session_state:
    st.session_state.hasil_jadwal = None
if "ga_history" not in st.session_state:
    st.session_state.ga_history = []
if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

# --- FUNGSI LOAD DATA AWAL ---
@st.cache_data
def load_data_csv():
    # Path sesuai struktur folder yang kita buat
    path = "data/raw/dataset.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# --- SIDEBAR (PARAMETER ALGORITMA) ---
st.sidebar.title("️ Parameter Algoritma Genetika")
st.sidebar.markdown("---")

pop_size = st.sidebar.slider("Ukuran Populasi", 50, 300, 100, 10)
generations = st.sidebar.slider("Jumlah Generasi", 100, 1000, 500, 50)
mutation_rate = st.sidebar.slider("Mutation Rate", 0.01, 0.5, 0.1, 0.01)
min_piket = st.sidebar.number_input("Min. Karyawan Piket/Hari", 1, 20, 5)
st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Batasan Frekuensi Piket")
piket_per_minggu = st.sidebar.slider("Min. Piket per Minggu", 1, 3, 1)
piket_per_bulan = st.sidebar.slider("Target Piket per Bulan", 3, 6, 4)

st.sidebar.info(f"💡 Setiap karyawan harus piket minimal **{piket_per_minggu}x/minggu** dan target **{piket_per_bulan}x/bulan**")

st.sidebar.markdown("---")
st.sidebar.info(" **J&T Express GSK08**\nSistem Penjadwalan Otomatis\nBerbasis Algoritma Genetika")

# --- MAIN APP ---
st.title("🚚 Sistem Automatic Scheduling J&T Express")
st.caption("Perancangan Sistem Automatic Scheduling untuk Penjadwalan Shift Piket Karyawan Menggunakan Metode Algoritma Genetika")

# Membuat Tabs untuk memisahkan fungsi
tab1, tab2, tab3 = st.tabs([" 1. Data Master (CRUD)", "🧬 2. Generate Jadwal", " 3. Hasil & Analisis"])

# ==========================================
# TAB 1: DATA MASTER (CRUD)
# ==========================================
with tab1:
    st.header("Manajemen Data Karyawan")
    
    # 🔥 PERBAIKAN 1: Gunakan Absolute Path
    CSV_PATH = os.path.abspath("data/raw/dataset.csv")
    
    # Load data dari CSV jika session state masih kosong
    if st.session_state.df_karyawan.empty:
        if os.path.exists(CSV_PATH):
            raw_df = pd.read_csv(CSV_PATH)
            st.session_state.df_karyawan = raw_df
            st.success(f"✅ Berhasil memuat {len(raw_df)} data karyawan.")
        else:
            st.warning("⚠️ File dataset.csv tidak ditemukan. Silakan input manual.")
            st.session_state.df_karyawan = pd.DataFrame(columns=["Kode Karyawan", "Nama", "Req Libur"])

    st.write("### 📝 Edit Data Karyawan")
    st.info("💡 **PENTING UNTUK PENGGUNA HP:** Setelah mengedit sel, **ketuk area kosong di luar tabel** terlebih dahulu untuk menutup keyboard, baru kemudian klik tombol Simpan.")

    edited_df = st.data_editor(
        st.session_state.df_karyawan,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Kode Karyawan": st.column_config.TextColumn("Kode", width="small"),
            "Nama": st.column_config.TextColumn("Nama Karyawan", width="medium"),
            "Req Libur": st.column_config.SelectboxColumn(
                "Permintaan Libur",
                width="small",
                options=["Bebas", "SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU", "SETIAP HARI"],
                required=True
            )
        },
        hide_index=True,
        key="crud_editor"
    )

    # 🔥 PERBAIKAN 2: Alert Perubahan Data (Unsaved Changes)
    df_asli = st.session_state.df_karyawan.reset_index(drop=True).fillna("__NAN__")
    df_edit = edited_df.reset_index(drop=True).fillna("__NAN__")
    
    if not df_asli.equals(df_edit):
        st.warning("⚠️ **Anda memiliki perubahan yang belum disimpan!** Jangan lupa klik tombol **💾 Simpan Permanen** di bawah agar data tidak hilang saat halaman di-refresh.", icon="🚨")

    # Statistik
    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.metric("Total Karyawan", len(edited_df))
    with col_stats2:
        n_spesifik = len(edited_df[edited_df['Req Libur'] != 'Bebas'])
        st.metric("Req Spesifik", n_spesifik)

    st.markdown("---")
    
    # Tombol-tombol aksi
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Simpan Permanen", type="primary", width="stretch"):
            st.session_state.df_karyawan = edited_df
            try:
                os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
                edited_df.to_csv(CSV_PATH, index=False)
                
                st.toast("✅ Data berhasil disimpan permanen!", icon="💾")
                # 🔥 PERBAIKAN 3: Set flag untuk balon, lalu rerun
                st.session_state.show_balloons = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal menyimpan: {str(e)}")
    
    with col2:
        if st.button("🔄 Reset ke Awal", width="stretch"):
            if os.path.exists(CSV_PATH):
                st.session_state.df_karyawan = pd.read_csv(CSV_PATH)
                st.rerun()

    # Tampilkan balon jika flag aktif (setelah rerun)
    if st.session_state.get("show_balloons", False):
        st.balloons()
        st.session_state.show_balloons = False

# ==========================================
# TAB 2: GENERATE JADWAL
# ==========================================
with tab2:
    st.header("Eksekusi Algoritma Genetika")
    
    if st.session_state.df_karyawan.empty:
        st.warning("⚠️ Data karyawan masih kosong. Silakan isi atau load data di Tab 1 terlebih dahulu.")
    else:
        st.write(f"Total Data Karyawan Aktif: **{len(st.session_state.df_karyawan)}**")
        
        # Preview Data yang akan diproses
        with st.expander("Lihat Data yang akan diproses"):
            st.dataframe(st.session_state.df_karyawan, width="stretch")

        st.markdown("---")
        st.write("### Konfigurasi Saat Ini")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Populasi", pop_size)
        c2.metric("Generasi", generations)
        c3.metric("Mutation Rate", f"{mutation_rate*100}%")
        c4.metric("Min Piket/Hari", min_piket)

        if st.button("🚀 MULAI GENERATE JADWAL", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 🔥 PERBAIKAN DI SINI: Reset history menjadi List kosong sebelum GA mulai
            st.session_state.ga_history = [] 
            
            try:
                # 1. PREPROCESSING
                status_text.text("⏳ Tahap 1: Preprocessing Data...")
                builder = MatrixBuilder(st.session_state.df_karyawan)
                df_ga, bobot_matrix, df_locked = builder.build_preference_matrix()
                
                # 2. INISIALISASI GA
                status_text.text("🧬 Tahap 2: Inisialisasi Algoritma Genetika...")
                ga = GeneticAlgorithm(
                    df_karyawan=df_ga,
                    bobot_matrix=bobot_matrix,
                    karyawan_setiap_hari=df_locked,
                    population_size=pop_size,
                    generations=generations,
                    mutation_rate=mutation_rate,
                    min_piket_per_hari=min_piket,
                    piket_per_minggu=piket_per_minggu, 
                    piket_per_bulan=piket_per_bulan 
                )

                # 3. RUNNING GA
                status_text.text("🧬 Tahap 3: Evolusi Generasi Berlangsung...")
                
                def update_progress(gen, best_fit, avg_fit):
                    progress = gen / generations
                    progress_bar.progress(progress)
                    status_text.text(f"🧬 Generasi {gen}/{generations} | Best Fitness: {best_fit:.2f} | Avg: {avg_fit:.2f}")
                    
                    # Simpan history untuk grafik (karena ga_history sudah di-reset jadi List, .append() akan aman)
                    if gen % 5 == 0: 
                        st.session_state.ga_history.append({'Gen': gen, 'Best': best_fit, 'Avg': avg_fit})

                best_chromosome = ga.run(callback=update_progress)
                
                # 4. SELESAI - Pindahkan history dari GA ke session state
                progress_bar.progress(1.0)
                status_text.text("✅ Algoritma Selesai! Menyiapkan hasil...")

                # Simpan hasil jadwal (INDENTASI SUDAH DIPERBAIKI)
                st.session_state.hasil_jadwal = ga.get_schedule_dataframe(best_chromosome)

                # 🔥 PENTING: Pindahkan history dari GA object ke session state
                if ga.history:
                    st.session_state.ga_history = pd.DataFrame(ga.history)
                    # Rename kolom agar sesuai dengan yang diharapkan di Tab 3
                    st.session_state.ga_history = st.session_state.ga_history.rename(columns={
                        'generation': 'Gen',
                        'best_fitness': 'Best',
                        'avg_fitness': 'Avg'
                    })
                else:
                    st.session_state.ga_history = pd.DataFrame()

                st.success(f"Jadwal berhasil digenerate! Fitness Score Terbaik: **{best_chromosome.fitness:.2f}**")
                st.rerun()

            except Exception as e:
                st.error(f"Terjadi kesalahan saat menjalankan algoritma: {str(e)}")
                import traceback
                st.code(traceback.format_exc()) # Menampilkan detail error jika ada

# ==========================================
# TAB 3: HASIL & ANALISIS
# ==========================================
with tab3:
    st.header("Hasil Penjadwalan")
    
    # CEK APAKAH JADWAL SUDAH ADA DI SESSION STATE
    if st.session_state.hasil_jadwal is None:
        st.info("🕒 Belum ada jadwal yang digenerate. Silakan jalankan algoritma di Tab 2 terlebih dahulu.")
    
    else:
        # ==========================================
        # 1. TABEL HASIL
        # ==========================================
        st.subheader("📅 Tabel Jadwal Mingguan")
        st.info("Keterangan: **LIBUR** (Merah), **PIKET** (Hijau), **PIKET (LOCKED)** (Abu-abu)")
        
        def highlight_schedule(val):
            if val == 'LIBUR':
                return 'background-color: #ffcccc; color: red; font-weight: bold;'
            elif val == 'PIKET':
                return 'background-color: #ccffcc; color: green;'
            elif 'LOCKED' in str(val):
                return 'background-color: #e0e0e0; color: gray;'
            return ''

        styled_df = st.session_state.hasil_jadwal.style.map(
            highlight_schedule, 
            subset=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        )
        
        st.dataframe(styled_df, width="stretch", height=600)

                # ==========================================
        # 🔥 FORMAT TABEL SEPERTI EXCEL (JADWAL OFF & PIKET)
        # ==========================================
        st.markdown("---")
        
        # Panggil fungsi yang baru
        df_off, df_piket = generate_jadwal_off_and_piket(st.session_state.hasil_jadwal)

        # --- TABEL 1: JADWAL OFF ---
        st.subheader(" JADWAL OFF (LIBUR) PER TIM")
        st.info("Sel berwarna merah menunjukkan karyawan yang LIBUR pada hari tersebut.")
        
        # Styling untuk Tabel OFF
        def highlight_off(val):
            if val != '':
                return 'background-color: #ffcccc; color: red; font-weight: bold;'
            return ''
            
        styled_off = df_off.style.map(highlight_off)
        st.dataframe(styled_off, width="stretch", height=300)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- TABEL 2: JADWAL PIKET ---
        st.subheader(" PIKET JAM 04.30 & 17.45")
        st.info("Setiap karyawan piket **1 kali seminggu** (4x sebulan). Nama yang tertera adalah karyawan yang bertugas piket pada hari tersebut.")
        
        # Styling untuk Tabel Piket (Abu-abu seperti Excel)
        def highlight_piket(val):
            if val != '':
                return 'background-color: #d9d9d9; color: black; font-weight: bold;'
            return ''
            
        styled_piket = df_piket.style.map(highlight_piket)
        st.dataframe(styled_piket, width="stretch", height=400)
        
        # Download button untuk format ini
        st.download_button(
            label="📥 Download Format Excel (CSV)",
            data=df_piket.to_csv(index=False).encode('utf-8'),
            file_name='jadwal_piket_jt_express.csv',
            mime='text/csv',
            width="stretch"
        )

        # ==========================================
        # 2. STATISTIK DISTRIBUSI PIKET
        # ==========================================
        st.subheader("📊 Statistik Distribusi Piket")
        hari_list = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        stats = []
        for hari in hari_list:
            n_piket = len(st.session_state.hasil_jadwal[st.session_state.hasil_jadwal[hari].str.contains('PIKET')])
            stats.append({'Hari': hari, 'Jumlah Piket': n_piket})
        
        stats_df = pd.DataFrame(stats)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ['#2ecc71' if x >= min_piket else '#e74c3c' for x in stats_df['Jumlah Piket']]
        ax.bar(stats_df['Hari'], stats_df['Jumlah Piket'], color=colors)
        ax.axhline(y=min_piket, color='blue', linestyle='--', label=f'Minimum Required ({min_piket})')
        ax.set_title('Jumlah Karyawan Piket per Hari')
        ax.set_ylabel('Jumlah Karyawan')
        ax.legend()
        st.pyplot(fig)

        # ==========================================
        # 3. GRAFIK KONVERGENSI FITNESS
        # ==========================================
        st.subheader("📈 Grafik Konvergensi Fitness")
        if not st.session_state.ga_history.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.plot(st.session_state.ga_history['Gen'], st.session_state.ga_history['Best'], label='Best Fitness', color='blue', linewidth=2)
            ax2.plot(st.session_state.ga_history['Gen'], st.session_state.ga_history['Avg'], label='Average Fitness', color='orange', alpha=0.7, linestyle='--')
            ax2.set_title('Konvergensi Algoritma Genetika')
            ax2.set_xlabel('Generasi')
            ax2.set_ylabel('Fitness Score')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)
        else:
            st.warning("Data history konvergensi tidak tersedia.")

        # ==========================================
        # 4. EKSPOR DATA (HANYA MUNCUL JIKA HASIL ADA)
        # ==========================================
        st.subheader("📥 Ekspor Data")
        st.markdown("Download hasil penjadwalan untuk laporan atau arsip.")
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # Tombol Download CSV
            # Kita buat variabel csv di dalam blok else ini agar aman dari error NoneType
            export_df = st.session_state.hasil_jadwal.copy()
            csv = export_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="⬇️ Download Hasil (CSV)",
                data=csv,
                file_name='jadwal_piket_jt_express.csv',
                mime='text/csv',
                width="stretch"
            )
            
        with col_dl2:
            # Tombol Download Excel (Jika fungsi export_to_excel sudah dibuat)
            try:
                # Panggil fungsi export excel yang sudah kita buat sebelumnya
                # Pastikan filepath sesuai atau biarkan default
                filepath = "results/schedules/jadwal_piket_jt_express.xlsx"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                export_to_excel(export_df, filepath)
                
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Hasil (Excel .xlsx)",
                        data=f,
                        file_name='jadwal_piket_jt_express.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        width="stretch"
                    )
            except Exception as e:
                st.error(f"Fitur Excel belum siap atau error: {e}")