from django.urls import path
from . import views

urlpatterns = [
    # URL untuk halaman utama atau dashboard
    path('', views.dashboard, name='dashboard'),  

    # URL untuk input data baru stiker tera
    path('input/', views.input_data, name='input_data'),  

    # URL untuk prediksi kebutuhan stiker berdasarkan tahun
    path('prediksi/', views.prediksi_stiker, name='prediksi_stiker'),  

    # URL untuk melihat dan mengoreksi data yang sudah diinput
    path('koreksi/', views.koreksi_data, name='koreksi_data'),  

    # URL untuk menambah data SPBU baru jika tidak ada di pilihan
    path('hasil-tambah/', views.tambah_spbu, name='hasil_tambah'),  

    # URL untuk mengedit data berdasarkan ID
    path('edit/<int:data_id>/', views.edit_data, name='edit_data'),  

    # URL untuk memeriksa nama SPBU
    path('cek-nama-spbu/', views.cek_nama_spbu, name='cek_nama_spbu'),  

    # URL untuk memeriksa perhitungan decision tree
    path('decision_tree/', views.decision_tree, name='pu_bbm_per_tahun'),

]
