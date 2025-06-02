import logging
import pandas as pd
import datetime
import math

from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, Case, When, IntegerField
from django.db.models.functions import ExtractYear
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import SPBU, StikerTera
from .forms import InputDataForm, SPBUForm


# Logger untuk mencatat error atau aktivitas
logger = logging.getLogger(__name__)

# Halaman dashboard
def dashboard(request):
    # Menampilkan template dashboard
    return render(request, 'dashboard.html')

# Halaman input data
def input_data(request):
    if request.method == 'POST':
        form = InputDataForm(request.POST)
        
        if form.is_valid():
            spbu = form.cleaned_data['spbu']
            spbu_baru = form.cleaned_data['spbu_baru']

            # Jika SPBU yang dipilih kosong dan SPBU baru ada
            if not spbu and spbu_baru:
                try:
                    # Membuat SPBU baru jika belum ada
                    spbu = SPBU.objects.create(spbu=spbu_baru.strip())

                except Exception as e:
                    # Catat error jika gagal membuat SPBU baru
                    logger.error(f'Gagal membuat SPBU baru: {str(e)}')
                    messages.error(request, 'Gagal membuat SPBU baru.')
                    return render(request, 'input_data.html', {'form': form})

            # Menyimpan data pengujian stiker
            pengujian = form.save(commit=False)
            pengujian.spbu = spbu
            pengujian.save()
            messages.success(request, 'Data berhasil disimpan.')

            # Pengalihan ke dashboard setelah data disimpan
            return redirect('dashboard')  
        
        else:
            messages.error(request, 'Form tidak valid.')

    else:
        form = InputDataForm()
   
    # Menampilkan template input data
    return render(request, 'input_data.html', {'form': form})

# Halaman untuk menambah SPBU baru
def tambah_spbu(request):
    if request.method == 'POST':
        nama = request.POST.get('spbu', '').strip()

        # Memeriksa jika nama kosong
        if not nama:
            return render(request, 'hasil_tambah.html', {
                'success': False,
                'message': 'Nama SPBU harus diisi.'
            })

        # Memeriksa apakah SPBU sudah ada di database
        if SPBU.objects.filter(spbu__iexact=nama).exists():
            return render(request, 'hasil_tambah.html', {
                'success': False,
                'message': 'SPBU telah terdaftar.'
            })

        # Jika validasi sukses, menyimpan SPBU baru
        try:
            spbu_obj = SPBU(spbu=nama)
            spbu_obj.save()
            return render(request, 'hasil_tambah.html', {
                'success': True,
                'message': 'SPBU berhasil ditambahkan.'
            })
        
        except Exception as e:
            
            # Menangani error saat menyimpan SPBU baru
            return render(request, 'hasil_tambah.html', {
                'success': False,
                'message': 'Terjadi kesalahan saat menyimpan data.'
            })

    # Menampilkan template tambah SPBU
    return render(request, 'tambah_spbu.html', {'form': SPBUForm()})

# Cek nama SPBU untuk memastikan sudah terdaftar atau belum
def cek_nama_spbu(request):

    # Mengambil parameter 'nama' dari query string
    nama_spbu = request.GET.get('nama')  

    # Memeriksa nama SPBU yang sudah ada
    if SPBU.objects.filter(spbu__iexact=nama_spbu).exists():  
        return JsonResponse({'success': False})
    
    return JsonResponse({'success': True})

# Halaman untuk melihat dan mengoreksi data yang sudah diinput
def koreksi_data(request):
    # Query pencarian
    query = request.GET.get('q', '')  
    # Mengambil data StikerTera yang terkait dengan SPBU
    data = StikerTera.objects.select_related('spbu')  
    if query:
        # Menyaring berdasarkan nama SPBU
        data = data.filter(spbu__spbu__icontains=query)  

    context = {
        'data': data,
        'query': query,
    }

    # Menampilkan template koreksi data
    return render(request, 'koreksi_data.html', context)

# Halaman untuk mengedit data berdasarkan ID
def edit_data(request, data_id):
    # Mengambil data berdasarkan primary key (ID), jika tidak ditemukan maka akan muncul 404
    data = get_object_or_404(StikerTera, pk=data_id)

    if request.method == "POST":
        # Memperbarui data dari form POST yang dikirim pengguna
        data.nozzle = request.POST.get("nozzle")
        data.pu_bbm = request.POST.get("pu_bbm")
        data.jenis_layanan = request.POST.get("jenis_layanan")
        # Memperbarui waktu terakhir pengeditan
        data.timestamp = timezone.now()
        # Menyimpan perubahan ke database  
        data.save()  
        # Mengarahkan kembali ke halaman koreksi setelah edit
        return redirect("koreksi_data")  

    # Menampilkan template edit data
    return render(request, "edit_data.html", {"data": data})

