from django.shortcuts import render, redirect
from landing_page.views import is_login
from utilities.helper import query
from django.http.response import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

# Create your views here.
def show_dashboard(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]

    profile_data = query(
        f"""
        SELECT N.nama_depan, N.nama_belakang, N.email, N.nomor_hp, N.alamat 
        FROM MANAJER M JOIN NON_PEMAIN N ON M.id_manajer = N.id 
        WHERE M.username = '{username}'
        """
    )

    # Mengambil data status yang dimiliki manajer
    status_data = query(
        f"""
        SELECT STRING_AGG(S.status, ', ') as stat
        FROM STATUS_NON_PEMAIN S JOIN MANAJER M ON S.id_non_pemain = M.id_manajer
        WHERE M.username = '{username}' 
        """
    )

    # Mengambil data pemain dan tim
    data_pemain = query(
        f"""
        SELECT nama_depan, nama_belakang, nomor_hp, tgl_lahir, is_captain, posisi, npm, jenjang, T.nama_tim
        FROM PEMAIN P, MANAJER M, TIM_MANAJER T 
        WHERE M.id_manajer = T.id_manajer and T.nama_tim = P.nama_tim and M.username = '{username}'
        """
    )
    
    # Mengambil data berupa nama tim yang dimiliki manajer
    tim = query(
        f"""
        SELECT nama_tim FROM TIM_MANAJER T JOIN MANAJER M ON T.id_manajer = M.id_manajer
        WHERE username = '{username}'
        """
    )

    # Mengambil data pelatih
    data_pelatih = query(
        f"""
        SELECT P.id_pelatih, nama_depan, nama_belakang, nomor_hp, email, alamat, spesialisasi
        FROM MANAJER M JOIN TIM_MANAJER T ON M.id_manajer = T.id_manajer 
        JOIN PELATIH P ON T.nama_tim = P.nama_tim JOIN NON_PEMAIN N ON P.id_pelatih = N.id
        JOIN SPESIALISASI_PELATIH S ON P.id_pelatih = S.id_pelatih
        WHERE M.username = '{username}'
        """
    )

    context = {
        'profile': profile_data[0],
        'status': status_data[0],
        'tim': tim,
        'pemain': data_pemain,
        'pelatih': data_pelatih
    }

    return render(request, 'base_manajer.html', context)

@csrf_exempt
def mengelola_tim(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    # Mengambil data manajer yang login
    username = request.session["username"]

    if request.method == 'POST':
        nama_tim = request.POST.get('tim')
        nama_univ = request.POST.get('universitas')

        # Mendaftarkan tim ke sistem dan cek jika ada pelanggaran
        register_tim = query(
            f"""
            INSERT INTO TIM VALUES ('{nama_tim}', '{nama_univ}')
            """
        )

        if type(register_tim) != int:
            return JsonResponse({'success': 'false', 'message': f'{register_tim}'.split('.')[0] + '.'}, status = 200)
        
        # Masukkan data ke tabel TIM_MANAJER dan cek jika ada pelanggaran
        id_manajer = query(
            f"""
            SELECT id_manajer FROM MANAJER WHERE username = '{username}'
            """
        )[0].id_manajer

        register_tim_manajer = query(
            f"""
            INSERT INTO TIM_MANAJER VALUES ('{id_manajer}', '{nama_tim}')
            """
        )

        if type(register_tim_manajer) != int:
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status = 200)
        else:
            return JsonResponse({'success': 'true', 'message': 'Tim berhasil didaftarkan.'}, status=200)

    else:
        # Mengambil data pemain dan tim
        data_pemain = query(
            f"""
            SELECT id_pemain, nama_depan, nama_belakang, nomor_hp, tgl_lahir, is_captain, posisi, npm, jenjang, T.nama_tim
            FROM PEMAIN P, MANAJER M, TIM_MANAJER T 
            WHERE M.id_manajer = T.id_manajer and T.nama_tim = P.nama_tim and M.username = '{username}'
            """
        )

        # Mengambil data berupa nama tim yang dimiliki manajer
        tim = query(
            f"""
            SELECT nama_tim FROM TIM_MANAJER T JOIN MANAJER M ON T.id_manajer = M.id_manajer
            WHERE username = '{username}'
            """
        )

        # Mengambil data pelatih
        data_pelatih = query(
            f"""
            SELECT P.id_pelatih, nama_depan, nama_belakang, nomor_hp, email, alamat, spesialisasi
            FROM MANAJER M JOIN TIM_MANAJER T ON M.id_manajer = T.id_manajer 
            JOIN PELATIH P ON T.nama_tim = P.nama_tim JOIN NON_PEMAIN N ON P.id_pelatih = N.id
            JOIN SPESIALISASI_PELATIH S ON P.id_pelatih = S.id_pelatih
            WHERE M.username = '{username}'
            """
        )

        context = {
            'pemain': data_pemain,
            'pelatih': data_pelatih,
            'tim': tim
        }
        
        return render(request, 'mengelola_tim.html', context)
    
