from django.urls import path
from manajer.views import *

app_name = 'manajer'

urlpatterns = [
    path('', show_dashboard, name='show_manajer'),
    path('mengelola_tim/', mengelola_tim, name='mengelola_tim'),
    path('peminjaman_stadium/', peminjaman_stadium, name='peminjaman_stadium'),
    path('list_pertandingan/', list_pertandingan, name='list_pertandingan'),
    path('history_rapat/', history_rapat, name='history_rapat'),
    path('laporan_rapat/', laporan_rapat, name='laporan_rapat'),
    path('mengelola_tim/tambah_pemain', tambah_pemain, name='tambah_pemain'),
    path('mengelola_tim/tambah_pelatih', tambah_pelatih, name='tambah_pelatih'),
    path('mengelola_tim/make_captain/<str:id>/', make_captain, name='make_captain'),
    path('mengelola_tim/delete_pemain/<str:id>/', delete_pemain, name='delete_pemain'),
    path('mengelola_tim/delete_pelatih/<str:id>/', delete_pelatih, name='delete_pelatih'),
    path('peminjaman_stadium/pilih_stadium/', pilih_stadium, name='pilih_stadium'),
    path('peminjaman_stadium/pilih_stadium/<str:id>/<str:tanggal>/', list_waktu_stadium, name='list_waktu_stadium'),
]