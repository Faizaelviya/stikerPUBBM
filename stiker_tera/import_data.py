import csv
from stiker.models import DataHistoris  # Ganti kalau model ada di app lain

# Hapus data lama (kalau perlu)
DataHistoris.objects.all().delete()

# Path ke CSV (pakai raw string biar nggak error di Windows)
with open(r'data\data_historis.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        DataHistoris.objects.create(
            spbu=row['spbu'],
            tanggal_pengujian=row['tanggal_pengujian'],
            jenis_layanan=row['jenis_layanan'].strip(),  # Strip spasi
            nozzle=row['nozzle'],
            pu_bbm=row['pu_bbm'],
        )

print("✅ Import selesai!")
