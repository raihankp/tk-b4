from django.db import IntegrityError
from django.shortcuts import render, redirect
from landing_page.views import is_login
from utilities.helper import query
from django.utils.crypto import get_random_string
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse

# Create your views here.
def show_penonton(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data panitia yang login
    username = request.session["username"]

    data_penonton = query(
        f"""
        SELECT N.nama_depan, N.nama_belakang, N.email, N.nomor_hp, N.alamat
        FROM NON_PEMAIN N JOIN PENONTON P ON P.id_penonton = N.id
        WHERE P.username = '{username}'
        """
    )

    # Mengambil data status panitia
    status_penonton = query(
        f"""
        SELECT STRING_AGG(S.status, ', ') as stat
        FROM STATUS_NON_PEMAIN S JOIN PENONTON P ON S.id_non_pemain = P.id_penonton
        WHERE P.username = '{username}' 
        """
    )

    """
    Note: 
    Bakal menampilkan pertandingan yang akan datang dan penonton membeli tiket dari pertandingan tersebut
    """
    data_upcoming_matches = query(
    f"""
        SELECT ARRAY_AGG(TP.nama_tim) as tim, S.nama as nama_stadium, TO_CHAR(P.start_datetime, 'DD FMMonth YYYY') AS date, 
        TO_CHAR(P.start_datetime, 'HH:MI') AS start_time, TO_CHAR(P.end_datetime, 'HH:MI') AS end_time
        FROM PERTANDINGAN P 
        JOIN STADIUM S ON P.stadium = S.id_stadium 
        JOIN TIM_PERTANDINGAN TP ON P.id_pertandingan = TP.id_pertandingan 
        JOIN PEMBELIAN_TIKET PT ON PT.id_pertandingan = P.id_pertandingan 
        JOIN PENONTON O ON PT.id_penonton = O.id_penonton
        WHERE O.username = '{username}'
        GROUP BY S.nama, P.start_datetime, P.end_datetime 
        ORDER BY P.start_datetime ASC;
        """
    )

    context = {
        'profile': data_penonton[0],
        'status': status_penonton[0],
        'pertandingan': data_upcoming_matches
    }

    return render(request, 'base_penonton.html', context)

def show_list_pertandingan_penonton(request):
    
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    pertandingan = query(
        f"""
        SELECT ARRAY_AGG(TP.nama_tim) as tim, S.nama as nama_stadium, TO_CHAR(P.start_datetime, 'DD FMMonth YYYY') AS date, 
        TO_CHAR(P.start_datetime, 'HH:MI') AS start_time, TO_CHAR(P.end_datetime, 'HH:MI') AS end_time
        FROM PERTANDINGAN P, STADIUM S, TIM_PERTANDINGAN TP
        WHERE P.id_pertandingan = TP.id_pertandingan AND P.stadium = S.id_stadium
        GROUP BY S.nama, P.start_datetime, P.end_datetime, P.id_pertandingan
        ORDER BY P.start_datetime ASC;
        """
    )
    
    context = {
        'pertandingan': pertandingan
    }
    
    return render(request, 'list_pertandingan_penonton.html', context)

def show_pembelian_tiket(request):
    
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    stadium = query(
        f"""
        SELECT S.nama as nama, S.id_stadium as id
        FROM Stadium S;
        """
    )
    
    context = {
        'stadium': stadium,
    }
    
    return render(request, 'pembelian_tiket.html', context)

def show_pilih_waktu(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    if request.method == 'POST':
        nama_stadium = request.POST.get('stadium')
        tanggal = request.POST.get('tanggal')
    
    print(nama_stadium)
    print(tanggal)
    
    waktu = query(
        f"""
        SELECT ARRAY_AGG(TP.nama_tim) as tim, P.ID_pertandingan as id_pertandingan, TO_CHAR(P.start_datetime, 'HH:MI') AS start_time, TO_CHAR(P.end_datetime, 'HH:MI') AS end_time
        FROM Pertandingan P, Stadium S, Tim_Pertandingan TP
        WHERE S.nama = '{nama_stadium}' AND S.id_stadium = P.stadium AND TO_CHAR(P.start_datetime, 'YYYY-MM-DD') = '{tanggal}' 
        AND P.id_pertandingan = TP.id_pertandingan
        GROUP BY S.nama, P.start_datetime, P.end_datetime, P.ID_pertandingan
        ORDER BY P.start_datetime ASC;;
        """
    )
    
    context = {
        'waktu': waktu,
        'stadium_nama' : nama_stadium
    }
    
    return render(request, 'pilih_waktu.html', context)

def show_beli_tiket(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    if request.method == 'POST':
        id_pertandingan = request.GET.get('id')
        jenis_tiket = request.POST.get('jenis_tiket')
        jenis_pembayaran = request.POST.get('jenis_pembayaran')
        nomor_receipt = generate_receipt()
        print(jenis_tiket)
        print(jenis_pembayaran)
        
        id_penonton = query(
            f"""
            SELECT DISTINCT P.id_penonton as id
            FROM PENONTON P
            WHERE P.username = '{username}';
            """
        )
        # Insert data ke tabel USER_SYSTEM dan cek jika ada pelanggaran
        for penonton in id_penonton:
            membeli_tiket = query(
                f"INSERT INTO PEMBELIAN_TIKET (nomor_receipt, id_penonton, jenis_tiket, jenis_pembayaran, id_pertandingan) VALUES ('{nomor_receipt}', '{penonton.id}', '{jenis_tiket}', '{jenis_pembayaran}', '{id_pertandingan}')"
        )
            if type(membeli_tiket) != int:
                return JsonResponse({'success': 'false', 'message': f'{membeli_tiket}'.split('!')[0] + "!"}, status=200)

        return JsonResponse({'success': 'true', 'message': 'Berhasil membeli tiket!'}, status=200)
    
    else:
        id = request.GET.get('id')
        
        print(id)
    
        context = {
            'username' : username,
            'id_pertandingan': id,
        }

        return render(request, 'beli_tiket.html', context)
                 
def generate_receipt():
    nomor_receipt = get_random_string(length=4, allowed_chars='0123456789')
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM PEMBELIAN_TIKET WHERE nomor_receipt = %s", [nomor_receipt])
        count = cursor.fetchone()[0]
        if count > 0:
            return generate_receipt()
    return nomor_receipt