# Event Aggregator Service

Service ini merupakan sistem agregasi event menggunakan Python, FastAPI, dan SQLite. Sistem bertugas menerima event, melakukan deduplikasi berdasarkan `(topic, event_id)`, serta menyimpan unique event.

---

## Setup dan Menjalankan Layanan

### Prasyarat

* Docker dan Docker Compose

### Dengan Docker Compose

Untuk menjalankan seluruh sistem (Aggregator dan Publisher):

```bash
docker compose up --build
```

Layanan Aggregator dapat diakses melalui `http://localhost:8080`.

Publisher akan secara otomatis mengirimkan 5.000 event, dengan 20% duplikasi event.

---

## Contoh Penggunaan API

### 1. Publish Event

**POST** `/publish`

Endpoint untuk mem-publish event ke aggregator

Contoh request body:
```json
[
  {
    "topic": "orders",
    "event_id": "ORD-123",
    "timestamp": "2024-03-20T10:00:00Z",
    "source": "checkout-service",
    "payload": {"amount": 99.99, "currency": "USD"}
  }
]
```

### 2. Metrik Sistem Aggregator

**GET** `/stats`

Metrik sistem aggregator dapat dilihat melalui endpoint ini. Metrik meliputi total event, total event unik, total event duplikat, daftar topik, dan uptime sistem.

Contoh respons:
```json
{
  "received": 5000,
  "unique_processed": 4012,
  "duplicate_dropped": 988,
  "topics": ["orders", "inventory", "notifications"],
  "uptime": 120.5
}
```

### 3. Agregasi Event

**GET** `/events?topic=EVENT_TOPIC`

Daftar event unik yang telah diproses dapat dilihat melalui event ini. Gunakan query parameter `topic` untuk memfilter berdasarkan topik.

Contoh respons:
```json
[
  {
    "topic": "inventory",
    "event_id": "2e6c5547-cbe0-4dd4-82e3-d5fb287f4928",
    "timestamp": "2026-04-24T07:15:20.241392",
    "source": "simulated_publisher",
    "payload": {
      "data": 703
    }
  },
  ...
]
```

---

## Pengujian

Pengujian dilakukan untuk memastikan fungsi deduplikasi, persistensi data, serta validasi skema berjalan dengan baik.

```bash
uv run pytest
```

### 1. Validasi Skema Data Tidak Valid 

Menguji respons sistem ketika input event tidak memenuhi skema yang ditentukan (misalnya, field wajib seperti `source` tidak disertakan). Sistem diharapkan mengembalikan kode status `422` sebagai indikasi kesalahan validasi.

### 2. Publikasi Event Tunggal

Menguji keberhasilan pengiriman satu event valid ke endpoint `/publish`. Sistem diharapkan mengembalikan status 200 serta jumlah event yang berhasil diproses.

### 3. Mekanisme Deduplikasi

Menguji kemampuan sistem dalam mengidentifikasi dan menolak event duplikat berdasarkan pasangan `(topic, event_id)`. Event yang sama dikirim dua kali, dan sistem diharapkan hanya memproses satu kali serta mencatat satu duplikat yang diabaikan.

### 4. Persistensi Data Antar Restart

Menguji apakah data yang telah disimpan tetap dikenali setelah simulasi restart sistem. Event yang sudah ada di basis data tidak boleh diproses ulang, dan harus dikenali sebagai duplikat.

### 5. Endpoint Metrik

Memverifikasi bahwa endpoint `/stats` dapat diakses dan mengembalikan atribut yang sesuai, yaitu `received`, `unique_processed`, dan `duplicate_dropped`.

### 6. Ingesti Data Secara Batch

Menguji kemampuan sistem dalam memproses beberapa event sekaligus dalam satu permintaan. Sistem diharapkan dapat memproses seluruh event dalam batch dan mengembalikan jumlah yang sesuai.

---

## Keputusan Desain dan Asumsi

### 1. Pengurutan Data

Sistem menggunakan mekanisme FIFO melalui `asyncio.Queue` dan satu worker process di latar belakang. Pengurutan global pada sistem terdistribusi sulit dijamin karena adanya latensi jaringan. Oleh karena itu, sistem memproses event sesuai urutan masuk setelah diterima oleh layanan.

### 2. Penyimpanan Data

SQLite dipilih karena kemudahan penggunaan tanpa konfigurasi tambahan serta dukungan terhadap prinsip ACID (Atomicity, Consistency, Isolation, Durability). Penggunaan indeks composite pada `(topic, event_id)` memungkinkan proses deduplikasi dilakukan secara efisien.

### 3. Idempotensi

Pendekatan at-least-once delivery ditangani melalui mekanisme deduplikasi. Jika terjadi pengiriman ulang oleh publisher, sistem tetap menerima permintaan tersebut, namun data duplikat akan diabaikan pada tahap pemrosesan, sehingga konsistensi data tetap terjaga.
