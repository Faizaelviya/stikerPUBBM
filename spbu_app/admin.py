from django.contrib import admin  
from .models import StikerTera, SPBU  

# Mendaftarkan model StikerTera dan SPBU ke admin panel
admin.site.register(StikerTera)  
admin.site.register(SPBU)
