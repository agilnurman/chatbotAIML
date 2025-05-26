import aiml
import re
import difflib
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

kernel = aiml.Kernel()
kernel.learn("budidaya_ayam.aiml")

TOKEN = "8015063155:AAG-kgTqBWHuSYuh-0uyFNEkg3Gut5QibgM"

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Tentang Ayam Pedaging", callback_data='info_ayam')],
        [InlineKeyboardButton("Informasi Pakan", callback_data='info_pakan')],
        [InlineKeyboardButton("Kesehatan Ayam", callback_data='info_kesehatan')],
        [InlineKeyboardButton("Manajemen Kandang", callback_data='info_kandang')],
        [InlineKeyboardButton("Statistik & FCR", callback_data='info_statistik')],
        [InlineKeyboardButton("Kembali ke Menu Utama", callback_data='menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Selamat datang di Chatbot Budidaya Ayam Pedaging!\n"
        "Silakan pilih kategori informasi:",
        reply_markup=main_menu_keyboard()
    )
    context.user_data['feature'] = None

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    command = query.data

    feature_lookup = {
        'info_ayam': 'INFORMASI TENTANG AYAM PEDAGING',
        'info_pakan': 'INFORMASI TENTANG PAKAN',
        'info_kesehatan': 'INFORMASI TENTANG KESEHATAN',
        'info_kandang': 'INFORMASI TENTANG KANDANG',
        'info_statistik': 'INFORMASI TENTANG FCR',
        'menu': None  # untuk kembali menu utama
    }

    if command == 'menu' or command not in feature_lookup:
        # Reset fitur aktif
        context.user_data['feature'] = None
        query.edit_message_text("Silakan pilih kategori:", reply_markup=main_menu_keyboard())
        return


    context.user_data['feature'] = command
    reply_text = kernel.respond(feature_lookup[command])
    keyboard = main_menu_keyboard()
    query.edit_message_text(reply_text, reply_markup=keyboard)

PATTERNS = {
    # ✅ Tentang Ayam Pedaging
    "APA ITU AYAM PEDAGING": [
        "ARTI AYAM", "APA ITU AYAM ", "MAKNA AYAM", "PENGERTIAN AYAM", "DEFINISI AYAM"
    ],
    
    # ✅ Tentang Jenis Pakan
    "JENIS PAKAN UNTUK AYAM PEDAGING": [
        "JENIS PAKAN", "PAKAN UNTUK BROILER", "JENIS MAKANAN", "MAKANAN UNTUK AYAM", "PAKAN PEDAGING"
    ],

    # ✅ Tentang Kelompok/Urutan Pakan
    "KELOMPOK PAKAN AYAM": [
        "KELOMPOK PAKAN", "URUTAN PAKAN", "TAHAP PAKAN", "PAKAN AYAM BROILER"
    ],

    # ✅ Jadwal / Frekuensi Pakan
    "BERAPA KALI AYAM DIBERI MAKAN": [
        "FREKUENSI PAKAN", "JADWAL PAKAN", "SEHARI BERAPA KALI", "KAPAN AYAM MAKAN", "MAKAN BERAPA KALI", "WAKTU PAKAN"
    ],

    # ✅ Cara Memberi Makan
    "BAGAIMANA CARA MEMBERI MAKAN AYAM": [
        "CARA MEMBERI PAKAN", "MEMBERI MAKAN AYAM", "CARA PAKAN", "BAGAIMANA PEMBERIAN PAKAN", "TEKNIK MEMBERI PAKAN"
    ],

    # ✅ Informasi tentang Kesehatan Ayam
    "PERAWATAN KESEHATAN AYAM": [
        "OBAT AYAM", "PENYAKIT AYAM", "VAKSIN AYAM", "MENJAGA KESEHATAN", "PERAWATAN AYAM", "CARA MENJAGA KESEHATAN"
    ],

    # ✅ Penyakit Ayam
    "PENYAKIT UMUM PADA AYAM PEDAGING": [
        "PENYAKIT BROILER", "MASALAH KESEHATAN", "PENYAKIT UMUM", "PENYAKIT SERING TERJADI", "PENYAKIT AYAM PEDAGING"
    ],

    # ✅ Informasi tentang Kandang
    "JADWAL MEMBERSIHKAN KANDANG": [
        "CUCI KANDANG", "BERSIH KANDANG", "MEMBERSIHKAN KANDANG", "JADWAL KEBERSIHAN KANDANG"
    ],

    # ✅ Suhu kandang
    "SUHU KANDANG": [
        "TEMPERATUR KANDANG", "SUHU IDEAL", "PANAS KANDANG", "KELEMBABAN KANDANG", "KANDANG TERLALU PANAS"
    ],

    # ✅ Tentang FCR
    "APA ITU FCR": [
        "FCR", "FEED CONVERSION RATIO", "RASIO PAKAN", "RASIO KONVERSI PAKAN", "APA ITU FEED RATIO"
    ],

    # ✅ Berat Ideal Ayam
    "BERAT AYAM IDEAL": [
        "BOBOT AYAM", "BERAT AYAM", "IDEAL WEIGHT", "BERAT PANEN", "TARGET BOBOT", "BERAT YANG BAGUS"
    ],

    # ✅ Mortalitas Ayam
    "TINGKAT KEMATIAN AYAM": [
        "KEMATIAN AYAM", "TINGKAT KEMATIAN", "MORTALITY RATE", "PERSENTASE KEMATIAN", "AYAM MATI"
    ],

    # ✅ Navigasi Kembali
    "KEMBALI": [
        "MENU", "KEMBALI KE MENU", "BACK", "START", "KEMBALI KE AWAL", "HOME"
    ]
}


def normalize(text):
    text = text.upper().strip()
    text = re.sub(r'[^A-Z\s]', '', text)  # Hilangkan karakter aneh
    return text

def match_pattern(user_input):
    user_input = normalize(user_input)
    for pattern, variants in PATTERNS.items():
        all_phrases = [pattern] + variants
        match = difflib.get_close_matches(user_input, all_phrases, n=1, cutoff=0.75)
        if match:
            return pattern      
    return None


def message_handler(update: Update, context: CallbackContext) -> None:
    feature = context.user_data.get('feature')
    if not feature:
        update.message.reply_text(
            "Kamu belum memilih kategori!\n"
            "Silakan pilih kategori info dulu menggunakan tombol menu."
        )
        return

    user_input = update.message.text
    matched_pattern = find_best_match(user_input, patterns.get(feature, []))

    if matched_pattern:
        response = kernel.respond(matched_pattern)
    else:
        response = kernel.respond("Saya tidak mengerti")

    update.message.reply_text(response)


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
