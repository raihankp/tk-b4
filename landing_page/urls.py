from django.urls import path
from landing_page.views import register_penonton
from landing_page.views import register_panitia
from landing_page.views import register_manajer
from landing_page.views import login
from landing_page.views import loginregister
from landing_page.views import main_register
from landing_page.views import logout

app_name = 'landing_page'

urlpatterns = [
    path('', loginregister, name='loginregister'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register_manajer/', register_manajer, name='register_manajer'),
    path('register_panitia/', register_panitia, name='register_panitia'),
    path('register_penonton/', register_penonton, name='register_penonton'),
    path('main_register/', main_register, name='main_register'),
]