from django.urls import path
from penonton.views import *

app_name = 'penonton'

urlpatterns = [
    path('', show_penonton, name='show_penonton'),
    path('list_pertandingan/', show_list_pertandingan_penonton, name='list_pertandingan'),
    path('show_pembelian_tiket/', show_pembelian_tiket, name='show_pembelian_tiket'),
    path('show_pembelian_tiket/pilih_waktu', show_pilih_waktu, name='show_pilih_waktu'),
    path('show_pembelian_tiket/beli_tiket', show_beli_tiket, name='show_beli_tiket'),
]