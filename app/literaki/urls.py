from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('literakiapp.urls')),
]

handler404 = 'literakiapp.views.error'
handler403 = 'literakiapp.views.error'
