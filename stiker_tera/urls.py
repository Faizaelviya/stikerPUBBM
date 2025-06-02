from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('spbu_app.urls')),  # arahkan ke urls di app
    path('admin/', admin.site.urls),
]
