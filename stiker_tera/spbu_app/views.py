from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import SPBU, StikerTera
from .forms import InputDataForm, SPBUForm
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import logging
import datetime

logger = logging.getLogger(__name__)

# Halaman dashboard
def dashboard(request):
    return render(request, 'dashboard.html')

# Halaman input data
def input_data(request):
    if request.method == 'POST':
        form = InputDataForm(request.POST)
        if form.is_valid():
            spbu = form.cleaned_data['spbu']
            spbu_baru = form.cleaned_data['spbu_baru']

            # Kalau user isi SPBU baru
            if not spbu and spbu_baru:
                try:
                    spbu = SPBU.objects.create(spbu=spbu_baru.strip())
                except Exception as e:
                    logger.error(f'Gagal membuat SPBU baru: {str(e)}')
                    messages.error(request, 'Gagal membuat SPBU baru.')
                    return render(request, 'input_data.html', {'form': form})

            pengujian = form.save(commit=False)
            pengujian.spbu = spbu
            pengujian.save()

            messages.success(request, 'Data berhasil disimpan.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = InputDataForm()

    return render(request, 'input_data.html', {'form': form})

# Halaman tambah SPBU
def tambah_spbu(request):
    if request.method == 'POST':
        form = SPBUForm(request.POST)

        if form.is_valid():
            nama = form.cleaned_data.get('spbu', '').strip()

            if not nama:
                messages.error(request, 'Nama SPBU harus diisi.')
            elif SPBU.objects.filter(spbu__iexact=nama).exists():
                messages.error(request, 'SPBU dengan nama tersebut sudah terdaftar.')
            else:
                form.save()
                messages.success(request, 'SPBU berhasil ditambahkan.')
                return redirect('input_data')
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = SPBUForm()

    return render(request, 'tambah_spbu.html', {'form': form})

# Halaman koreksi data
def koreksi_data(request):
    query = request.GET.get('q')
    if query:
        data = StikerTera.objects.filter(spbu__spbu__icontains=query)
    else:
        data = StikerTera.objects.all()
    context = {'data': data}
    return render(request, 'koreksi_data.html', context)

# Halaman edit data
def edit_data(request, data_id):
    data = get_object_or_404(StikerTera, pk=data_id)

    if request.method == "POST":
        data.nozzle = request.POST.get("nozzle")
        data.pu_bbm = request.POST.get("pu_bbm")
        data.jenis_layanan = request.POST.get("jenis_layanan")
        data.timestamp = timezone.now()  # update waktu perubahan
        data.save()
        return redirect("koreksi_data")

    return render(request, "edit_data.html", {"data": data})

# Halaman prediksi stiker
def prediksi_stiker(request):
    hasil = None
    if request.method == 'POST':
        try:
            tahun_input = int(request.POST.get('tahun'))
            if tahun_input < 2000 or tahun_input > 2100:
                messages.error(request, 'Tahun tidak valid. Masukkan antara 2000 - 2100.')
                return render(request, 'prediksi_stiker.html', {'hasil': hasil})
        except (TypeError, ValueError):
            messages.error(request, 'Tahun harus berupa angka.')
            return render(request, 'prediksi_stiker.html', {'hasil': hasil})

        # Ambil data historis
        data_qs = StikerTera.objects.select_related('spbu')
        if not data_qs.exists():
            messages.error(request, 'Belum ada data historis yang tersedia.')
            return render(request, 'prediksi_stiker.html', {'hasil': hasil})

        # Konversi ke DataFrame
        df = pd.DataFrame([{
            'Tahun': d.tanggal_pengujian.year,
            'pu_bbm': d.pu_bbm,
            'jenis_layanan': d.jenis_layanan
        } for d in data_qs])

        # Kategori tahun manual
        def kategori_tahun(tahun):
            if tahun <= 2019:
                return 1
            elif tahun <= 2022:
                return 2
            else:
                return 3

        df['Kategori Tahun'] = df['Tahun'].apply(kategori_tahun)
        le = LabelEncoder()
        df['kode_layanan'] = le.fit_transform(df['jenis_layanan'])

        # Validasi apakah jenis layanan target tersedia
        layanan_diperlukan = ['Tera Ulang Tahunan', 'Tera Ulang Tambahan']
        if not set(layanan_diperlukan).issubset(set(le.classes_)):
            logger.warning('Jenis layanan belum lengkap di data historis: ditemukan=%s', list(le.classes_))
            messages.warning(request, 'Jenis layanan belum lengkap. Tambahkan data terlebih dahulu.')
            return render(request, 'prediksi_stiker.html', {'hasil': hasil})

        # Model dan prediksi
        X = df[['Kategori Tahun', 'kode_layanan']]
        y = df['pu_bbm']
        model = DecisionTreeRegressor(criterion='entropy', random_state=42)
        model.fit(X, y)

        hasil_prediksi = []
        total_prediksi = 0
        for jenis in layanan_diperlukan:
            try:
                kategori = kategori_tahun(tahun_input)
                kode_layanan = le.transform([jenis])[0]
                prediksi = model.predict([[kategori, kode_layanan]])[0]
                nilai_bulat = round(prediksi)
                total_prediksi += nilai_bulat
                hasil_prediksi.append({
                    'Tahun': tahun_input,
                    'Jenis Layanan': jenis,
                    'Kategori Tahun': kategori,
                    'Prediksi PU BBM': nilai_bulat
                })
            except Exception as e:
                logger.error(f'Error saat prediksi untuk layanan "{jenis}" | kategori={kategori}, kode={kode_layanan} => {str(e)}')
                hasil_prediksi.append({
                    'Tahun': tahun_input,
                    'Jenis Layanan': jenis,
                    'Kategori Tahun': kategori,
                    'Prediksi PU BBM': 'Gagal diprediksi'
                })

        hasil = {
            'Total Prediksi': total_prediksi,
            'Rincian': hasil_prediksi
        }

    current_year = datetime.datetime.now().year
    tahun_range = range(2017, current_year + 2)

    return render(request, 'prediksi_stiker.html', {
        'hasil': hasil,
        'tahun_range': tahun_range
    })