# Pembentukan decision tree
def decision_tree(request):
    # Total jumlah pu_bbm per tahun
    data = (
        StikerTera.objects
        .annotate(tahun=ExtractYear('tanggal_pengujian'))
        .filter(tahun__gte=2017, tahun__lte=2024)
        .values('tahun')
        .annotate(jumlah_putotal=Sum('pu_bbm'))
        .order_by('tahun')
    )

    # Jumlah pu_bbm per jenis layanan (Tahunan/Tambahan)
    data_jenis = (
        StikerTera.objects
        .annotate(tahun=ExtractYear('tanggal_pengujian'))
        .filter(tahun__gte=2017, tahun__lte=2024)
        .values('tahun')
        .annotate(
            pu_bbm_tahunan=Sum(
                Case(
                    When(jenis_layanan='Tahunan', then='pu_bbm'),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            pu_bbm_tambahan=Sum(
                Case(
                    When(jenis_layanan='Tambahan', then='pu_bbm'),
                    default=0,
                    output_field=IntegerField()
                )
            ),
        )
        .order_by('tahun')
    )

    # Membuat dictionary tahun -> data
    tahun_to_data = {item['tahun']: item for item in data_jenis}

    # Membuat dictionary tahun -> total pu untuk ambil kategori
    tahun_to_total_pu = {}
    for item in data_jenis:
        total_pu = item['pu_bbm_tahunan'] + item['pu_bbm_tambahan']
        tahun_to_total_pu[item['tahun']] = total_pu

    data_tambahan_x2 = []
    data_tahunan_x2 = []

    tahun_list = sorted(tahun_to_data.keys())

    for tahun in tahun_list:
        tahun_x2 = tahun - 2
        if tahun_x2 in tahun_to_data and tahun in tahun_to_total_pu:
            tambahan = tahun_to_data[tahun_x2]['pu_bbm_tambahan']
            tahunan = tahun_to_data[tahun_x2]['pu_bbm_tahunan']

            total_pu = tahun_to_total_pu[tahun]  

            # Kategorisasi berdasarkan total PU tahun yang diprediksi
            if total_pu <= 350:
                kategori = 1
            elif total_pu <= 400:
                kategori = 2
            else:
                kategori = 3

            data_tambahan_x2.append({
                'tahun': tahun,
                'jumlah_pu_bbm_tambahan_x2': tambahan,
                'kategori': kategori
            })

            data_tahunan_x2.append({
                'tahun': tahun,
                'jumlah_pu_bbm_tahunan_x2': tahunan,
                'kategori': kategori
            })

    # Perhitungan Entropy Awal 
    kategori_counts = {1: 0, 2: 0, 3: 0}

    for item in data_tambahan_x2:  
        kategori = item['kategori']
        kategori_counts[kategori] += 1

    total_data = sum(kategori_counts.values())

    entropy = 0
    for count in kategori_counts.values():
        if count > 0:
            p = count / total_data
            entropy += -p * math.log2(p)

    entropy = round(entropy, 4)

    # PU BBM Tambahan
    nilai_tambahan = [item['jumlah_pu_bbm_tambahan_x2'] for item in data_tambahan_x2]
    nilai_tambahan = sorted(set(nilai_tambahan))  

    split_points_tambahan = []
    for i in range(len(nilai_tambahan) - 1):
        split = (nilai_tambahan[i] + nilai_tambahan[i+1]) / 2
        split_points_tambahan.append(split)

    split_info_gain_tambahan = []

    for split in split_points_tambahan:
        left_counts = {1: 0, 2: 0, 3: 0}
        right_counts = {1: 0, 2: 0, 3: 0}
        left_total = 0
        right_total = 0

        for item in data_tambahan_x2:
            if item['jumlah_pu_bbm_tambahan_x2'] <= split:
                left_counts[item['kategori']] += 1
                left_total += 1
            else:
                right_counts[item['kategori']] += 1
                right_total += 1

        # Entropy left
        entropy_left = 0
        for count in left_counts.values():
            if count > 0:
                p = count / left_total
                entropy_left += -p * math.log2(p)

        # Entropy right
        entropy_right = 0
        for count in right_counts.values():
            if count > 0:
                p = count / right_total
                entropy_right += -p * math.log2(p)

        # Weighted entropy
        weighted_entropy = (left_total / total_data) * entropy_left + (right_total / total_data) * entropy_right

        # Information Gain
        info_gain = entropy - weighted_entropy
        info_gain = round(info_gain, 3)

        # Split Information
        split_info = 0
        if left_total > 0:
            p_left = left_total / total_data
            split_info += -p_left * math.log2(p_left)
        if right_total > 0:
            p_right = right_total / total_data
            split_info += -p_right * math.log2(p_right)
        split_info = round(split_info, 3)

        # Gain Ratio
        if split_info != 0:
            gain_ratio = round(info_gain / split_info, 3)
        else:
            gain_ratio = 0  

        split_info_gain_tambahan.append({
            'split_point': split,
            'information_gain': info_gain,
            'split_information': split_info,
            'gain_ratio': gain_ratio,
        })

    # Mencari split point dengan gain ratio tertinggi
    best_split_tambahan = max(split_info_gain_tambahan, key=lambda x: x['gain_ratio'])
   

    # PU BBM Tahunan
    nilai_tahunan = [item['jumlah_pu_bbm_tahunan_x2'] for item in data_tahunan_x2]
    nilai_tahunan = sorted(set(nilai_tahunan))  # Unik + urut

    split_points_tahunan = []
    for i in range(len(nilai_tahunan) - 1):
        split = (nilai_tahunan[i] + nilai_tahunan[i+1]) / 2
        split_points_tahunan.append(split)

    split_info_gain_tahunan = []

    for split in split_points_tahunan:
        left_counts = {1: 0, 2: 0, 3: 0}
        right_counts = {1: 0, 2: 0, 3: 0}
        left_total = 0
        right_total = 0

        for item in data_tahunan_x2:
            if item['jumlah_pu_bbm_tahunan_x2'] <= split:
                left_counts[item['kategori']] += 1
                left_total += 1
            else:
                right_counts[item['kategori']] += 1
                right_total += 1

        # Entropy left
        entropy_left = 0
        for count in left_counts.values():
            if count > 0:
                p = count / left_total
                entropy_left += -p * math.log2(p)

        # Entropy right
        entropy_right = 0
        for count in right_counts.values():
            if count > 0:
                p = count / right_total
                entropy_right += -p * math.log2(p)

        # Weighted entropy
        weighted_entropy = (left_total / total_data) * entropy_left + (right_total / total_data) * entropy_right

        # Information Gain
        info_gain = entropy - weighted_entropy
        info_gain = round(info_gain, 3)
    
        # Split Information
        split_info = 0
        if left_total > 0:
            p_left = left_total / total_data
            split_info += -p_left * math.log2(p_left)
        if right_total > 0:
            p_right = right_total / total_data
            split_info += -p_right * math.log2(p_right)
        split_info = round(split_info, 3)

        # Gain Ratio
        if split_info != 0:
            gain_ratio = round(info_gain / split_info, 3)
        else:
            gain_ratio = 0  

        split_info_gain_tahunan.append({
            'split_point': split,
            'information_gain': info_gain,
            'split_information': split_info,
            'gain_ratio': gain_ratio,
        })

    # Mencari split point dengan gain ratio tertinggi
    best_split_tahunan = max(split_info_gain_tahunan, key=lambda x: x['gain_ratio'])

    # Data jumlah pu bbm tahunan lebih besar dari split point terbaik
    filtered_data = [
        item for item in data_tahunan_x2
        if item['jumlah_pu_bbm_tahunan_x2'] > best_split_tahunan['split_point']
    ]

    # Menghitung total data 
    total_filtered = len(filtered_data)

    # Menghitung jumlah masing-masing kategori
    kategori_counts = {1: 0, 2: 0, 3: 0}
    for item in filtered_data:
        kategori_counts[item['kategori']] += 1

    # Entropy baru
    entropy_filtered = 0
    for count in kategori_counts.values():
        if count > 0:
            p = count / total_filtered
            entropy_filtered += -p * math.log2(p)

    entropy_filtered = round(entropy_filtered, 3)

    # Data PU BBM tambahan setelah penyaringan PU BBM tahunan
    tambahan_lookup = {item['tahun']: item for item in data_tambahan_x2}

    filtered_data = []
    for item in data_tahunan_x2:
        if item['jumlah_pu_bbm_tahunan_x2'] > best_split_tahunan['split_point']:
            tahun = item['tahun']
            tambahan_item = tambahan_lookup.get(tahun, {})
            filtered_data.append({
                'tahun': tahun,
                'jumlah_pu_bbm_tahunan_x2': item['jumlah_pu_bbm_tahunan_x2'],
                'jumlah_pu_bbm_tambahan_x2': tambahan_item.get('jumlah_pu_bbm_tambahan_x2', 0),
                'kategori': item['kategori'],
            })

    filtered_data_tambahan = [
        {
            'tahun': item['tahun'],
            'jumlah_pu_bbm_tambahan_x2': item['jumlah_pu_bbm_tambahan_x2'],
            'kategori': item['kategori'],
        }
        for item in filtered_data
        ]

    # Data untuk dihitung split pointnya
    data_tambahan_filtered = filtered_data_tambahan

    # Total data
    total_data = len(data_tambahan_filtered)

    # Entropy awal
    kategori_counts = {1: 0, 2: 0, 3: 0}
    for item in data_tambahan_filtered:
        kategori_counts[item['kategori']] += 1

    entropy_awal = 0
    for count in kategori_counts.values():
        if count > 0:
            p = count / total_data
            entropy_awal += -p * math.log2(p)

    entropy_awal = round(entropy_awal, 3)

    # Mengurutkan berdasarkan jumlah PU BBM tambahan
    data_sorted = sorted(filtered_data_tambahan, key=lambda x: x['jumlah_pu_bbm_tambahan_x2'])

    # Mencari kandidat split point
    split_points = []
    for i in range(len(data_sorted) - 1):
        current = data_sorted[i]['jumlah_pu_bbm_tambahan_x2']
        next = data_sorted[i + 1]['jumlah_pu_bbm_tambahan_x2']
        if current != next:
            split = (current + next) / 2
            split_points.append(split)


    # Menghitung untuk setiap split point
    split_info_gain_tambahan2 = []

    for split in split_points:
        left = [item for item in data_sorted if item['jumlah_pu_bbm_tambahan_x2'] <= split]
        right = [item for item in data_sorted if item['jumlah_pu_bbm_tambahan_x2'] > split]

        left_total = len(left)
        right_total = len(right)

        # Entropy left
        left_counts = {1: 0, 2: 0, 3: 0}
        for item in left:
            left_counts[item['kategori']] += 1

        entropy_left = 0
        for count in left_counts.values():
            if count > 0:
                p = count / left_total
                entropy_left += -p * math.log2(p)

        # Entropy right
        right_counts = {1: 0, 2: 0, 3: 0}
        for item in right:
            right_counts[item['kategori']] += 1

        entropy_right = 0
        for count in right_counts.values():
            if count > 0:
                p = count / right_total
                entropy_right += -p * math.log2(p)

        # Weighted entropy
        weighted_entropy = (left_total / total_data) * entropy_left + (right_total / total_data) * entropy_right

        # Information Gain
        info_gain = entropy_awal - weighted_entropy
        info_gain = round(info_gain, 3)

        # Split Information
        split_info = 0
        if left_total > 0:
            p_left = left_total / total_data
            split_info += -p_left * math.log2(p_left)
        if right_total > 0:
            p_right = right_total / total_data
            split_info += -p_right * math.log2(p_right)
        split_info = round(split_info, 3)

        # Gain Ratio
        if split_info != 0:
            gain_ratio = round(info_gain / split_info, 3)
        else:
            gain_ratio = 0

        split_info_gain_tambahan2.append({
            'split_point': split,
            'information_gain': info_gain,
            'split_information': split_info,
            'gain_ratio': gain_ratio,
        })


    # Mencari split point dengan gain ratio tertinggi
    best_split_tambahan2 = max(split_info_gain_tambahan2, key=lambda x: x['gain_ratio'])

    # Setelah best_split_tambahan2 dan best_split_tahunan dihitung
    request.session['best_split_tahunan'] = best_split_tahunan['split_point']  
    request.session['best_split_tambahan2'] = best_split_tambahan2['split_point']

    context = {
        'data': data,
        'data_jenis': data_jenis,
        'data_tambahan_x2': data_tambahan_x2,
        'data_tahunan_x2': data_tahunan_x2,
        'kategori_counts': kategori_counts,
        'total_data': total_data,
        'entropy_awal': entropy,
        'split_info_gain_tambahan': split_info_gain_tambahan,
        'split_info_gain_tahunan': split_info_gain_tahunan,
        'best_split_tambahan' : best_split_tambahan, 
        'best_split_tahunan' : best_split_tahunan,
        'entropy_filtered' : entropy_filtered,
        'filtered_data_tambahan': filtered_data_tambahan,
        'split_info_gain_tambahan2': split_info_gain_tambahan2,
        'best_split_tambahan2': best_split_tambahan2,
    }

    return render(request, 'decision_tree.html', context)

# Fungsi decision tree
def hasil_dt(pu_tahunan, pu_tambahan, best_split_tahunan, best_split_tambahan2):
    # Jika PU tahunan lebih kecil atau sama dengan split point tahunan
    if pu_tahunan <= best_split_tahunan:
        return '350'
    else:
        # Jika PU tambahan lebih kecil atau sama dengan split point tambahan
        if pu_tambahan <= best_split_tambahan2:
            return '400'
        else:
            return '450'  # Jika lebih dari itu, maka butuh 450 stiker

# Halaman prediksi kebutuhan stiker
def prediksi_stiker(request):
    context = {}  
    tahun_terpilih = None  

    # Mengambil data dari model StikerTera
    data_qs = StikerTera.objects.all().values('spbu', 'nozzle', 'pu_bbm', 'jenis_layanan', 'tanggal_pengujian')
    df = pd.DataFrame(data_qs)  

    # Mengonversi kolom ke tipe datetime dan numerik
    df['tanggal_pengujian'] = pd.to_datetime(df['tanggal_pengujian'], errors='coerce')
    df['pu_bbm'] = pd.to_numeric(df['pu_bbm'], errors='coerce')

    # Menambahkan kolom 'tahun' dari tanggal pengujian
    df['tahun'] = df['tanggal_pengujian'].dt.year

    # Mencari tahun terbaru dari data
    tahun_terakhir_data = df['tahun'].max()

    # Membuat daftar range tahun 
    tahun_range = list(range(2019, tahun_terakhir_data + 2))

    # Mengirim ke template untuk pilihan dropdown tahun
    context['tahun_range'] = tahun_range 

    # Menyaring data berdasarkan jenis layanan (tahunan dan tambahan)
    df_tahunan = df[df['jenis_layanan'].str.lower() == 'tahunan']
    df_tambahan = df[df['jenis_layanan'].str.lower() == 'tambahan']

    # Menghitung total PU BBM per tahun untuk masing-masing jenis layanan
    pu_tahunan_per_tahun = df_tahunan.groupby('tahun')['pu_bbm'].sum()
    pu_tambahan_per_tahun = df_tambahan.groupby('tahun')['pu_bbm'].sum()

    if request.method == 'POST':

        # Ambil tahun dari form
        tahun_terpilih = int(request.POST.get('tahun_terpilih'))  
        context['tahun_terpilih'] = tahun_terpilih

        # Menggunakan 2 tahun sebelumnya sebagai dasar prediksi 
        tahun_dasar = tahun_terpilih - 2  

        decision_tree(request)

        # Mengambil lagi dari session
        best_split_tahunan = request.session.get('best_split_tahunan')
        best_split_tambahan2 = request.session.get('best_split_tambahan2')

        # Mengambil nilai PU dari data tahun dasar
        pu_tahunan = pu_tahunan_per_tahun.get(tahun_dasar)
        pu_tambahan = pu_tambahan_per_tahun.get(tahun_dasar)

        # Memprediksi jumlah stiker menggunakan fungsi pohon keputusan
        kebutuhan_stiker = hasil_dt(pu_tahunan, pu_tambahan, best_split_tahunan, best_split_tambahan2)

        # Menambahkan data ke konteks untuk ditampilkan di template
        context.update({
            'pu_tahunan': pu_tahunan,
            'pu_tambahan': pu_tambahan,
            'kebutuhan_stiker': kebutuhan_stiker,
            'split_point_tahunan': best_split_tahunan,
            'split_point_tambahan': best_split_tambahan2,  
        })

    # Menampilkan template prediksi
    return render(request, 'prediksi_stiker.html', context)
