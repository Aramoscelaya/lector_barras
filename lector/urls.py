from django.urls import path
from .views import camera_reader

urlpatterns = [
   #path('', barcode_reader, name='barcode_reader'),
   path('', camera_reader, name='camera_reader'),
]
