"""English label layer.

Codebook labels are in Indonesian. `translate()` maps each cleaned attribute label
to a concise English version; anything not in the map falls back to the source text.
Categorical value maps (gender, age, tenure, …) live here too.
"""

# ---------------------------------------------------------------------------
# Touchpoint domains -> codebook group prefix
# ---------------------------------------------------------------------------
# Paired groups (have a '- kompetitor' counterpart) usable for XYZ-vs-competitor.
DOMAINS_PAIRED = {
    "Brand Image": "T_C1B",
    "Branch Facility": "T_KC2",
    "Security": "T_SC2",
    "Teller": "T_TL3",
    "Customer Service": "T_CS3",
    "ATM": "T_AT3",
    "Loyalty Drivers": "T_H1A",
}

# Touchpoints for the drill-down page. `paired` flags whether a competitor exists.
TOUCHPOINTS = {
    "Security": {"prefix": "T_SC2", "paired": True},
    "Teller": {"prefix": "T_TL3", "paired": True},
    "Customer Service": {"prefix": "T_CS3", "paired": True},
    "Customer Advisor": {"prefix": "T_CA1", "paired": False},
    "ATM": {"prefix": "T_AT3", "paired": True},
    "Electronic Facilities": {"prefix": "T_SL1", "paired": False},
}

# ---------------------------------------------------------------------------
# Categorical value maps
# ---------------------------------------------------------------------------
GENDER_MAP = {"Pria": "Male", "Laki-laki": "Male", "Wanita": "Female", "Perempuan": "Female"}

MARITAL_MAP = {"Menikah": "Married", "Belum menikah": "Single", "Duda / Janda": "Widowed / Divorced"}

TENURE_MAP = {
    "1 bulan s/d 3 bulan": "1–3 months",
    "3 bulan s/d 11 bulan": "3–11 months",
    "1 tahun s/d 2 tahun 11 bulan": "1–2 years",
    "3 tahun s/d 4 tahun 11 bulan": "3–4 years",
    "5 tahun atau lebih": "≥ 5 years",
}
TENURE_ORDER = ["1–3 months", "3–11 months", "1–2 years", "3–4 years", "≥ 5 years"]

FREQUENCY_MAP = {
    "1 minggu 2 kali atau lebih": "≥ 2× a week",
    "1 minggu sekali": "Once a week",
    "2 minggu sekali": "Once every 2 weeks",
    "1 bulan sekali": "Once a month",
}
FREQUENCY_ORDER = ["≥ 2× a week", "Once a week", "Once every 2 weeks", "Once a month"]

OCCUPATION_MAP = {
    "Pegawai/Karyawan Swasta": "Private Employee",
    "Wiraswasta/Pengusaha/Pedagang": "Entrepreneur / Trader",
    "Pegawai Negeri Sipil (Bukan Guru)": "Civil Servant (Non-Teacher)",
    "Pegawai Negeri Sipil (Guru)": "Civil Servant (Teacher)",
    "Ibu Rumah Tangga": "Homemaker",
    "Tenaga Honorer": "Contract Worker",
    "Mahasiswa/i": "Student",
    "Guru (Non PNS)": "Teacher (Non-Civil Servant)",
    "Perangkat Desa (Camat/Lurah/RW)": "Village Official",
    "Polisi / Tentara / Militer": "Police / Military",
    "Pensiunan": "Retiree",
    "Sedang Tidak Bekerja": "Unemployed",
    "Pengacara/Advokat/Notaris": "Lawyer / Notary",
    "Dokter": "Doctor",
    "Lainnya": "Other",
}

EDUCATION_MAP = {
    "SD": "Primary",
    "SLTP/SMP": "Junior High",
    "SLTA/SMA/SMK": "Senior High",
    "Diploma (D1/D2/D3)": "Diploma",
    "S1/D4": "Bachelor",
    "S2": "Master",
    "S3": "Doctorate",
}


def clean_age(value):
    v = str(value)
    v = v.replace(" tahun ke atas", "+")
    v = v.replace(" tahun dan ke atas", "+")
    v = v.replace(" tahun", "")
    return v.replace(" ", "")


# Banknote/income brackets keep the rupiah figures; we just strip the code prefix.
def clean_bracket(value):
    v = str(value)
    if " : " in v:
        v = v.split(" : ", 1)[1]
    return v.replace("Rp.", "Rp").strip()


