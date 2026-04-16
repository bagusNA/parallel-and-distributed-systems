# Simulasi Model Komunikasi Sistem Terdistribusi

Simulasi model komunikasi sistem terdistribusi melalui aplikasi berbasis arsitektur event-driven.
Aplikasi ini menggunakan Spring Boot, gRPC, dan Apache Kafka dalam struktur multimodule.
Proyek ini dirancang untuk mendemonstrasikan model komunikasi _request-response_ yang bersifat _synchronous_ dan _publish-subscriber_ yang bersifat _asynchronous_ dalam arsitektur sistem terdistribusi.

---

## Daftar Isi

* [Pendahuluan](#pendahuluan)
* [Tujuan](#tujuan)
* [Arsitektur Sistem](#arsitektur-sistem)
* [Model Komunikasi](#model-komunikasi)
* [Struktur Proyek](#struktur-proyek)
* [Logika Simulasi](#logika-simulasi)
* [Cara Menjalankan](#cara-menjalankan)
* [Cara Menggunakan](#cara-menggunakan)
* [Visualisasi](#visualisasi)
* [Interpretasi Hasil](#interpretasi-hasil)
* [Karakteristik Sistem](#karakteristik-sistem)
* [Kesimpulan](#kesimpulan)

---

## Pendahuluan

Proyek ini merupakan simulasi sistem pemrosesan order yang terdiri dari beberapa modul independen.
Sistem memanfaatkan pendekatan event-driven untuk mensimulasikan model publish-subscriber dan request-response tradisional.

---

## Tujuan

Simulasi ini bertujuan untuk:

* Mengilustrasikan model request-response dan publish-subscriber
* Memahami perbedaan model request-response dan publish-subscriber
* Memvisualisasikan alur pemrosesan data
* Mengimplementasikan integrasi gRPC dan Kafka

---

## Arsitektur Sistem

Sistem terdiri dari empat modul utama:

* **Order Module** → Entry point sistem
* **Notification Module** → Logging notifikasi
* **Inventory Module** → Manajemen stok
* **Analytics Module** → Agregasi data

Meski model Remote Procedure Call (RPC) tidak disajikan dalam simulasi ini, arsitektur sistem tetap memanfaatkan RPC sebagai bentuk implementasinya.

### Alur Sistem

```
Client
  │
  ▼
Order Module
  │
  ▼
Kafka (order-event)
  ├── Notification Module
  ├── Inventory Module
  └── Analytics Module
```

---

## Struktur Proyek

```
assignment2/
│
├── services/
│   ├── order-module/
│   ├── notification-module/
│   ├── invetory-module/
│   └── analytics-module/
├── frontend/
├── proto/
└── shared/
```

---

## Alur Simulasi

### Create Order Flow

1. Client mengirim request place order
2. Order dibuat dan dipublish dari order module
3. Modul notifikasi, inventory, dan analitik menerima event dan memprosesnya masing-masing.

### Event Payload

* user_id
* item_id
* quantity

### Subscriber Behavior

#### Notification Module

* Menyimpan log notifikasi

#### Inventory Module

* Mengurangi stok barang

#### Analytics Module

* Menghitung jumlah tipe barang terjual

---

## Cara Menjalankan

### Prasyarat

* Java 25 JDK
* Gradle
* Docker & Docker Compose

### Langkah

1. Jalankan Docker Compose untuk Kafka dan Frontend
   ```bash
   docker compose up -d
   ```
2. Jalankan masing-masing module:

   ```bash
   ./gradlew :services:order-service:bootRun
   ./gradlew :services:notification-service:bootRun
   ./gradlew :services:inventory-service:bootRun
   ./gradlew :services:analytics-service:bootRun
   ```

3. Buka url di browser
   ```bash
   localhost:3000
   ```

---

## Visualisasi

Aplikasi menyediakan tampilan web untuk:

### 1. Visualisasi Model
* Alur data dalam simulasi divisualisasikan sebagai event yang turun atau mengalir dari atas ke bawah, menggambarkan representasi data yang mengalir dari publisher ke subscriber.

### 2. Inventory

* Menampilkan stok barang

### 3. Notification Log

* Menampilkan daftar notifikasi order

### 4. Analytics

* Menampilkan jumlah tipe barang terjual

---

## Interpretasi Hasil

### Request-Response
Bersifat sinkron, di mana client harus menunggu respon dari server.
Memiliki latency yang deterministik, karena hanya melibatkan satu interaksi langsung.
Ketergantungan tinggi antara client dan server (tight coupling secara waktu).
Tidak cocok untuk proses _long-running_.

Hasil Pengamatan:

* Order berhasil dibuat secara langsung setelah request dikirim
* Lama respons sangat bergantung pada lama proses di server karena sifatnya yang synchronous atau blocking.

### Publish-Subscribe

Bersifat asinkron, tidak memerlukan respon langsung.
Producer tidak mengetahui siapa saja consumer.
Mendukung loose coupling antar modul.
Memungkinkan pemrosesan paralel oleh banyak subscriber.

Hasil Pengamatan:

* Setelah order dibuat, efeknya (stok berkurang, log tercatat, data analytics bertambah) tidak selalu terjadi secara instan
* Setiap modul memproses event secara independen.
* Jika salah satu modul gagal, modul lain tetap berjalan.

---
