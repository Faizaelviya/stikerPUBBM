from django.db import models
from django.utils import timezone

# Model untuk SPBU (Stasiun Pengisian Bahan Bakar Umum)
class SPBU(models.Model):
    # Field untuk menyimpan nama SPBU
    spbu = models.CharField(max_length=100, unique=True)  

    # Menampilkan representasi string dari objek SPBU
    def __str__(self):
        return self.spbu  

# Model untuk StikerTera yang menyimpan informasi terkait tera SPBU
class StikerTera(models.Model):
    # Pilihan jenis layanan untuk tera
    JENIS_LAYANAN_CHOICES = [
        # Tera yang dilakukan setiap tahun
        ('Tahunan', 'Tera Ulang Tahunan'),  
        # Tera tambahan selain tahunan
        ('Tambahan', 'Tera Tambahan'),  
    ]
 
    # Relasi dengan model SPBU, di mana setiap StikerTera terkait dengan satu SPBU
    spbu = models.ForeignKey(SPBU, on_delete=models.CASCADE)  

    # Jumlah nozzle yang diuji pada SPBU
    nozzle = models.PositiveIntegerField()  

    # Jumlah PU BBM (Pengisian Ulang Bahan Bakar Minyak) yang diuji
    pu_bbm = models.PositiveIntegerField() 

    # Tanggal pengujian dilakukan
    tanggal_pengujian = models.DateField()  

    # Jenis layanan yang diberikan (Tahunan atau Tambahan)
    jenis_layanan = models.CharField(max_length=20, choices=JENIS_LAYANAN_CHOICES)  

    # Timestamp untuk mencatat waktu pembuatan atau pembaruan data StikerTera
    timestamp = models.DateTimeField(default=timezone.now)  

    # Menampilkan representasi string dari objek StikerTera
    def __str__(self):
        return f"{self.spbu.spbu} - {self.tanggal_pengujian} - {self.jenis_layanan}"
