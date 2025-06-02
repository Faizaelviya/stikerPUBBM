from django.apps import AppConfig 

class SpbuAppConfig(AppConfig):
    # Menentukan tipe field otomatis untuk ID model
    default_auto_field = 'django.db.models.BigAutoField'  
    # Menentukan nama aplikasi ini
    name = 'spbu_app'  
