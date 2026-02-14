# YouTube Political Sentiment Analysis

Aplikasi web untuk mengumpulkan dan menganalisis sentimen komentar politik dari YouTube menggunakan YouTube Data API v3 dan machine learning.

## 🌟 Fitur

- 🔍 **Pencarian Video**: Cari video politik berdasarkan kata kunci
- 💬 **Pengumpulan Komentar**: Ambil komentar dari video YouTube secara otomatis
- 📊 **Analisis Sentimen**: Analisis sentimen komentar (Positif/Netral/Negatif) menggunakan model AI untuk Bahasa Indonesia
- 📈 **Visualisasi**: Tampilan statistik dan grafik interaktif
- 💾 **Export Data**: Export hasil analisis ke CSV atau JSON
- 🎨 **UI Modern**: Interface yang menarik dengan dark mode dan animasi smooth

## 🚀 Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Langkah Instalasi

1. **Clone atau download repository ini**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Konfigurasi API Key**
   - Jika ingin menggunakan API key sendiri, edit file `.env`:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

4. **Jalankan aplikasi**
```bash
python app.py
```

5. **Buka browser**
   - Akses: `http://localhost:5000`

## 📖 Cara Penggunaan

1. **Cari Video**
   - Masukkan kata kunci politik (contoh: "pemilu 2024", "debat capres", "politik indonesia")
   - Klik "Cari Video"

2. **Pilih Video**
   - Pilih video dari hasil pencarian
   - Klik "Analisis Komentar" pada video yang dipilih

3. **Lihat Hasil**
   - Statistik sentimen ditampilkan dalam bentuk angka dan grafik
   - Scroll ke bawah untuk melihat komentar individual dengan label sentimen
   - Filter komentar berdasarkan sentimen (Semua/Positif/Netral/Negatif)

4. **Export Data**
   - Klik "Export CSV" atau "Export JSON" untuk menyimpan hasil analisis
   - File akan disimpan di folder `data/`

## ⚠️ Penting: YouTube API Quota

YouTube Data API v3 memiliki **quota limit 10,000 units per hari**:
- Search video: **100 units** per request
- Fetch comments: **1 unit** per request

**Tips menghemat quota:**
- Batasi jumlah hasil pencarian video (max_results)
- Batasi jumlah komentar yang diambil (max_comments)
- Monitor penggunaan quota di dashboard aplikasi

## 🛠️ Teknologi

- **Backend**: Flask (Python)
- **YouTube API**: Google API Client
- **Sentiment Analysis**: Transformers (IndoBERT model)
- **Frontend**: HTML, CSS, JavaScript
- **Visualisasi**: Chart.js
- **Data Storage**: CSV/JSON

## 📁 Struktur Proyek

```
ytb/
├── app.py                  # Main Flask application
├── youtube_api.py          # YouTube API integration
├── sentiment_analyzer.py   # Sentiment analysis module
├── data_handler.py         # Data persistence
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── main.js        # Frontend logic
└── data/                  # Exported data files
```

## 🔧 Troubleshooting

**Error: API quota exceeded**
- Tunggu hingga quota reset (setiap hari pada midnight Pacific Time)
- Atau gunakan API key yang berbeda

**Error: Comments disabled**
- Video tersebut menonaktifkan komentar
- Pilih video lain

**Model sentiment analysis lambat**
- Pertama kali load model akan download file (±500MB)
- Setelah download, model akan di-cache untuk penggunaan selanjutnya

## 📝 Lisensi

Project ini dibuat untuk tujuan edukasi dan penelitian.

## 🤝 Kontribusi

Silakan buat issue atau pull request untuk improvement.
