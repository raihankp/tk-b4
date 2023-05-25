import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from landing_page.views import is_login
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query

# Create your views here.
def show_panitia(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data panitia yang login
    username = request.session["username"]

    data_panitia = query(
        f"""
        SELECT N.nama_depan, N.nama_belakang, N.email, N.nomor_hp, P.jabatan, N.alamat
        FROM NON_PEMAIN N JOIN PANITIA P ON P.id_panitia = N.id
        WHERE P.username = '{username}'
        """
    )

    # Mengambil data status panitia
    status_panitia = query(
        f"""
        SELECT STRING_AGG(S.status, ', ') as stat
        FROM STATUS_NON_PEMAIN S JOIN PANITIA P ON S.id_non_pemain = P.id_panitia
        WHERE P.username = '{username}' 
        """
    )

    """
    Note: 
    Rapat yang akan datang itu basically sama kayak pertandingan yang akan datang, tapi data pertandingannya belom terdaftar
    di tabel rapat
    """
    data_upcoming_rapat = query(
    f"""
    SELECT STRING_AGG(T.nama_tim, ' vs ') as tim, S.nama, P.start_datetime, P.end_datetime
    FROM PERTANDINGAN P JOIN STADIUM S ON P.stadium = S.id_stadium JOIN TIM_PERTANDINGAN T ON P.id_pertandingan = T.id_pertandingan
    WHERE P.id_pertandingan NOT IN (SELECT id_pertandingan FROM RAPAT)
    GROUP BY S.nama, P.start_datetime, P.end_datetime 
    ORDER BY P.start_datetime ASC;
    """
    )

    context = {
        'profile': data_panitia[0],
        'status': status_panitia[0],
        'rapat': data_upcoming_rapat
    }

    return render(request, 'base_panitia.html', context)

# disya start
def show_rapat(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')

    # Mengambil data manajer yang login
    username = request.session["username"]


    rapat = query(    
        f"""
        SELECT p.id_pertandingan, ARRAY_AGG(tp.nama_tim) as tim, s.nama, p.start_datetime
        FROM pertandingan p , tim_pertandingan tp, stadium s, rapat r
        WHERE p.id_pertandingan = tp.id_pertandingan
        and p.id_pertandingan = r.id_pertandingan
        and s.id_stadium = p.stadium 
        and r.isi_rapat = ''
        GROUP BY p.id_pertandingan, s.nama, p.start_datetime
        ORDER BY p.start_datetime asc;
        """
    )

    print(rapat)

    context = {
        'rapat':rapat
    }

    return render(request, 'rapat_panitia.html', context)

@csrf_exempt
def show_notula(request, id_pertandingan):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    username = request.session["username"]

    if request.method =='POST':
        notula = request.POST.get('notulaRapat')

        query(
            f"""
            UPDATE RAPAT 
            SET isi_rapat = '{notula}'
            WHERE id_pertandingan = '{id_pertandingan}' 
            """
        )

        return redirect("/panitia/rapat")

    else:
        judul = query(
            f"""
            SELECT id_pertandingan, ARRAY_AGG(nama_tim) as tim
            FROM tim_pertandingan
            WHERE id_pertandingan = '{id_pertandingan}'
            group by id_pertandingan;
            """
    )

    context = {
        'judul': judul
    }

    return render(request, 'notula_panitia.html', context)

    # disya sampe simi

def list_pertandingan(request):
    return render(request, 'list_pertandingan.html')

def add_pertandingan(request):
    return render(request, 'add_pertandingan.html')

def add_waktu_pertandingan(request):
    return render(request, 'add_waktu_pertandingan.html')

def buat_pertandingan(request):
    return render(request, 'buat_pertandingan.html')

def show_manage_pertandingan(request):
    # Validasi user
    if not is_login(request):
        return redirect('/')
    
    pertandingan = query(
        f"""
        SELECT pertandingan.id_pertandingan, ARRAY_AGG(tim_pertandingan.nama_tim) as tim, start_datetime, end_datetime
        FROM pertandingan, tim_pertandingan
        WHERE pertandingan.id_pertandingan=tim_pertandingan.id_pertandingan
        GROUP BY pertandingan.id_pertandingan
        ORDER BY start_datetime asc;
        """
    )

    pemenang = {}
    for p in pertandingan:    
        pemenangQuery = query(
            f"""
            SELECT nama_tim, skor
            FROM tim_pertandingan
            WHERE id_pertandingan='{p.id_pertandingan}';
            """
        )

        if pemenangQuery[0].skor == '' and pemenangQuery[1].skor == '':
            pemenang[p.id_pertandingan] = "-"
        elif pemenangQuery[0].skor > pemenangQuery[1].skor:
            pemenang[p.id_pertandingan] = pemenangQuery[0].nama_tim
        elif pemenangQuery[0].skor < pemenangQuery[1].skor:
            pemenang[p.id_pertandingan] = pemenangQuery[1].nama_tim
        else:
            pemenang[p.id_pertandingan] = "SERI"

        peristiwa = query(
            f"""
            select count(*) as jumlah 
            from peristiwa 
            where id_pertandingan='{p.id_pertandingan}' 
            group by id_pertandingan;
            """
        )



    jumlahPertandingan = query(
        f"""
        select count(*) as jumlah_pertandingan from pertandingan;
        """
    )

    
    context = {
        'pertandingan': pertandingan,
        'pemenang': pemenang,
        'jumlahPertandingan': jumlahPertandingan[0].jumlah_pertandingan,
    }

    return render(request, 'manage_pertandingan.html', context)

def show_peristiwa_tim(request, id_pertandingan, nama_tim):

    peristiwa = query(
        f"""
        SELECT datetime, jenis, pemain.id_pemain, nama_depan, nama_belakang
        FROM peristiwa, pemain
        WHERE peristiwa.id_pemain=pemain.id_pemain
        AND peristiwa.id_pertandingan='{id_pertandingan}'
        AND nama_tim='{nama_tim}';
        """
    )

    context = {
        'peristiwa': peristiwa,
        'nama_tim': nama_tim
    }

    return render(request, 'peristiwa_tim.html', context)

def show_mulai_pertandingan(request, id_pertandingan):
    data = query(
        f"""
        SELECT ARRAY_AGG(nama_tim) as nama_tim, id_pertandingan
        FROM tim_pertandingan
        WHERE id_pertandingan='{id_pertandingan}'
        GROUP BY id_pertandingan;
        """
    )

    context = {
        "data": data[0]
    }
    return render(request, 'mulai_pertandingan.html', context)

@csrf_exempt
def show_pilih_peristiwa(request, id_pertandingan, nama_tim):
    if request.method == "POST":
        # Do Something
        pemain1 = request.POST.get('pemain1') 
        pemain2 = request.POST.get('pemain2')
        pemain3 = request.POST.get('pemain3') 
        pemain4 = request.POST.get('pemain4')
        pemain5 = request.POST.get('pemain5')  
        peristiwa1 = request.POST.get('peristiwa1') 
        peristiwa2 = request.POST.get('peristiwa2') 
        peristiwa3 = request.POST.get('peristiwa3') 
        peristiwa4 = request.POST.get('peristiwa4') 
        peristiwa5 = request.POST.get('peristiwa5')
        waktu1 = str(request.POST.get('waktu1')).replace("T", " ") + ":00"
        waktu2 = str(request.POST.get('waktu2')).replace("T", " ") + ":00"
        waktu3 = str(request.POST.get('waktu3')).replace("T", " ") + ":00"
        waktu4 = str(request.POST.get('waktu4')).replace("T", " ") + ":00"
        waktu5 = str(request.POST.get('waktu5')).replace("T", " ") + ":00"
        peristiwa = [[pemain1, peristiwa1, waktu1], [pemain2, peristiwa2, waktu2], [pemain3, peristiwa3, waktu3], [pemain4, peristiwa4, waktu4], [pemain5, peristiwa5, waktu5]]

        print(peristiwa)

        for data in peristiwa:
            # Check null: Jika ada satu baris yang isinya kosong/ada kolom dalam satu baris yang kosong, tidak perlu menjalankan query
            if data[0] == 0 or data[1] == 0 or len(data[2]) < 19:
                continue
            else:
                # Format Insert: id_pertandingan, datetime, jenis, id_pemain
                insert_data = query(
                    f"""
                    INSERT INTO peristiwa VALUES(
                    '{id_pertandingan}', '{data[2]}', '{data[1]}', '{data[0]}'
                    );
                    """
                ) 

        if type(insert_data) != int  :
            return JsonResponse({'success': 'false', 'message': 'Something is wrong'}, status = 200)
        else:
            return JsonResponse({'success': 'true', 'message': 'Berhasil menyimpan peristiwa.'}, status=200)        
    else:
        data = query(
            f"""
            SELECT pertandingan.id_pertandingan, tim_pertandingan.nama_tim, JSON_AGG(JSON_BUILD_ARRAY(id_pemain, pemain.nama_depan, pemain.nama_belakang)) as nama_pemain
            FROM pertandingan, tim_pertandingan, pemain
            WHERE pertandingan.id_pertandingan=tim_pertandingan.id_pertandingan
            AND tim_pertandingan.nama_tim=pemain.nama_tim
            AND pertandingan.id_pertandingan='{id_pertandingan}'
            AND tim_pertandingan.nama_tim='{nama_tim}'
            GROUP BY pertandingan.id_pertandingan, tim_pertandingan.nama_tim;
            """
        )

        context = {
            'data': data[0]
        }
        return render(request, 'pilih_peristiwa.html',context)
