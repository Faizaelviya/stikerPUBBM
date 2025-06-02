from django.db import models
from django.utils import timezone

class SPBU(models.Model):
    spbu = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.spbu

class StikerTera(models.Model):
    JENIS_LAYANAN_CHOICES = [
        ('Tahunan', 'Tera Ulang Tahunan'),
        ('Tambahan', 'Tera Tambahan'),
    ]

    spbu = models.ForeignKey(SPBU, on_delete=models.CASCADE)
    nozzle = models.PositiveIntegerField()
    pu_bbm = models.PositiveIntegerField()
    tanggal_pengujian = models.DateField()
    jenis_layanan = models.CharField(max_length=20, choices=JENIS_LAYANAN_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.spbu.spbu} - {self.tanggal_pengujian} - {self.jenis_layanan}"

