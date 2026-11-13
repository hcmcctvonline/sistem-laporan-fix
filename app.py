from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import pandas as pd
from datetime import datetime
import io

app = Flask(__name__)

# --- INISIALISASI DATABASE ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            divisi TEXT NOT NULL,
            kategori TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            tanggal TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTE 1: HALAMAN UTAMA & FILTER ---
@app.route("/")
def home():
    selected_divisi = request.args.get("divisi_filter")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if selected_divisi and selected_divisi != "Semua":
        cursor.execute("SELECT * FROM laporan WHERE divisi = ? ORDER BY id DESC", (selected_divisi,))
    else:
        cursor.execute("SELECT * FROM laporan ORDER BY id DESC")

    semua_laporan = cursor.fetchall()
    conn.close()

    return render_template("index.html", laporan_list=semua_laporan, divisi_terpilih=selected_divisi)

# --- ROUTE 2: SIMPAN LAPORAN ---
@app.route("/submit", methods=["POST"])
def submit():
    nama = request.form.get("nama")
    divisi = request.form.get("divisi")
    kategori = request.form.get("kategori")
    deskripsi = request.form.get("deskripsi")
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO laporan (nama, divisi, kategori, deskripsi, tanggal)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, divisi, kategori, deskripsi, waktu_sekarang))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

# --- ROUTE 3: UNDUH LAPORAN KE EXCEL ---
@app.route("/export")
def export_excel():
    conn = sqlite3.connect('database.db')
    
    # Ambil data dari SQLite menggunakan Pandas
    df = pd.read_sql_query("SELECT id, tanggal, nama, divisi, kategori, deskripsi FROM laporan ORDER BY id DESC", conn)
    conn.close()

    # Ubah nama header kolom di Excel agar lebih rapi
    df.columns = ['ID Laporan', 'Tanggal & Waktu', 'Nama Pengirim', 'Divisi', 'Jenis Laporan', 'Detail Deskripsi']

    # Simpan file Excel ke dalam memori
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Rekap Laporan')
    output.seek(0)

    # Kirim file sebagai unduhan (.xlsx)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"Rekap_Laporan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

if __name__ == "__main__":
    app.run(debug=True)