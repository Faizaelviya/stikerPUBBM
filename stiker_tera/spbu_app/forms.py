from django import forms
from .models import StikerTera, SPBU
import datetime

JENIS_LAYANAN_CHOICES = [
    ('tera ulang tahunan', 'Tera Ulang Tahunan'),
    ('tambahan', 'Tambahan'),
]

class InputDataForm(forms.ModelForm):
    spbu = forms.ModelChoiceField(
    queryset=SPBU.objects.all(),
    required=False,
    label="Pilih SPBU (jika sudah ada)",
    empty_label="-- Pilih SPBU --",
    widget=forms.Select(attrs={'class': 'form-control'})
)


    spbu_baru = forms.CharField(
        required=False,
        label="Atau Masukkan Nama SPBU Baru",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama SPBU baru jika tidak ada di atas'})
    )

    jumlah_nozzle = forms.IntegerField(
        min_value=0,
        label="Jumlah Nozzle",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    jumlah_pu_bbm = forms.IntegerField(
        min_value=0,
        label="Jumlah PU BBM",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    tanggal_pengujian = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': f'{datetime.date.today().year}-01-01',
                'max': f'{datetime.date.today().year}-12-31',
            }
        )
    )

    jenis_layanan = forms.ChoiceField(
        choices=JENIS_LAYANAN_CHOICES,
        label="Jenis Layanan",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StikerTera
        fields = ['spbu', 'spbu_baru', 'jumlah_nozzle', 'jumlah_pu_bbm', 'tanggal_pengujian', 'jenis_layanan']

class SPBUForm(forms.ModelForm):
    class Meta:
        model = SPBU
        fields = '__all__'
        widgets = {
            'spbu': forms.Select(attrs={'class': 'input'}),
            'tanggal_pengujian': forms.DateInput(attrs={'type': 'date'}),
            'jenis_layanan': forms.Select(attrs={'class': 'input'}),
        }

class PrediksiStikerForm(forms.Form):
    tahun = forms.IntegerField(
        label="Tahun Prediksi",
        min_value=2000,
        max_value=2100,
        initial=datetime.date.today().year + 1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan tahun prediksi'
        })
    )
    
class TahunForm(forms.Form):
    tahun = forms.IntegerField(
        label='Tahun',
        min_value=2017,
        max_value=datetime.datetime.now().year + 5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2025'})
    )