@csrf_exempt
def tambah_pemain(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    username = request.session["username"]
    
    if request.method =='POST':
        pemain = request.POST.get('pemain')

        # Masukkan data pemain ke dalam tim manajer dan cek jika ada pelanggaran
        tim = query(
            f"""
            SELECT nama_tim FROM TIM_MANAJER T JOIN MANAJER M ON T.id_manajer = M.id_manajer
            WHERE username = '{username}'
            """
        )[0].nama_tim

        update_pemain = query(
            f"""
            UPDATE PEMAIN SET nama_tim = '{tim}'
            WHERE id_pemain = '{pemain}'
            """
        )

        if type(update_pemain) != int:
            return JsonResponse({'success': 'false', 'message': f'{update_pemain}'.split('.')[0] + '.'}, status = 200)
        else:
            return JsonResponse({'success': 'true', 'message': 'Berhasil menambahkan pemain.'}, status=200)
        
    else:
        # Ambil data pemain yang belom masuk ke dalam tim apapun
        get_pemain = query(
            f"""
            SELECT id_pemain, nama_depan, nama_belakang, posisi
            FROM PEMAIN
            WHERE nama_tim is NULL
            """
        )

        print(get_pemain)

        context = {
            'pemain': get_pemain
        }

        return render (request, 'tambah_pemain.html', context)

@csrf_exempt
def tambah_pelatih(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    username = request.session["username"]

    if request.method == 'POST':
        # Do something
        pelatih = request.POST.get('pelatih')

        # Masukkan data pelatih ke dalam tim manajer dan cek jika ada pelanggaran
        tim = query(
            f"""
            SELECT nama_tim FROM TIM_MANAJER T JOIN MANAJER M ON T.id_manajer = M.id_manajer
            WHERE username = '{username}'
            """
        )[0].nama_tim

        update_pelatih = query(
            f"""
            UPDATE PELATIH SET nama_tim = '{tim}'
            where id_pelatih = '{pelatih}'
            """
        )

        if type(update_pelatih) != int:
            return JsonResponse({'success': 'false', 'message':  f'{update_pelatih}'.split('.')[0] + '.'}, status = 200)
        else:
            return JsonResponse({'success': 'true', 'message': 'Berhasil menambahkan pelatih.'}, status=200)
        
    else:
        # Mengambil data pelatih yang tidak melatih tim apapun
        get_pelatih = query(
            f"""
            SELECT P.id_pelatih, N.nama_depan, N.nama_belakang, S.spesialisasi
            FROM PELATIH P JOIN SPESIALISASI_PELATIH S ON S.id_pelatih = P.id_pelatih
            JOIN NON_PEMAIN N ON N.id = P.id_pelatih
            WHERE P.nama_tim is NULL
            """
        )

        print(get_pelatih)

        context = {
            'pelatih': get_pelatih
        }

        return render (request, 'tambah_pelatih.html', context)

@csrf_exempt
def make_captain(request, id):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    query(
        f"""
        UPDATE PEMAIN SET is_captain = True WHERE id_pemain = '{id}'
        """
    )
    
    # Basically refresh page
    return redirect('/manajer/mengelola_tim')

@csrf_exempt
def delete_pemain(request, id):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    query(
        f"""
        UPDATE PEMAIN SET nama_tim = NULL WHERE id_pemain = '{id}'
        """
    )

    query(
        f"""
        UPDATE PEMAIN SET is_captain = False WHERE id_pemain = '{id}'
        """
    )
    
    # Basically refresh page
    return redirect('/manajer/mengelola_tim')

@csrf_exempt
def delete_pelatih(request, id):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    query(
        f"""
        UPDATE PELATIH SET nama_tim = Null WHERE id_pelatih = '{id}'
        """
    )

    # Basically refresh page
    return redirect('/manajer/mengelola_tim')

# disya
def peminjaman_stadium(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]

     # ambil nama stadium
    check_stadium = query(
        f"""SELECT nama, TO_CHAR(P.start_datetime, 'DD FMMonth YYYY') AS date, 
        TO_CHAR(P.start_datetime, 'HH:MI') AS start_time, TO_CHAR(P.end_datetime, 'HH:MI') AS end_time
        FROM STADIUM S, PEMINJAMAN P, MANAJER M 
        WHERE S.ID_STADIUM = P.ID_STADIUM AND M.ID_MANAJER = P.ID_MANAJER AND M.username = '{username}' 
        ORDER BY start_datetime asc;"""
    )

    context = {
        'stadium':check_stadium
    }

    return render(request, 'peminjaman_stadium.html', context)

@csrf_exempt
def pilih_stadium(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    if request.method == 'POST':

        id_stadium = request.POST.get('id')
        tanggal = request.POST.get('tanggal')
        
        return JsonResponse({'id': id_stadium, 'tanggal': tanggal}, status=200)
    
    else:
        data_stadium = query(
            f"""
            SELECT id_stadium, nama FROM STADIUM
            """
        )

        context = {
            'stadium': data_stadium
        }

        return render (request, 'pilih_stadium.html', context)

@csrf_exempt
def list_waktu_stadium(request, id, tanggal):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    username = request.session["username"]

    if request.method == 'POST':
        waktu_mulai = request.POST.get('waktu_mulai')
        waktu_akhir = request.POST.get('waktu_akhir')

        # Mengambil id_manajer yang login
        id_manajer = query(
            f"""
            SELECT id_manajer FROM MANAJER WHERE username = '{username}'
            """
        )[0].id_manajer

        # Memasukkan data peminjaman baru ke tabel PEMINJAMAN dan cek jika ada pelanggaran
        start_datetime = tanggal + " " + waktu_mulai
        end_datetime = tanggal + " " + waktu_akhir

        data_peminjaman = query(
            f"""
            INSERT INTO PEMINJAMAN VALUES(
            '{id_manajer}', '{start_datetime}', '{end_datetime}', '{id}'
            )
            """
        )

        if type(data_peminjaman) != int:
            return JsonResponse({'success': 'false', 'message': f'{data_peminjaman}'.split('!')[0] + '!'}, status=200)
        else:
            return JsonResponse({'success': 'true', 'message': 'Berhasil memesan stadium!'}, status=200)

    else:
        check_peminjaman = query(
            f"""
            SELECT start_datetime FROM PEMINJAMAN 
            WHERE CAST(start_datetime AS VARCHAR) LIKE '{tanggal}%' AND id_stadium = '{id}'
            """
        )
        context = {
            'id': id,
            'tanggal': tanggal,
        }

        # Jika udah ada 2 peminjaman suatu stadium pada tanggal yang sama, udah pasti full booked
        if len(check_peminjaman) == 2:
            context['status'] = True
            context['time'] = ""
        # Jika tidak ada peminjaman sama sekali
        elif not len(check_peminjaman):
            context['status'] = False
            context['time'] = ""
        # Jika ada satu peminjaman
        else:
            date = str(check_peminjaman[0].start_datetime).split(" ")[1]
            context['status'] = False
            context['time'] = date

        return render(request, 'list_waktu_stadium.html', context)

# end disya
def list_pertandingan(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    pertandingan = query(
        f"""
        SELECT ARRAY_AGG(TP.nama_tim) as nama_tim, S.nama as nama_stadium, TO_CHAR(P.start_datetime, 'DD FMMonth YYYY') AS date, 
        TO_CHAR(P.start_datetime, 'HH:MI') AS start_time, TO_CHAR(P.end_datetime, 'HH:MI') AS end_time
        FROM PERTANDINGAN P, STADIUM S, TIM_PERTANDINGAN TP
        WHERE TP.id_pertandingan IN (
            SELECT TP.id_pertandingan
            FROM MANAJER M, TIM_MANAJER TM, TIM_PERTANDINGAN TP
            WHERE M.username = '{username}' AND M.id_manajer = TM.id_manajer AND TM.nama_tim = TP.nama_tim
        ) AND TP.id_pertandingan = P.id_pertandingan AND P.stadium = S.id_stadium
        GROUP BY P.id_pertandingan, S.nama, P.start_datetime, P.end_datetime;
        """
    )
    
    context = {
        'pertandingan': pertandingan
    }
    
    return render(request, 'list_pertandingan_manajer.html', context)

def history_rapat(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    rapat = query(
        f"""
        SELECT DISTINCT T.nama_tim as nama_tim, P.username, N.nama_depan, N.nama_belakang, TO_CHAR(R.datetime, 'DD FMMonth YYYY') AS date, 
        TO_CHAR(R.datetime, 'HH:MI') AS start_time, S.nama as nama_stadium, R.datetime, R.perwakilan_panitia, R.manajer_tim_b, R.manajer_tim_a
        FROM Tim_Pertandingan T, Panitia P, Stadium S, Pertandingan X, Rapat R, Non_Pemain N, Manajer M, Tim_Manajer TM
        WHERE (R.manajer_tim_b = M.id_manajer OR R.manajer_tim_a = M.id_manajer) AND M.id_manajer = TM.id_manajer AND TM.nama_tim = T.nama_tim AND M.username = '{username}' AND R.id_pertandingan = X.id_pertandingan AND T.ID_Pertandingan = X.ID_Pertandingan
        AND S.id_stadium = X.stadium AND R.perwakilan_panitia = P.id_panitia AND P.id_panitia = N.id
        ORDER BY R.datetime asc;
        """
    )
    
    context = {
        'rapat': rapat,
    }
    
    return render(request, 'history_rapat.html', context)

def laporan_rapat(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]
    
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    perwakilan_panitia = request.GET.get('perwakilan_panitia')
    manajer_tim_a = request.GET.get('manajer_tim_a')
    manajer_tim_b = request.GET.get('manajer_tim_b')
    
    # masih salah nyamain datetimenya
    laporan = query(
        f"""
        SELECT R.isi_rapat, ARRAY_AGG(TP.nama_tim) as tim
        FROM RAPAT R, TIM_PERTANDINGAN TP
        WHERE TO_CHAR(R.datetime, 'DD FMMonth YYYY') = '{date}' AND TO_CHAR(R.datetime, 'HH:MI') = '{start_time}' AND R.perwakilan_panitia = '{perwakilan_panitia}' AND R.manajer_tim_a = '{manajer_tim_a}' AND R.manajer_tim_b = '{manajer_tim_b}'
        AND TP.id_pertandingan = R.id_pertandingan
        GROUP BY R.isi_rapat;
        """
    )
    
    context = {
        'laporan': laporan,
    }
    
    return render(request, 'laporan_rapat.html', context)


