#import "@preview/kunskap:0.1.0":*

#show: kunskap.with(
    title: "Tugas Praktikum 3 - Docker Compose",
    author: "11231015 - Bagus Nur Andiansyah",
    date: datetime.today().display(),
    header: "Sistem Parallel dan Terdistribusi",
)


= Docker Compose Version

Versi Docker Compose dapat ditampilkan menggunakan `docker compose version`.
Dalam pengerjaan ini digunakan versi 5.1.2

#figure(
    image("./assets/version-01.png")
)

= Configuration File

Docker Compose menggunakan format YAML dalam file konfigurasinya.
Format YAML sensitif terhadap indentasi, serupa dengan syntax bahasa pemrograman Python.
Tiap service didefinisikan dalam file konfigurasi tersebut.

#figure(
    image("./assets/conf-01.png")
)

= Create Container

Service yang telah didefinisikan dalam file konfigurasi Docker Compose dapat di-_create_ dengan `docker compose create`.

#figure(
    image("./assets/basic-01.png")
)

= Start Container

Service yang telah dibuat tidak otomatis berjalan, melainkan dapat dijalankan secara manual dengan menggunakan `docker compose start`.

#figure(
    image("./assets/basic-02.png")
)

= List Container

Service yang telah berjalan dapat ditampilkan menggunakan `docker compose ps`

#figure(
    image("./assets/basic-03.png")
)

= Stop Container

Service yang telah berjalan dapat dihentikan menggunakan `docker compose stop`

#figure(
    image("./assets/basic-04.png")
)

= Remove Container

Service yang telah berjalan dapat dihapus menggunakan `docker compose down`

#figure(
    image("./assets/basic-05.png")
)

= Project Name

Secara default, project name dari konfigurasi Docker Compose akan menggunakan nama folder tempat file konfigurasi berada.
Project-project tersebut dapat dilihat menggunakan `docker compose ls`

#figure(
    image("./assets/basic-06.png")
)

= Service

Docker compose dapat menerima banyak service dalam satu konfigurasi, dengan catatan nama tiap service harus unik.
Dalam contoh berikut digunakan service `nginx-example-second` dan `mongodb-example`.

#figure(
    image("./assets/service-01.png")
)

= Port

Port yang digunakan dalam aplikasi dapat diexpose dengan menggunakan property `ports`.
Dalam contoh berikut diekspos dua port berbeda, yakni `8080/tcp` dan `8081`.

#figure(
    image("./assets/port-01.png")
)

= Enviromnent Variable

Service dalam Docker Compose dapat menerima _environment variable_ dengan menggunakan property `environment`.

#figure(
    image("./assets/env-01.png")
)

= Bind Mount

Folder yang ada dalam sistem host dapat di-_bind mount_ ke dalam service yang membutuhkan dengan menggunakan property `volumes`.
Misalnya dalam contoh ini, dua buah folder (`data-mongo1` dan `data-mongo2`) dimount ke masing-masing service mongodb.

#figure(
    image("./assets/bind-01.png")
)

= Volume

Tidak hanya folder pada sistem host, volume yang dimanage oleh docker juga dapat dimount ke service.
Volume tersebut perlu didefinisikan dahulu dalam section `volumes`.
Dalam contoh ini, kini digunakan volume `mongo-data1` dan `mongo-data2` sebagai pengganti folder yang digunakan sebelumnya.

#figure(
    image("./assets/volume-01.png")
)

= Network

Jika ingin mengorganisir network secara mandiri (tidak bergantung pada default network yang dibuat oleh Docker), dapat
digunakan section `networks`.
Setelah didefinisikan, network dapat dikaitkan ke service dengan didaftarkan (di-_list_) pada property `networks`.

#figure(
    image("./assets/network-01.png")
)

= Depends On

Ketika service memiliki dependensi erat terhadap service lain, hubungan tersebut dapat didefinisikan dengan menggunakan property `depends_on`.
Akibatnya, service yang ada dalam `depends_on` akan berjalan terlebih dahulu sebelum _dependant service_-nya berjalan.
Di sini digunakan _dependant service_ (_myapp_) dengan Dockerfile custom, bukan menggunakan `mongo-express` karena image tersebut sudah tidak dimaintain
dan terdapat error yang diakibatkan oleh image `mongo-express` yang tidak membaca _environment variables_.

#figure(
    image("./assets/depends-01.png")
)

= Restart

`docker compose restart` dapat digunakan untuk merestart seluruh service dalam konfigurasi Docker Compose.

#figure(
    image("./assets/restart-01.png")
)

= Resource Limit

Resource limit dapat digunakan untuk mengatur dan membatasi penggunaan resource tiap service.
Konfigurasi limit tersebut dapat didefinisikan dalam property `deploy`.

#figure(
    image("./assets/resource-01.png")
)

= Dockerfile

Selain menggunakan image pada registry, dapat digunakan pula file Dockerfile sebagai dasar image untuk service.
Dockerfile ditetapkan pada property `build`.

#figure(
    image("./assets/dockerfile-01.png")
)

= Healthcheck

Mirip dengan healthcheck pada Dockerfile, konfigurasi Docker Compose juga dapat melakukan _health check_ pada service yang berjalan.

#figure(
    image("./assets/healthcheck-01.png")
)

= Extend Service

Suatu konfigurasi Docker Compose dapat di-_extend_ atau ditimpa dengan konfigurasi lain.
Dalam contoh ini, konfigurasi `docker-compose.yaml` di-_extend_ dengan `docker-compose.dev.yaml` dengan menggunakan `docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up`.

#figure(
    image("./assets/extend-01.png")
)