# ---------------------------------------------------------------------------
# Attribute translation map (cleaned Indonesian label -> concise English)
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    # --- Brand image (T_C1A / T_C1B) ---
    "Bank yang terkenal/terkemuka": "Well-known / prominent bank",
    "Bank yang digunakan banyak orang": "Used by many people",
    "Bank yang membuat saya merasa aman": "Makes me feel safe",
    "Bank yang membuat saya merasa dihargai menjadi nasabah bank ini": "Makes me feel valued",
    "Bank yang memiliki banyak ATM": "Has many ATMs",
    "Bank yang memiliki banyak kantor cabang": "Has many branches",
    "Bank yang memiliki reputasi yang baik": "Has a good reputation",
    "Bank yang menawarkan produk/layanan yang lengkap": "Complete products / services",
    "Menyediakan layanan online terkait dengan informasi produk": "Online product information",
    "Menyediakan banyak channel (call center, sms, email, dsb) untuk nasabah menyampaikan keluhan/saran": "Many feedback channels",
    "Bank yang menguntungkan untuk investasi/pengembangan kekayaan/uang saya": "Good for investment",
    "Bank yang membuat saya merasa bangga karena produk/layanan/promo yang tidak saya dapatkan dari bank lain": "Makes me feel proud (exclusive offers)",
    "Bank yang membuat saya merasa percaya diri dan dapat mengontrol penuh kebutuhan transaksi perbankan saya": "Confident & in control",
    "Bank yang membuat saya merasa prestigious/bergengsi": "Makes me feel prestigious",
    "Bank yang memberikan kemudahan untuk bertransaksi dimanapun dan kapanpun": "Easy to transact anytime, anywhere",
    "Bank yang mempermudah bisnis saya": "Makes my business easier",
    "Bank yang memberikan banyak kemudahan": "Provides many conveniences",
    "Bank yang memiliki kinerja bisnis yang baik": "Strong business performance",
    "Bank yang selalu menggunakan teknologi terbaru": "Uses the latest technology",
    "Bank yang dimiliki oleh negara": "State-owned bank",
    "Bank swasta terbesar di Indonesia": "Largest private bank",
    "Memberikan keuntungan saat digunakan untuk bertransaksi (diskon, cashback, point rewards)": "Transaction rewards (cashback, points)",
    "Memiliki fitur transaksi di e-channel lengkap (ATM, mobile banking, internet banking) lengkap": "Complete e-channel features",
    "Bank dengan segala produk dan fasilitas yang membuat saya merasa cukup dengan menjadi nasabah satu bank saja": "One-stop bank for all needs",

    # --- Emotions (T_I1A) ---
    "Saya merasa Bahagia pada saat menggunakan layanan cabang": "Happy",
    "Saya Percaya dengan layanan cabang": "Trusting",
    "Saya merasa Dihargai sebagai nasabah oleh cabang": "Valued",
    "Saya merasa Diperhatikan sebagai nasabah oleh cabang": "Cared for",
    "Saya merasa Aman pada saat menggunakan layanan cabang": "Safe",
    "Saya merasa Fokus pada saat menggunakan layanan cabang": "Focused",
    "Layanan cabang Memanjakan Saya sebagai nasabah": "Pampered",
    "Saya merasa Tertarik dengan layanan cabang": "Interested",
    "Layanan yang diberikan cabang membuat saya merasa Penuh Semangat": "Energized",
    "Saya merasa Tidak Puas dengan layanan yang diberikan cabang": "Dissatisfied",
    "Saya merasa Frustasi pada saat menggunakan layanan cabang": "Frustrated",
    "Saya merasa Kecewa dengan layanan cabang": "Disappointed",
    "Saya merasa Tertekan dengan layanan yang diberikan cabang": "Stressed",
    "Saya merasa Tidak Bahagia dengan layanan yang diberikan cabang": "Unhappy",
    "Saya merasa Diabaikan pada saat menggunakan layanan cabang": "Ignored",
    "Saya merasa Tergesa-gesa pada saat menggunakan layanan cabang": "Rushed",

    # --- Loyalty drivers (T_H1A) ---
    "Memberikan saya kemudahan untuk bertransaksi dimana pun dan kapan pun": "Easy to transact anytime, anywhere",
    "Bank yang memudahkan saya untuk bertransaksi karena digunakan oleh banyak orang": "Easy because widely used",
    "Bank yang memberikan promo sesuai dengan gaya hidup saya": "Promos that fit my lifestyle",
    "Memberikan saya kecepatan bertransaksi (real time ke semua bank dan pembayaran)": "Fast real-time transactions",
    "Saya merasa aman menyimpan uang dan bertransaksi di bank ini": "Safe to save & transact",
    "Saya bangga menjadi nasabah bank ini dengan produk/layanan/promo yang berbeda yang tidak saya dapatkan dari bank lain": "Proud of exclusive offers",
    "Bank yang membuat saya merasa up to date/keren/modern": "Makes me feel modern",
    "Bank turun-temurun yang membantu keluarga saya dan mengajarkan saya menabung pertama kali": "Family heritage bank",
    "Bank ini membuat saya merasa prestigius/bergengsi": "Makes me feel prestigious",

    # --- Security (T_SC2) ---
    "Penampilannya rapi": "Neat appearance",
    "Menggunakan seragam sekuriti yang lengkap": "Wears complete uniform",
    "Menyambut nasabah dengan ramah": "Greets customers warmly",
    "Berperilaku sopan": "Polite behaviour",
    "Mengucapkan salam saat nasabah datang/pulang": "Greets on arrival / departure",
    "Menawarkan bantuan saat nasabah datang": "Offers help on arrival",
    "Mengarahkan nasabah dan mengkonfirmasi kelengkapan dokumen yang diperlukan untuk bertransaksi": "Guides & checks documents",
    "Memiliki pengetahuan yang memadai untuk menjawab pertanyaan dari nasabah": "Knowledgeable in answering questions",
    "Memberikan nomor antrian kepada nasabah": "Hands out queue numbers",
    "Mengatur antrian nasabah": "Manages the queue",
    "Mengucapkan terima kasih saat nasabah pulang": "Thanks customers on departure",
    "Jumlah sekuriti memadai": "Adequate security staff",
    "Keberadaan Satpam Luar Banking Hall yang siap dan siaga (N/A untuk KCP)": "Outdoor security on standby",
    "Keberadaan Satpam Dalam Banking Hall yang siap dan siaga": "Indoor security on standby",

    # --- Teller (T_TL3) ---
    "Waktu antrian di Teller cepat": "Short teller queue time",
    "Sistem antrian yang dilengkapi dengan nomor antrian": "Queue system with numbers",
    "Layanan yang diberikan teller cepat": "Fast teller service",
    "Jumlah teller di kantor cabang mencukupi pada saat jam sibuk (meja teller tidak ada yang kosong)": "Enough tellers at peak hours",
    "Tellernya berpenampilan rapi dan menarik": "Neat & presentable teller",
    "Akurat dalam melakukan transaksi (Tidak salah dalam melakukan transaksi)": "Accurate transactions",
    "Kehandalan sistem komputer untuk Teller (online)": "Reliable teller system",
    "Teller memiliki pengetahuan yang memadai": "Knowledgeable teller",
    "Tellernya ramah selama melayani (tersenyum dan tidak jutek selama melayani)": "Friendly teller",
    "Tellernya mengucapkan salam saat menyambut dan mengakhiri layanan": "Greets at start & end",
    "Tellernya tidak mengobrol dengan rekannya / petugas bank lain": "Does not chat with colleagues",
    "Menunjukkan keinginan untuk membantu nasabah (selalu menanyakan apalagi yang bisa dibantu)": "Shows willingness to help",
    "Teller memperkenalkan diri/menyebut namanya saat menyambut nasabah": "Introduces themselves by name",
    "Memberikan pelayanan dengan pendekatan personal (menyebut nama nasabah)": "Personal approach (uses your name)",
    "Tellernya selalu melakukan validas setelah selesai transaksi di Teller": "Always validates after transaction",
    "Memberikan usaha lebih/extra effort untuk nasabahnya (membantu mengecek pengisian slip setoran/penarikan/pembayaran/verifikasi/konfirmasi data nasabah)": "Goes the extra mile",
    "Terdapat papan nama Teller di area meja kerja Teller": "Teller name plate on desk",
    "Terdapat informasi/signage transaksi di meja kerja teller": "Transaction signage on desk",

    # --- Customer Service (T_CS3) ---
    "CS ramah selama melayani (tersenyum dan tidak jutek selama melayani)": "Friendly CS",
    "Jumlah Customer Service yang melayani cukup pada saat jam sibuk (meja CS tidak ada yang kosong)": "Enough CS at peak hours",
    "Mengetahui pengetahuan yang baik tentang produk perbankan": "Good product knowledge",
    "Memberikan solusi yang tepat terhadap permasalahan nasabah": "Provides the right solutions",
    "Cepat dalam memberikan layanan": "Fast service",
    "Teliti dalam memberikan layanan": "Thorough service",
    "Waktu antrian di CS cepat": "Short CS queue time",
    "CS memiliki kehandalan sistem komputer di meja CS (online)": "Reliable CS system",
    "CS memiliki pengetahuan dalam menjawab pertanyaan nasabah atau pengetahuan CS ketika menjelaskan produk kepada nasabah": "Knowledgeable explaining products",
    "CS memiliki pemahaman terhadap permintaan/permasalahan nasabah": "Understands customer needs",
    "CS menjelaskan proses pembukaan rekening baru dengan e-form (formulir elektronik) dengan baik": "Explains e-form account opening",
    "Memberikan informasi yang lengkap dan akurat": "Complete & accurate information",
    "Tidak mengobrol dengan rekan kerja": "Does not chat with colleagues",
    "CS berpenampilan rapi dan menarik": "Neat & presentable CS",
    "Menunjukkan keinginan untuk membantu nasabah": "Shows willingness to help",
    "CSnya mengucapkan salam saat menyambut dan mengakhiri layanan": "Greets at start & end",
    "CSnya mengucapkan terima kasih saat mengakhiri layanan": "Thanks customer at end",
    "CSnya menawarkan bantuan lain ketika akan mengakhiri layanan": "Offers further help at end",
    "Terdapat papan nama CS di area meja kerja CS": "CS name plate on desk",
    "Terdapat informasi/signage terkait status transaksi CS": "Transaction status signage",

    # --- ATM (T_AT3) ---
    "Mesin ATMnya mudah ditemui dimana-mana": "ATMs easy to find",
    "Antrian di mesin ATM tidak panjang": "Short ATM queues",
    "Saya merasa aman ketika bertransaksi menggunakan ATM karena dilengkapi dengan CCTV/ada sekuriti": "Feels safe (CCTV / security)",
    "Mesin ATMnya berada di lokasi yang aman (bukan di tempat yang sepi)": "ATMs in safe locations",
    "Menyediakan ATM dengan berbagai pilihan pecahan nominal (Rp 50.000/Rp 100.000)": "Various banknote denominations",
    "Kartu ATMnya dapat digunakan untuk bertransaksi dan berbelanja": "Card works for transactions & shopping",
    "Selalu meminta PIN setiap kali berganti transaksi untuk menjamin keamanan": "Always asks PIN for security",
    "Kartu ATMnya bisa digunakan di ATM BERSAMA dan jaringan ATM lainnya": "Works on shared ATM networks",
    "Memiliki alarm yang mengingatkan jika kartu ATM belum diambil dari mesin ATM": "Alarm for un-collected card",
    "Disediakan nomor call center di mesin ATM yang bisa dihubungi": "Call center number on ATM",
    "Tersedia tempat sampah di bilik ATM": "Trash bin in ATM booth",
    "Terdapat tutup pengaman di atas tombol/keypad untuk menjaga kerahasiaan nasabah saat memasukkan PIN": "PIN keypad privacy cover",
    "Tersedia informasi untuk lokasi ATM terdekat": "Nearest ATM location info",
    "Memiliki persediaan uang yang cukup": "Sufficient cash supply",

    # --- Branch facility (T_KC2) ---
    "Kantor cabangnya banyak (dekat dengan tempat tinggal dan atau tempat kerja saya)": "Many nearby branches",
    "Menyediakan layanan weekend banking": "Weekend banking available",
    "Tersedia area parkir (khusus untuk cabang di gedung sendiri/ruko dan cabang yang menghadap ke tempat parkir)": "Parking area available",
    "Ada petugas Sekuriti yang mengatur di area parkir (khusus untuk cabang di gedung sendiri/ruko dan cabang yang menghadap ke tempat parkir)": "Security manages parking",
    "Kebersihan di area parkir": "Clean parking area",
    "Kebersihan pada area masuk cabang": "Clean entrance area",
    "Tersedia tempat duduk yang cukup di ruang tunggu": "Enough seating",
    "Pendingin ruangan di ruang tunggu sejuk": "Cool air-conditioning",
    "Ruang tunggu nyaman": "Comfortable waiting area",
    "Disediakan Wifi gratis di ruang tunggu": "Free WiFi",
    "Tersedia TV di ruang tunggu": "TV in waiting area",
    "Area ruang tunggunya wangi": "Pleasant-smelling waiting area",
    "Diputarkan lagu lembut yang mengalun di area banking hall": "Soft background music",
    "Banking hall/area ruang tunggunya bersih": "Clean banking hall",
    "Terdapat tempat sampah dan mudah ditemukan": "Trash bins easy to find",
    "Tata letak di kantor cabang mudah untuk diikuti dan mudah untuk menemukan sesuatu yang dibutuhkan": "Easy-to-follow layout",
    "Terdapat tanaman hidup": "Live plants",
    "Tersedianya ruang laktasi": "Lactation room",
    "Kemudahan mengisi data-data pembukaan rekening baru pada e-form (formulir elektronik)": "Easy e-form account opening",
    "Terdapat petunjuk arah ke toilet": "Restroom directions",
    "Terdapat toilet di cabang": "Restroom available",
    "Toilet bersih": "Clean restroom",
    "Toilet selalu harum dan tidak bau": "Fresh-smelling restroom",
    "Tersedia wastafel di area toilet": "Sink in restroom",
    "Selalu tersedia tisu di toilet": "Tissue always available",
    "Selalu tersedia sabun pencuci tangan di toilet": "Hand soap available",
    "Air selalu mengalir dengan lancar di semua keran yang ada di toilet": "Water runs smoothly",
    "Toilet selalu berfungsi dengan baik": "Restroom works well",
    "Terdapat tempat sampah di toilet dan mudah ditemukan": "Trash bin in restroom",
    "Tempat sampah tidak penuh": "Trash not overflowing",

    # --- Customer Advisor (T_CA1) ---
    "CA ramah selama melayani (tersenyum dan tidak jutek selama melayani)": "Friendly advisor",
    "CA selalu standby ketika dibutuhkan": "Always on standby",
    "Waktu layanan oleh CA cepat": "Fast advisor service",
    "Dapat menangani berbagai macam masalah sesuai kebutuhan": "Handles a range of issues",
    "CA memiliki keandalan sistem komputer/Laptop yang di gunakan (online)": "Reliable advisor system",
    "CA memiliki pengetahuan dalam menjawab pertanyaan nasabah atau pengetahuan CA ketika menjelaskan produk kepada nasabah": "Knowledgeable explaining products",
    "CA memiliki pemahaman terhadap permintaan/permasalahan nasabah": "Understands customer needs",
    "CA berpenampilan rapi dan menarik": "Neat & presentable advisor",
    "CA mengucapkan salam saat menyambut dan mengakhiri layanan": "Greets at start & end",
    "CA mengucapkan terima kasih saat mengakhiri layanan": "Thanks customer at end",
    "Menginformasikan produk, promo, dan kebijakan terbaru kepada nasabah dengan cara yang baik (disesuaikan dengan ketersediaan waktu nasabah)": "Informs about latest products / promos",
    "CA menawarkan bantuan lain ketika akan mengakhiri layanan": "Offers further help at end",

    # --- Electronic facilities (T_SL1) ---
    "Terdapat Smart Tab pada kantor cabang": "Smart Tab available",
    "CA menggunakan Smart Tab ketika menjelaskan kepada nasabah": "Advisor uses Smart Tab",
    "Terdapat XYZ Santer pada kantor cabang": "XYZ Santer available",
    "XYZ Santer dapat berfungsi dengan baik": "XYZ Santer works well",
    "Terdapat Digital Signage pada kantor cabang": "Digital Signage available",
    "Digital Signage dapat berfungsi dengan baik": "Digital Signage works well",
    "Terdapat Smart Table pada kantor cabang": "Smart Table available",
    "Smart Table dapat berfungsi dengan baik": "Smart Table works well",
    "Terdapat Pinpad pada area kerja CS": "Pinpad at CS desk",
    "Pinpad dapat berfungsi dengan baik": "Pinpad works well",
    "Terdapat Pinpad pada area kerja Teller": "Pinpad at teller desk",
    "Terdapat mesin CRM pada kantor cabang (CRM adalah mesin ATM yang memiliki fungsi ATM Tarikan Tunai, ATM Non Tunai, dan ATM Setoran Tunai)": "CRM machine available",
    "Mesin CRM dapat berfungsi dengan baik": "CRM machine works well",
    "Terdapat mesin TCR pada kantor cabang (TCR adalah mesin setor tunai di mana nasabah dapat melakukan setoran tunai secara mandiri di area toonbank teller)": "TCR machine available",
    "Mesin TCR dapat berfungsi dengan baik": "TCR machine works well",

    # --- Digitalization (T_J1) ---
    "Bank XYZ sudah melakukan proses DIGITALISASI LAYANAN CABANG DENGAN BAIK": "Branch digitalization done well",
    "Keberadaan DIGITAL SIGNAGE di cabang XYZ MEMUDAHKAN saya sebagai nasabah dalam memperoleh informasi produk layanan XYZ": "Digital signage helps get info",
    "Keberadaan SMART TABLE di cabang XYZ MEMUDAHKAN bagi saya sebagai nasabah dalam dalam memperoleh informasi produk layanan XYZ(Note: JAWAB 999 JIKA CABANG TIDAK MEMILIKI SMART TABLE)": "Smart Table helps get info",
    "Keberadaan TABLET SURVEY di cabang XYZ MEMUDAHKAN saya sebagai nasabah untuk memberikan penilaian layanan tim cabang": "Survey tablet eases feedback",
    "Akses ke cabang XYZ mudah": "Easy branch access",

    # --- Additional granular attributes (KC2 / TL3 / CS3 / AT3 / H1A) ---
    "Area ruang Tertata dengan baik, rapi dan teratur": "Well-organised, tidy space",
    "Penampilan luar bangunan cabang dan papan nama cabang dalam keadaan bersih, jelas dan terawat": "Clean, well-kept exterior & signage",
    "Petunjuk arah parkir untuk nasabah yang jelas dan bersih (petunjuk arah, tanda-tanda seperti “area parkir mobil”, “area parkir motor”)": "Clear parking signage",
    "Kebersihan dan kenyamanan area Banking Hall (kursi ruang tunggu, AC, TV, Pencahayaan, harum, dll)": "Clean & comfortable banking hall",
    "Tersedia penunjuk arah ruang pelayanan nasabah yang jelas/mudah terlihat (CS, Teller, Toilet, dan bisnis unit lainnya)": "Clear service-area signage",
    "Bank yang memberikan banyak keuntungan finansial (bunga lebih tinggi, biaya yang rendah, tanpa biaya administrasi, asuransi gratis)": "Strong financial benefits",
    "Bank yang menawarkan produk untuk semua kebutuhan saya (tabungan regular, tabungan anak, tabungan rencana, tabungan dengan tambahan asuransi, tabungan haji, deposito, dan lain-lain)": "Products for every need",
    "CS memberikan edukasi tentang penggunaan e-channel (ATM, Mobile Banking, dll)": "CS educates on e-channels",
    "Teller memberikan edukasi tentang penggunaan e-channel (ATM, Mobile Banking, dll)": "Teller educates on e-channels",
    "Fitur-fitur yang ada di mesin ATM lengkap: pembayaran berbagai macam tagihan, transfer antar bank dan pembelian": "Complete ATM features",
    "Ketersediaan berbagai jenis ATM (tunai, setor tunai, non tunai)": "Various ATM types available",
    "Mesin ATM dapat berfungsi dengan baik ketika akan digunakan (tidak sering error, offline,struk selalu tersedia)": "ATMs work reliably",
    "Ruangan mesin ATMnya nyaman (sejuk, bersih, wangi)": "Comfortable ATM booth",
    "Penampilannya sesuai dengan standar (tinggi, tegap, besar dan tidak gemuk)": "Standard appearance",
    "Saya merasa dihargai menjadi nasabah bank ini dengan layanan yang ramah, peduli, dan tidak membeda-bedakan": "Valued through warm, fair service",
    "Saya merasa nyaman bertransaksi dengan bank ini dengan segala fasilitas yang diberikan (sistem antrian, e-channel, mesin setor tunai)": "Comfortable with the facilities",
}

# Emotions split for the affective composition chart.
POSITIVE_EMOTIONS = {
    "Happy", "Trusting", "Valued", "Cared for", "Safe",
    "Focused", "Pampered", "Interested", "Energized",
}
NEGATIVE_EMOTIONS = {
    "Dissatisfied", "Frustrated", "Disappointed", "Stressed",
    "Unhappy", "Ignored", "Rushed",
}


def translate(label):
    """Return the English label, falling back to the source text if unmapped."""
    return TRANSLATIONS.get(str(label).strip(), str(label).strip())


def translate_df(df, col="attribute"):
    """Translate the attribute column of a tidy scores DataFrame in place (copy)."""
    out = df.copy()
    if col in out.columns:
        out[col] = out[col].map(translate)
    return out
