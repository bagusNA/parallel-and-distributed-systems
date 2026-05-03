#import "@preview/kunskap:0.1.0":*

#show: kunskap.with(
    title: "Tugas 3 - Sinkronisasi dan Distributed Systems",
    author: "11231015 - Bagus Nur Andiansyah",
    date: datetime.today().display(),
    header: "Sistem Parallel dan Terdistribusi",
)

= Arsitektur & Algoritma dalam Sistem

== Arsitektur Sistem
#figure(
    image(bytes(read("docs/architecture.svg"))),
)

Sistem yang dibangun tersusun atas beberapa cluster layanan dengan fungsi yang berbeda, yaitu _gateway_, _lock management_, _cache_, _queue_, dan _persistent storage_.

Pada lapisan paling depan, _Client Gateway_ berperan sebagai titik masuk permintaan melalui layanan API Entry.
Komponen ini menerima permintaan dari klien dan meneruskannya ke _cluster_ _Lock Manager_.
_Cluster_ ini terdiri atas tiga node (Lock 1, Lock 2, dan Lock 3) yang menggunakan mekanisme konsensus berbasis Raft.
Pola koneksi antar node yang bersifat berantai memungkinkan koordinasi replikasi log dan pemilihan pemimpin (_leader election_), sehingga konsistensi distribusi kunci dapat dijaga sebelum permintaan diproses lebih lanjut.

Setelah melewati _Lock Manager_, permintaan diteruskan ke _Cache Cluster_ yang mengimplementasikan protokol MESI.
Mekanisme koherensi cache berfungsi untuk menjaga konsistensi data antar replika.
Alur ini memungkinkan data yang sering diakses dapat diproses dengan latensi rendah, sekaligus memastikan bahwa perubahan status cache (Modified, Exclusive, Shared, Invalid) terpropagasi secara benar sebelum interaksi dengan penyimpanan utama.

Selanjutnya, sistem meneruskan data ke _Queue Cluster_ yang berbasis PBFT (Practical Byzantine Fault Tolerance).
PBFT digunakan agar sistem dapat menghadapi lingkungan dengan potensi kesalahan arbitrer (_Byzantine faults_), terutama dalam pengelolaan pesan asinkron.

Pada lapisan akhir, seluruh alur berakhir pada _Persistent Store_ yang memanfaatkan Redis.
Terdapat dua jalur masuk menuju penyimpanan ini, yaitu melalui _junction_ dari _cluster_ kunci dan _cluster_ antrian, serta jalur langsung dari _cluster_ cache.
Penyimpanan persisten berfungsi sebagai sumber kebenaran utama (_source of truth_), dengan beberapa jalur sinkronisasi untuk memastikan integritas data dari berbagai subsistem.

== Algoritma

Sistem yang dibangun mengimplementasikan algoritma PBFT.
_Practical Byzantine Fault Tolerance_ (PBFT) sendiri merupakan algoritma konsensus yang dirancang untuk menjaga konsistensi sistem terdistribusi meskipun sebagian node mengalami kegagalan arbitrer (_Byzantine faults_), seperti memberikan informasi yang salah, tidak merespons, atau berperilaku tidak sesuai protokol.
PBFT umumnya digunakan pada sistem yang membutuhkan _robustness_ tanpa bergantung pada asumsi kepercayaan penuh terhadap seluruh node.

Dalam PBFT, sistem terdiri atas sejumlah replika (node) yang berperan secara kolektif untuk memproses permintaan klien.
Salah satu node bertindak sebagai _primary_ (pemimpin), sementara yang lain sebagai _backup_.
Proses konsensus berlangsung dalam tiga tahap utama, yaitu _pre-prepare_, _prepare_, dan _commit_.
Pada tahap _pre-prepare_, _primary_ menerima permintaan klien dan mendistribusikannya ke seluruh _backup_.
Selanjutnya, pada tahap _prepare_, setiap node memverifikasi pesan tersebut dan saling bertukar informasi untuk memastikan bahwa pesan yang diterima konsisten.
Tahap terakhir, _commit_, memastikan bahwa mayoritas node telah mencapai kesepakatan sebelum eksekusi dilakukan.

Keamanan PBFT didasarkan pada prinsip kuorum.
Untuk dapat mentoleransi hingga _f_ node yang bersifat Byzantine, sistem memerlukan minimal _3f + 1_ node.
Dengan demikian, konsensus dianggap tercapai jika terdapat setidaknya _2f + 1_ node yang menyetujui suatu nilai atau urutan operasi.
Pendekatan ini memastikan bahwa meskipun terdapat node yang gagal atau bertindak jahat (_malicious_), hasil akhir tetap konsisten di seluruh replika yang jujur.

Salah satu keunggulan utama PBFT adalah kemampuannya mencapai _finality_ secara deterministik, artinya setelah suatu keputusan diambil, tidak diperlukan konfirmasi tambahan seperti pada algoritma berbasis probabilistik.
Hal ini membuat PBFT cocok untuk sistem yang membutuhkan kepastian tinggi, seperti pengelolaan antrian terdistribusi atau sistem keuangan.
Namun, PBFT memiliki keterbatasan dalam hal skalabilitas, karena kompleksitas komunikasi meningkat secara kuadratik terhadap jumlah node akibat pertukaran pesan antar semua replika.


= Hasil
