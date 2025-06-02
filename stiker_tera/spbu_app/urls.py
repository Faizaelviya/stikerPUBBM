from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Halaman utama/dashboard

    # Input data baru stiker tera
    path('input/', views.input_data, name='input_data'),

    # Prediksi kebutuhan stiker berdasarkan tahun
    path('prediksi/', views.prediksi_stiker, name='prediksi_stiker'),

    # Lihat dan koreksi data yang sudah diinput
    path('koreksi/', views.koreksi_data, name='koreksi_data'),

    # Tambah data SPBU baru jika tidak ada di pilihan
    path('tambah-spbu/', views.tambah_spbu, name='tambah_spbu'),

    # Edit data berdasarkan ID
    path('edit/<int:data_id>/', views.edit_data, name='edit_data'),
]
