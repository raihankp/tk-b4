from django.urls import path
from panitia.views import show_mulai_pertandingan
from panitia.views import show_rapat
from panitia.views import show_notula
from panitia.views import list_pertandingan
from panitia.views import add_pertandingan
from panitia.views import add_waktu_pertandingan
from panitia.views import buat_pertandingan

from panitia.views import show_manage_pertandingan, show_peristiwa_tim, show_panitia, show_pilih_peristiwa

app_name = 'panitia'

urlpatterns = [
    path('', show_panitia, name='show_panitia'),
    path('rapat/', show_rapat, name='show_rapat'),
    path('rapat/notula/<str:id_pertandingan>/', show_notula, name='show_notula'),
    
    path('pertandingan/list_pertandingan', list_pertandingan, name='list_pertandingan'),
    path('pertandingan/add_pertandingan', add_pertandingan, name='add_pertandingan'),
    path('pertandingan/add_waktu_pertandingan', add_waktu_pertandingan, name='add_waktu_pertandingan'),
    path('pertandingan/buat_pertandingan', buat_pertandingan, name='buat_pertandingan'),

    path('manage-pertandingan/', show_manage_pertandingan, name='show_manage_pertandingan'),
    path('manage-pertandingan/peristiwa-tim/<uuid:id_pertandingan>/<str:nama_tim>/', show_peristiwa_tim, name='show_peristiwa_tim'),    
    path('manage-pertandingan/mulai-pertandingan/<uuid:id_pertandingan>/', show_mulai_pertandingan, name='show_mulai_pertandingan'),
    path('manage-pertandingan/mulai-pertandingan/<uuid:id_pertandingan>/pilih-peristiwa/<str:nama_tim>/', show_pilih_peristiwa, name='show_pilih_peristiwa'),
]