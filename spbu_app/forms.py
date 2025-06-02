from django import forms
from .models import StikerTera, SPBU
import datetime

# Pilihan jenis layanan yang tersedia keperluan input data Tera SPBU
JENIS_LAYANAN_CHOICES = [
    ('tera ulang tahunan', 'Tera Ulang Tahunan'),
    ('tambahan', 'Tambahan'),
]

# Form untuk input data Tera SPBU
class InputDataForm(forms.ModelForm):
    # Pilihan SPBU yang sudah ada (ModelChoiceField) 
    spbu = forms.ModelChoiceField(
        # Mengambil semua data SPBU yang ada
        queryset=SPBU.objects.all(),
        # Field ini wajib diisi  
        required=True,  
        # Label untuk field ini
        label="Pilih SPBU (jika sudah ada)",
        # Label saat tidak ada pilihan  
        empty_label="-- Pilih SPBU --",  
        # Menambahkan kelas CSS untuk styling
        widget=forms.Select(attrs={'class': 'form-control'})  
    )

    # Field untuk memasukkan nama SPBU baru jika tidak ada dalam daftar
    spbu_baru = forms.CharField(
        # Field ini tidak wajib diisi
        required=False,  
        # Label untuk field ini
        label="Atau Masukkan Nama SPBU Baru",  
        # Menambahkan placeholder pada input
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama SPBU baru jika tidak ada di atas'})  
    )

    # Field untuk memasukkan jumlah nozzle 
    jumlah_nozzle = forms.IntegerField(
        # Nilai minimal 1
        min_value=1,  
        # Label untuk field ini
        label="Jumlah Nozzle",  
        # Menambahkan kelas CSS untuk styling
        widget=forms.NumberInput(attrs={'class': 'form-control'})  
    )

    # Field untuk memasukkan jumlah PU BBM 
    jumlah_pu_bbm = forms.IntegerField(
        # Nilai minimal 1
        min_value=1,  
        # Label untuk field ini
        label="Jumlah PU BBM",  
        # Menambahkan kelas CSS untuk styling
        widget=forms.NumberInput(attrs={'class': 'form-control'})  
    )

    # Field untuk memilih tanggal pengujian (hanya bisa memilih tanggal di tahun ini)
    tanggal_pengujian = forms.DateField(
        widget=forms.DateInput(
            attrs={
                # Tipe input adalah tanggal
                'type': 'date',  
                # Batas bawah: awal tahun ini
                'min': f'{datetime.date.today().year}-01-01',  
                # Batas atas: akhir tahun ini
                'max': f'{datetime.date.today().year}-12-31',  
            }
        )
    )

    # Field untuk memilih jenis layanan dengan pilihan yang telah ditentukan
    jenis_layanan = forms.ChoiceField(
        # Pilihan jenis layanan
        choices=JENIS_LAYANAN_CHOICES,
        # Label untuk field ini  
        label="Jenis Layanan",  
        # Menambahkan kelas CSS untuk styling
        widget=forms.Select(attrs={'class': 'form-control'})  
    )

    # Konfigurasi model yang digunakan untuk form ini
    class Meta:
        model = StikerTera  
        fields = ['spbu', 'spbu_baru', 'jumlah_nozzle', 'jumlah_pu_bbm', 'tanggal_pengujian', 'jenis_layanan']  

# Form untuk input data SPBU baru
class SPBUForm(forms.ModelForm):
    # Konfigurasi model yang digunakan untuk form ini
    class Meta:
        model = SPBU  
        fields = '__all__'  
        widgets = {
            # Menambahkan kelas CSS pada field 'spbu'
            'spbu': forms.Select(attrs={'class': 'input'}),  
            # Menambahkan tipe input 'date' pada field 'tanggal_pengujian'
            'tanggal_pengujian': forms.DateInput(attrs={'type': 'date'}),  
            # Menambahkan kelas CSS pada field 'jenis_layanan'
            'jenis_layanan': forms.Select(attrs={'class': 'input'}),  
        }
