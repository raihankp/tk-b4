from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query
from django.http.response import JsonResponse
import uuid

# Create your views here.
def loginregister(request):
    return render(request, 'loginregister.html')

def main_register(request):
    return render(request, 'main_register.html')

def get_role(username, password):
    # Check apakah terdaftar di USER_SYSTEM
    check_user = query(
        f"""
        SELECT username FROM USER_SYSTEM WHERE username = '{username}' and password = '{password}'
        """
    )

    if len(check_user) != 0:
        # Check apakah merupakan manajer. Jika terdaftar, maka akan mengembalikan list yang berisikan namedtuple
        check_manajer = query(
            f"SELECT username FROM MANAJER where username = '{username}'"
        ) 
        if len(check_manajer) != 0:
            return "manajer" 
    
        # Check apakah merupakan panitia
        check_panitia = query(
            f"SELECT username FROM PANITIA where username = '{username}'"
        )
        if len(check_panitia) != 0:
            return "panitia" 

        # Check apakah merupakan penonton
        check_penonton = query(
            f"SELECT username FROM PENONTON where username = '{username}'"
        )
        if len(check_penonton) != 0:
            return "penonton"

    else: # Kalau tidak terdaftar sebagai salah satu dari ketiganya
        return "" 

def is_login(request):
    if "username" in request.session: # Jika ada data username yang disimpan di session, berartisedang login
        return True
    else:
        return False

@csrf_exempt
def login(request):
    if request.method == 'POST':
        if is_login(request): # Hapus session sebelumnya (just in case)
            request.session.flush()
            request.session.clear_expired()

        username = request.POST.get('username')
        password = request.POST.get('password')
        role = get_role(username, password)

        if role == '':
            return JsonResponse({'success': 'false', 'message': "Username atau password salah."}, status=200)

        else:
            # Set session untuk user yang melakukan login
            request.session['username'] = username
            request.session['password'] = password
            request.session['role'] = role
            request.session.set_expiry(0) # Supaya session-nya baru habis ketika web di-close
            request.session.modified = True
            return JsonResponse({'success': 'true', 'message': 'Berhasil Login!', 'role': role}, status=200)

    return render(request, 'login.html')

def logout(request):
    if not is_login(request):
        return redirect('/') # Ke halaman Login-Register lagi
    
    # Hapus session
    request.session.flush()
    request.session.clear_expired()
    return redirect('/')

@csrf_exempt
def register_manajer(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        nomor_hp = request.POST.get('nomor_hp')
        email = request.POST.get('email')
        alamat = request.POST.get('alamat')

        # Mengambil data status dari user yang registrasi
        list_of_status = [
            request.POST.get('mahasiswa'),
            request.POST.get('dosen'),
            request.POST.get('tendik'),
            request.POST.get('alumni'),
            request.POST.get('umum'),
        ]
        filtered_list = list(filter(None, list_of_status))

        # Insert data ke tabel USER_SYSTEM dan cek jika ada pelanggaran
        register_user = query(
            f"INSERT INTO USER_SYSTEM VALUES ('{username}', '{password}')"
        )
        if type(register_user) != int:
            return JsonResponse({'success': 'false','message': f'{register_user}'.split('!')[0] + "!"}, status = 200)

        # Insert data ke tabel NON_PEMAIN dan cek jika ada pelanggaran
        id_non_pemain = str(uuid.uuid4()) # Generate unique UUID for user
        register_non_pemain = query(
            f"""INSERT INTO NON_PEMAIN VALUES ('{id_non_pemain}', '{nama_depan}', 
            '{nama_belakang}', '{nomor_hp}', '{email}', '{alamat}')"""
        )
        if type(register_non_pemain) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        
        # Insert data status NON_PEMAIN dan cek jika ada pelanggaran
        for item in filtered_list:
            insert_status = query(
                f"""
                INSERT INTO STATUS_NON_PEMAIN VALUES ('{id_non_pemain}', '{item}')
                """
            )
            if type(insert_status) != int:
                return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)

        # Insert data ke tabel MANAJER dan cek jika ada pelanggaran
        register_manajer = query(
            f"INSERT INTO MANAJER VALUES ('{id_non_pemain}', '{username}')"
        )
        if type(register_manajer) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        else:
            return JsonResponse({'success': 'true','message': 'Succesfully Registered!'}, status=200)

    return render(request, 'register_manajer.html')

