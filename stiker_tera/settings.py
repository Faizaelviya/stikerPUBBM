"""
Django settings untuk proyek stiker_tera.

Dihasilkan oleh 'django-admin startproject' menggunakan Django 4.2.20.

Untuk informasi lebih lanjut tentang file ini, lihat:
https://docs.djangoproject.com/en/4.2/topics/settings/

Untuk daftar lengkap pengaturan dan nilainya, lihat:
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# BASE_DIR mendefinisikan direktori dasar proyek
BASE_DIR = Path(__file__).resolve().parent.parent


# PERINGATAN KEAMANAN: simpan kunci rahasia yang digunakan di produksi dengan aman!
SECRET_KEY = 'django-insecure-$%rgkn6h2xno*d-&txxfj1zau(ha)_ekmg1_fl9aau2(!z%+u8'

# PERINGATAN KEAMANAN: jangan jalankan dengan debug aktif di produksi!
DEBUG = True

# Daftar host yang diizinkan untuk proyek Django ini; untuk produksi, ini tidak boleh kosong
ALLOWED_HOSTS = []


# Definisi aplikasi

INSTALLED_APPS = [
    # Aplikasi inti Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplikasi kustom
    'spbu_app',  # Aplikasi Anda sendiri
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Menangani middleware terkait keamanan
    'django.contrib.sessions.middleware.SessionMiddleware',  # Menangani manajemen sesi
    'django.middleware.common.CommonMiddleware',  # Menyediakan fungsionalitas umum untuk tampilan
    'django.middleware.csrf.CsrfViewMiddleware',  # Melindungi terhadap serangan Cross-Site Request Forgery (CSRF)
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Menyediakan informasi autentikasi pengguna
    'django.contrib.messages.middleware.MessageMiddleware',  # Menangani pesan untuk pengguna
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Mencegah serangan clickjacking
]

ROOT_URLCONF = 'stiker_tera.urls'  # Menunjukkan konfigurasi URL utama untuk proyek ini

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Mesin template yang digunakan
        'DIRS': [BASE_DIR / 'templates'],  # Menambahkan direktori templates ke dalam daftar direktori
        'APP_DIRS': True,  # Memungkinkan pencarian file template di dalam direktori aplikasi
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # Menyediakan informasi debugging dalam template
                'django.template.context_processors.request',  # Menyediakan informasi permintaan dalam template
                'django.contrib.auth.context_processors.auth',  # Menyediakan informasi autentikasi pengguna dalam template
                'django.contrib.messages.context_processors.messages',  # Menyediakan pesan dalam template
            ],
        },
    },
]

WSGI_APPLICATION = 'stiker_tera.wsgi.application'  # Menunjukkan aplikasi WSGI untuk proyek ini


# Konfigurasi Database
# Ini adalah konfigurasi default untuk menggunakan SQLite, yang cocok untuk pengembangan.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Mesin database SQLite
        'NAME': BASE_DIR / 'db.sqlite3',  # Path ke file database SQLite
    }
}


# Pengaturan validasi kata sandi untuk memastikan kata sandi yang kuat
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Pengaturan internasionalisasi
LANGUAGE_CODE = 'en-us'  # Kode bahasa untuk proyek ini
TIME_ZONE = 'UTC'  # Zona waktu untuk proyek ini

USE_I18N = True  # Mengaktifkan internasionalisasi
USE_TZ = True  # Mengaktifkan dukungan zona waktu


# Berkas statis (CSS, JavaScript, Gambar)
# Django akan mencari berkas statis (seperti CSS dan JavaScript) di direktori ini
STATIC_URL = '/static/'

# Menambahkan direktori tambahan tempat Django dapat menemukan berkas statis
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Menambahkan direktori "static" di root proyek
]

# Tipe kunci utama default
# Menggunakan BigAutoField sebagai tipe default untuk kunci utama pada model
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
