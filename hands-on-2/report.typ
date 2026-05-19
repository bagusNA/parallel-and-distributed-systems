#import "@preview/kunskap:0.1.0":*

#show: kunskap.with(
    title: "Tugas Praktikum 2 - Dockerfile",
    author: "11231015 - Bagus Nur Andiansyah",
    date: datetime.today().display(),
    header: "Sistem Parallel dan Terdistribusi",
)

Link _source code_:

= FROM Instruction

#figure(
    image("./assets/img.png")
)
#figure(
    image("./assets/img_1.png")
)

FROM merupakan instruksi yang umum digunakan pertama kali dalam membangun Docker image.
Docker image yang dibangun pada umumnya menggunakan image lain sebagai _base_-nya.
Command `docker build` digunakan untuk mem-_build_ Dockerfile yang telah dibuat.

= RUN Instruction

#figure(
    image("./assets/img_2.png")
)
#figure(
    image("./assets/img_3.png")
)

Instruksi RUN digunakan untuk menjalankan command ketika proses pembuatan image berjalan.
Dalam contoh ini dijalankan beberapa command yang outputnya dapat dilihat selama proses _image building_.

= CMD Instruction

#figure(
    image("./assets/img_4.png")
)
#figure(
    image("./assets/img_5.png")
)

CMD merupakan instruksi yang berisi command yang akan berjalan ketika container dijalankan, bukan dalam proses _image building_.
Dalam contoh ini, terlihat command `cat` berjalan hanya setelah container dijalankan.

= LABEL Instruction

#figure(
    image("./assets/img_6.png")
)
#figure(
    image("./assets/img_7.png")
)

LABEL digunakan untuk menyematkan metadata ke dalam image yang dibuat.
Metadata dapat berisi apapun, misalnya author, lisensi, dan tautan website.

= ADD Instruction

#figure(
    image("./assets/img_8.png")
)
#figure(
    image("./assets/img_9.png")
)

ADD digunakan untuk menambahkan file ke dalam _image_ yang dibangun.
ADD dapat menerima file maupun url, serta mampu meng-_extract file archive_.

= COPY Instruction

#figure(
    image("./assets/img_10.png")
)
#figure(
    image("./assets/img_11.png")
)

Mirip dengan ADD, COPY dapat menambahkan file dari _host machine_ ke dalam _image_ yang dibangun.
Perbedaannya COPY hanya menerima file saja.
Instruction ini sering digunakan untuk menambahkan _source code_ atau dependensi lain ke dalam _image_.

= .dockerignore

#figure(
    image("./assets/img_12.png")
)
#figure(
    image("./assets/img_13.png")
)

File `.dockerignore` berisikan daftar file dan folder yang akan dikecualikan dari command COPY dan ADD.
Dalam contoh ini, folder `temp` dan semua `*.log` dikecualikan dalam `.gitgnore` sehingga tidak muncul dalam hasil image yang dibuat.

= EXPOSE Instruction

#figure(
    image("./assets/img_14.png")
)
#figure(
    image("./assets/img_15.png")
)

Instruksi EXPOSE digunakan untuk mendokumentasikan port dan protocol mana yang dapat di-_listen_ dari container.
Dalam contoh ini digunakan port 8080 untuk di-_expose_, terlihat dalam hasil inspect image.

= ENV Instruction

#figure(
    image("./assets/img_16.png")
)
#figure(
    image("./assets/img_17.png")
)

ENV digunakan untuk mendeklarasikan _environment variable_ yang dapat digunakan dalam proses _building image_.
Untuk menggunakan ENV yang telah dibuat, dapat menggunakan syntax `${NAMA_ENV}`
ENV dapat ditimpa ketika membuat container dengan dengan option `--env key=value`.

= VOLUME Instruction

#figure(
    image("./assets/img_18.png")
)
#figure(
    image("./assets/img_19.png")
)
#figure(
    image("./assets/img_20.png")
)
#figure(
    image("./assets/img_21.png")
)

Instruksi VOLUME digunakan untuk membuat volume secara otomotis ketika container dibuat.
Dalam contoh ini, digunakan volume `/logs`.

= WORKDIR Instruction

#figure(
    image("./assets/img_22.png")
)
#figure(
    image("./assets/img_23.png")
)

Instruksi WORKDIR berfungsi untuk menentukan directory berjalannya instruksi RUN, CMD, ENTRYPOINT, COPY, dan ADD.

= USER Instruction

#figure(
    image("./assets/img_24.png")
)
#figure(
    image("./assets/img_25.png")
)

Instruksi USER berfungsi untuk mengubah user maupun user group untuk image yang dibangun.
Secara default, docker menggunakan `root` user dan dapat memberikan beberapa _concern_ untuk use case tertentu.
Dalam contoh, digunakan user `bagus` dengan user group `etmin` sebagai pengganti.

= ARG Instruction

#figure(
    image("./assets/img_26.png")
)
#figure(
    image("./assets/img_27.png")
)

ARG digunakan untuk mendefinisikan variabel yang dapat ditimpa oleh pengguna dalam proses build.
Mirip dengan ENV, ARG sangat berguna untuk mengirimkan parameter atau data yang diperlukan dalam proses build image yang tidak dapat di-_hardcode_ langsung.
Lifetime ARG hanya selama proses build image dan tidak sampai proses run container.

= HEALTHCHECK Instruction

#figure(
    image("./assets/img_28.png")
)
#figure(
    image("./assets/img_29.png")
)
#figure(
    image("./assets/img_30.png")
)

HEALTHCHECK digunakan untuk mengecek status _ready_ (_healthy_) atau tidaknya (_unhealthy_) container.
Umumnya digunakan endpoint khusus yang akan dipanggil melalui HEALTHCHECK secara berkala.

= ENTRYPOINT Instruction

#figure(
    image("./assets/img_31.png")
)
#figure(
    image("./assets/img_32.png")
)

ENTRYPOINT berfungsi untuk menentukan executable file yang akan dijalankan ketika container berjalan.
Pada contoh ini, `go run` akan berjalan ketika container dimulai.

= Multi-Stage Dockerfile

#figure(
    image("./assets/img_33.png")
)
#figure(
    image("./assets/img_34.png")
)

Untuk meminimalkan besaran image yang dihasilkan, dapat dilakukan approach multi-stage.
Tiap stage dalam Dockerfile melakukan pengolahan menggunakan base image yang sesuai, dengan stage terakhir akan digunakan sebagai base image dalam image yang dibuat.
Misalnya, digunakan dua stage terpisah project frontend berbasis Vite.
Stage pertama digunakan untuk mem-_build_ project dengan base image dari Node.js.
Sedangkan stage kedua cukup meng-_copy_ build file dari stage sebelumnya dan menyajikannya melalui web server dengan base image Nginx atau Caddy.