@csrf_exempt
def register_panitia(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        nomor_hp = request.POST.get('nomor_hp')
        email = request.POST.get('email')
        alamat = request.POST.get('alamat')
        jabatan = request.POST.get('jabatan')

        # Mengambil data status dari user yang registrasi
        list_of_status = [
            request.POST.get('mahasiswa'),
            request.POST.get('dosen'),
            request.POST.get('tendik'),
            request.POST.get('alumni'),
            request.POST.get('umum'),
        ]
        filtered_list = list(filter(None, list_of_status))

        # Insert data ke tabel USER_SYSTEM dan cek jika ada pelanggaran
        register_user = query(
            f"INSERT INTO USER_SYSTEM VALUES ('{username}', '{password}')"
        )
        if type(register_user) != int:
            return JsonResponse({'success': 'false','message': f'{register_user}'.split('!')[0] + "!"}, status = 200)

        # Insert data ke tabel NON_PEMAIN dan cek jika ada pelanggaran
        id_non_pemain = str(uuid.uuid4()) # Generate unique UUID for user
        register_non_pemain = query(
            f"""INSERT INTO NON_PEMAIN VALUES ('{id_non_pemain}', '{nama_depan}', 
            '{nama_belakang}', '{nomor_hp}', '{email}', '{alamat}')"""
        )
        if type(register_non_pemain) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        
        # Insert data status NON_PEMAIN dan cek jika ada pelanggaran
        for item in filtered_list:
            insert_status = query(
                f"""
                INSERT INTO STATUS_NON_PEMAIN VALUES ('{id_non_pemain}', '{item}')
                """
            )
            if type(insert_status) != int:
                return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)

        # Insert data ke tabel PANITIA dan cek jika ada pelanggaran
        register_panitia = query(
            f"INSERT INTO PANITIA VALUES ('{id_non_pemain}', '{jabatan}','{username}')"
        )
        if type(register_panitia) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        else:
            return JsonResponse({'success': 'true','message': 'Succesfully Registered!'}, status=200)
        
    return render(request, 'register_panitia.html')

@csrf_exempt
def register_penonton(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        nomor_hp = request.POST.get('nomor_hp')
        email = request.POST.get('email')
        alamat = request.POST.get('alamat')

        # Mengambil data status dari user yang registrasi
        list_of_status = [
            request.POST.get('mahasiswa'),
            request.POST.get('dosen'),
            request.POST.get('tendik'),
            request.POST.get('alumni'),
            request.POST.get('umum'),
        ]
        filtered_list = list(filter(None, list_of_status))

        # Insert data ke tabel USER_SYSTEM dan cek jika ada pelanggaran
        register_user = query(
            f"INSERT INTO USER_SYSTEM VALUES ('{username}', '{password}')"
        )
        if type(register_user) != int:
            return JsonResponse({'success': 'false','message': f'{register_user}'.split('!')[0] + "!"}, status = 200)

        # Insert data ke tabel NON_PEMAIN dan cek jika ada pelanggaran
        id_non_pemain = str(uuid.uuid4()) # Generate unique UUID for user
        register_non_pemain = query(
            f"""INSERT INTO NON_PEMAIN VALUES ('{id_non_pemain}', '{nama_depan}', 
            '{nama_belakang}', '{nomor_hp}', '{email}', '{alamat}')"""
        )
        if type(register_non_pemain) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        
        # Insert data status NON_PEMAIN dan cek jika ada pelanggaran
        for item in filtered_list:
            insert_status = query(
                f"""
                INSERT INTO STATUS_NON_PEMAIN VALUES ('{id_non_pemain}', '{item}')
                """
            )
            if type(insert_status) != int:
                return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)

        # Insert data ke tabel PENONTON dan cek jika ada pelanggaran
        register_penonton = query(
            f"INSERT INTO PENONTON VALUES ('{id_non_pemain}', '{username}')"
        )
        if type(register_penonton) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status=200)
        else:
            return JsonResponse({'success': 'true','message': 'Succesfully Registered!'}, status=200)
        
    return render(request, 'register_penonton.html')


