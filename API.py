from flask import Blueprint, jsonify, request, Flask
from models import db, User, Kades, Desa, Notification, Belanja_Camat_Kades


# Create the Flask application instance
api_token = Blueprint("API_TOKEN", __name__)
api = Blueprint("API_LOGIN", __name__)
logout = Blueprint("API_LOGOUT", __name__)
registrasi = Blueprint("API_REGISTRASI", __name__)
registrasi_desa = Blueprint("API_REGISTRASI_DESA", __name__)
notifikasi = Blueprint("API_NOTIFIKASI", __name__)
belanja = Blueprint("API_BELANJA", __name__)
daftarbelanja = Blueprint("API_DAFTAR_BELANJA", __name__)
daftarbelanjakades = Blueprint("API_DAFTAR_BELANJA_KADES", __name__)

select_user_api = Blueprint("API_USER_API", __name__)
select_desa = Blueprint("API_DESA", __name__)
select_kades = Blueprint("API_KADES", __name__)
select_notifikasi = Blueprint("API_SELECT_NOTIFIKASI", __name__)
select_notifikasi_desa = Blueprint("API_SELECT_NOTIFIKASI_desa", __name__)


delete_user = Blueprint("API_DELETE_USER", __name__)
delete_desa = Blueprint("API_DELETE_DESA", __name__)
delete_kades = Blueprint("API_DELETE_KADES", __name__)
delete_notifikasi = Blueprint("API_DELETE_NOTIFIKASI", __name__)
delete_belanja = Blueprint("API_DELETE_BELANJA", __name__)

update_user = Blueprint("API_UPDATE_USER", __name__)
update_desa = Blueprint("API_UPDATE_DESA", __name__)
update_kades = Blueprint("API_UPDATE_KADES", __name__)
update_notifikasi = Blueprint("API_UPDATE_NOTIFIKASI", __name__)
update_belanja = Blueprint("API_UPDATE_BELANJA", __name__)
changepass = Blueprint("API_UPDATE_PASSWORD", __name__)


@api.route("/api-login", methods=["POST"])
def api_login():
    email = request.form.get("email")
    password_api = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    if user is not None:
        if user.status == 1:
            if user and user.password == password_api:
                response = {
                    "message": "Login Sukses",
                    "status": "success",
                    "username": user.full_name,
                    "user_status": user.status,
                    "Desa": "tidak ada",
                    "user-id": user.id,
                    # Use a different key name here
                }
                return jsonify(response), 200

        elif user.status == 2:
            if user and user.password == password_api:
                response = {
                    "message": "Login Sukses",
                    "status": "success",
                    "username": user.full_name,
                    "user_status": user.status,
                    "Desa": "tidak ada",
                    "user-id": user.id,
                    # Use a different key name here
                }
                return jsonify(response), 200

        elif user.status == 3:
            if user and user.password == password_api:
                Desa = Kades.query.filter_by(nama_kades=user.full_name).first()
                response = {
                    "message": "Login Sukses",
                    "status": "success",
                    "username": user.full_name,
                    "user_status": user.status,
                    "Desa": Desa.Desa,
                    "user-id": user.id,
                    # Use a different key name here
                }
                return jsonify(response), 200

    # Handle the case where user.status is not 1, 2, or 3
    response = {"message": "Login failed. Invalid password.", "status": "error"}
    return jsonify(response), 401  # tambahkan pernyataan return di sini


@logout.route("/api-logout", methods=["POST"])
def api_logout():
    response = {
        "message": "Berhasil Logout..",
        "status": "success",
    }
    return jsonify(response), 200


@registrasi.route("/api-registrasi", methods=["POST"])
def api_registrasi():
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")
    status = request.form.get("status")

    # Validate required fields
    if not full_name or not email or not password or not status:
        response = {
            "message": "Full name, password, email, and status masih kosong.",
            "status": "Failed",
        }
        return jsonify(response), 400

    # Check if the email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        response = {"message": "Email sudah terdaftar.", "status": "Failed"}
        return jsonify(response), 202

    new_user = User(full_name=full_name, email=email, password=password, status=status)

    db.session.add(new_user)
    db.session.commit()

    response = {"message": "Berhasil Registrasi", "status": "success"}
    return jsonify(response), 200


@registrasi_desa.route("/api-registrasi-desa", methods=["POST"])
def api_registrasi_desa():
    nama_desa = request.form.get("nama_desa")

    # Validate required fields
    if not nama_desa:
        response = {
            "message": "Nama Desa masih kosong.",
            "status": "Failed",
        }
        return jsonify(response), 400

    # Check if the email is already registered
    existing_user = Desa.query.filter_by(nama_desa=nama_desa).first()
    if existing_user:
        response = {"message": "Nama Desa sudah terdaftar.", "status": "Failed"}
        return jsonify(response), 202

    new_desa = Desa(nama_desa=nama_desa)

    db.session.add(new_desa)
    db.session.commit()

    response = {"message": "Berhasil Mendaftar Desa", "status": "success"}
    return jsonify(response), 200


@notifikasi.route("/api-notifikasi", methods=["POST"])
def api_notifikasi():
    nama_desa = request.form.get("nama_desa")
    pesan = request.form.get("pesan")

    namadesa = Desa.query.filter_by(id_desa=nama_desa).first()

    if not nama_desa or not pesan:
        response = {
            "message": "Nama Desa masih kosong atau Pesan masih kosong",
            "status": "Failed",
        }
        return jsonify(response), 400

    new_notifikasi = Notification(pesan=pesan, desa=namadesa.nama_desa)

    db.session.add(new_notifikasi)
    db.session.commit()

    response = {"message": "Berhasil membuat Notifikasi", "status": "success"}
    return jsonify(response), 200


@belanja.route("/api-belanja", methods=["POST"])
def api_belanja():
    nama_barang = request.form.get("nama_barang")
    jumlah = int(request.form.get("jumlah"))
    harga_satuan = int(request.form.get("harga_satuan"))
    desa = request.form.get("desa")
    total_harga = jumlah * harga_satuan
    status = "Pengajuan"

    if not nama_barang or not jumlah or not harga_satuan or not desa:
        response = {
            "message": "Nama Barang, Jumlah,Harga_satuan,desa masih kosong.",
            "status": "Failed",
        }
        return jsonify(response), 400

    new_belanja = Belanja_Camat_Kades(
        nama_barang=nama_barang,
        jumlah=jumlah,
        harga_satuan=harga_satuan,
        total_harga=total_harga,
        status=status,
        desa=desa,
    )

    db.session.add(new_belanja)
    db.session.commit()

    response = {"message": "Berhasil Pengajuan Belanja", "status": "success"}
    return jsonify(response), 200


# bagian select api
@daftarbelanja.route("/api-daftar-belanja", methods=["GET"])
def get_all_belanja():
    belanja_entries = Belanja_Camat_Kades.query.all()

    if not belanja_entries:
        response = {"message": "Belanja entries not found.", "status": "error"}
        return jsonify(response), 404

    belanja_list = []
    for entry in belanja_entries:
        belanja_data = {
            "id_belanja": entry.id_belanja,
            "nama_barang": entry.nama_barang,
            "jumlah": entry.jumlah,
            "harga_satuan": entry.harga_satuan,
            "total_harga": entry.total_harga,
            "status": entry.status,
            "desa": entry.desa,
            "tanggal_pengajuan": entry.tanggal_pengajuan.strftime(
                "%Y-%m-%d"
            ),  # Format the date
        }
        belanja_list.append(belanja_data)

    response = {"message": "Success", "status": "success", "data": belanja_list}
    return jsonify(response), 200


@daftarbelanjakades.route("/api-daftar-belanja-kades", methods=["GET"])
def get_all_belanja_kades():
    nama_desa = request.args.get("nama_desa")

    belanja_entries = Belanja_Camat_Kades.query.filter_by(desa=nama_desa).all()
    if not belanja_entries:
        response = {"message": "Belanja entries not found.", "status": "error"}
        return jsonify(response), 404

    belanja_list = []
    for entry in belanja_entries:
        belanja_data = {
            "id_belanja": entry.id_belanja,
            "nama_barang": entry.nama_barang,
            "jumlah": entry.jumlah,
            "harga_satuan": entry.harga_satuan,
            "total_harga": entry.total_harga,
            "status": entry.status,
            "tanggal_pengajuan": entry.tanggal_pengajuan.strftime(
                "%Y-%m-%d"
            ),  # Format the date
        }
        belanja_list.append(belanja_data)

    response = {"message": "Success", "status": "success", "data": belanja_list}
    return jsonify(response), 200


@select_user_api.route("/api-list-user", methods=["GET"])
def get_all_user():
    user = User.query.all()
    if not user:
        response = {"message": "Users entries not found.", "status": "error"}
        return jsonify(response), 404

    user_list = []
    for entry in user:
        user_data = {
            "id": entry.id,
            "email": entry.email,
            "password": entry.password,
            "status": entry.status,
        }
        user_list.append(user_data)

    response = {"message": "Success", "status": "success", "data": user_list}
    return jsonify(response), 200


@select_desa.route("/api-desa", methods=["GET"])
def get_all_desa():
    desa = Desa.query.all()
    if not desa:
        response = {"message": "Desa entries not found.", "status": "error"}
        return jsonify(response), 404

    desa_list = []
    for entry in desa:
        desa_data = {
            "id_desa": entry.id_desa,
            "nama_desa": entry.nama_desa,
        }
        desa_list.append(desa_data)

    response = {"message": "Success", "status": "success", "data": desa_list}
    return jsonify(response), 200


@select_kades.route("/api-kades", methods=["GET"])
def get_all_kades():
    kades = Kades.query.all()
    if not kades:
        response = {"message": "Kepala Desa entries not found.", "status": "error"}
        return jsonify(response), 404

    kades_list = []
    for entry in kades:
        kades_data = {
            "id_kepala": entry.id_kepala,
            "nama_kades": entry.nama_kades,
            "Desa": entry.Desa,
        }
        kades_list.append(kades_data)

    response = {"message": "Success", "status": "success", "data": kades_list}
    return jsonify(response), 200


@select_notifikasi.route("/api-notifikasi", methods=["GET"])
def get_all_notifikasi():
    notifikasi = Notification.query.all()
    if not notifikasi:
        response = {"message": "Notifikasi entries not found.", "status": "error"}
        return jsonify(response), 404

    notifikasi_list = []
    for entry in notifikasi:
        notifikasi_data = {
            "id_notifikasi": entry.id_notifikasi,
            "pesan": entry.pesan,
            "desa": entry.desa,
            "tanggal_notif": entry.tanggal_notif,
        }
        notifikasi_list.append(notifikasi_data)

    response = {"message": "Success", "status": "success", "data": notifikasi_list}
    return jsonify(response), 200


@select_notifikasi_desa.route("/api-notifikasi-desa", methods=["GET"])
def get_all_notifikasi_desa():
    desa = request.args.get("desa")
    notifikasi = Notification.query.filter_by(desa=desa).all()
    jumlah = Notification.query.filter_by(desa=desa).count()
    if not notifikasi:
        response = {"message": "Notifikasi entries not found.", "status": "error"}
        return jsonify(response), 404

    notifikasi_list = []
    for entry in notifikasi:
        notifikasi_data = {
            "id_notifikasi": entry.id_notifikasi,
            "pesan": entry.pesan,
            "desa": entry.desa,
            "tanggal_notif": entry.tanggal_notif,
        }
        notifikasi_list.append(notifikasi_data)

    response = {
        "message": "Success",
        "status": "success",
        "data": notifikasi_list,
        "jumlah_pesan": jumlah,
    }
    return jsonify(response), 200


# bagian delete api
@delete_user.route("/api-delete-user", methods=["POST"])
def delete_user_api():
    user_id = request.form.get("id")
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    response = {
        "message": "user berhasil di delete ",
        "status": "success",
    }
    return jsonify(response), 200


@delete_desa.route("/api-delete-desa", methods=["POST"])
def delete_desa_api():
    id_desa = request.form.get("id_desa")
    desa = Desa.query.get(id_desa)
    if desa:
        db.session.delete(desa)
        db.session.commit()
    response = {
        "message": "desa berhasil di delete ",
        "status": "success",
    }
    return jsonify(response), 200


@delete_notifikasi.route("/api-delete-notifikasi", methods=["POST"])
def delete_notifikasi_api():
    id_notifikasi = request.form.get("id_notifikasi")
    notifikasi = Notification.query.get(id_notifikasi)

    if notifikasi:
        db.session.delete(notifikasi)
        db.session.commit()
    response = {
        "message": "notifikasi berhasil  di delete ",
        "status": "success",
    }
    return jsonify(response), 200


@delete_belanja.route("/api-delete-belanja", methods=["POST"])
def delete_belanja_api():
    belanja_id = request.form.get("id_belanja")
    belanja = Belanja_Camat_Kades.query.get(belanja_id)

    if belanja:
        db.session.delete(belanja)
        db.session.commit()
    response = {
        "message": "daftar belanja berhasil  di delete ",
        "status": "success",
    }
    return jsonify(response), 200


# bagian update api
@update_user.route("/api-update-user", methods=["POST"])
def update_user_api():
    id = request.form.get("id")
    email_update = request.form.get("email")
    password_update = request.form.get("password")
    status_update = request.form.get("status")

    if id and email_update and password_update and status_update:
        # Find the user by ID
        user = User.query.get(int(id))

        # Update user information
        if user:
            user.email = email_update
            user.password = password_update
            user.status = status_update

            # Commit the changes to the database
            db.session.commit()

        response = {
            "message": "Berhasil Mengupdate Data User ",
            "status": "success",
        }
        return jsonify(response), 200
    if not id or not email_update or not password_update or not status_update:
        response = {
            "message": "Data Masih Kosong... ",
            "status": "Failed",
        }
    return jsonify(response), 202


@changepass.route("/api-changepass", methods=["POST"])
def changepassword():
    id = request.form.get("id")
    konfirmasi_baru = request.form.get("password_konfirmasi")

    if id and konfirmasi_baru:
        # Find the user by ID
        user = User.query.get(int(id))

        # Update user information
        if user:
            user.password = konfirmasi_baru

            # Commit the changes to the database
            db.session.commit()

        response = {
            "message": "Berhasil Mengupdate Data User ",
            "status": "success",
        }
        return jsonify(response), 200
    if not id or not konfirmasi_baru:
        response = {
            "message": "Data Masih Kosong... ",
            "status": "Failed",
        }
    return jsonify(response), 202


@update_desa.route("/api-update-desa", methods=["POST"])
def update_desa_api():
    id_desa = request.form.get("id_desa")
    nama_desa = request.form.get("nama_desa")

    if id_desa and nama_desa:
        desa = Desa.query.get(int(id_desa))

        if desa:
            desa.nama_desa = nama_desa

            db.session.commit()

        response = {
            "message": "Berhasil Mengupdate Data Desa ",
            "status": "success",
        }
        return jsonify(response), 200
    if not id_desa or not nama_desa:
        response = {
            "message": "Data Masih Kosong... ",
            "status": "Failed",
        }
    return jsonify(response), 202


@update_kades.route("/api-update-kades", methods=["POST"])
def update_kades_api():
    id_kepala = request.form.get("id_kepala")
    nama_desa = request.form.get("nama_desa")
    namadesa = Desa.query.filter_by(id_desa=nama_desa).first()

    if id_kepala and nama_desa:
        # Find the user by ID
        kades = Kades.query.get(int(id_kepala))

        # Update user information
        if kades:
            kades.Desa = namadesa.nama_desa

            # Commit the changes to the database
            db.session.commit()

        response = {
            "message": "Berhasil Mengupdate Data Kepala Desa ",
            "status": "success",
        }
        return jsonify(response), 200
    if not id_kepala or not nama_desa:
        response = {
            "message": "Data Masih Kosong... ",
            "status": "Failed",
        }
    return jsonify(response), 202


@update_notifikasi.route("/api-update-notifikasi", methods=["POST"])
def update_notifikasi_api():
    id_notifikasi = request.form.get("id_notifikasi")
    pesan = request.form.get("pesan")
    id_desa = request.form.get("desa")
    desa_nama = Desa.query.filter_by(id_desa=id_desa).first()

    if id_notifikasi and pesan:
        # Find the notification by ID
        notifikasi = Notification.query.get(int(id_notifikasi))

        # Update notification information
        if notifikasi:
            notifikasi.pesan = pesan
            notifikasi.desa = desa_nama.nama_desa

            # Commit the changes to the database
            db.session.commit()

            response = {
                "message": "Berhasil Mengupdate Data Notifikasi",
                "status": "success",
            }
            return jsonify(response), 200
        else:
            response = {
                "message": "Notifikasi tidak ditemukan",
                "status": "Failed",
            }
            return jsonify(response), 404

    else:
        response = {
            "message": "Data masih kosong",
            "status": "Failed",
        }
        return jsonify(response), 400


@update_belanja.route("/api-update-belanja", methods=["POST"])
def update_belanja_api():
    id_belanja = request.form.get("id_belanja")
    status = request.form.get("status")

    if id_belanja and status:
        # Find the user by ID
        belanja = Belanja_Camat_Kades.query.get(int(id_belanja))

        # Update user information
        if belanja:
            belanja.status = status

            # Commit the changes to the database
            db.session.commit()

        response = {
            "message": "Berhasil Mengupdate Data Belanja ",
            "status": "success",
        }
        return jsonify(response), 200
    if not id_belanja or not status:
        response = {
            "message": "Data Masih Kosong... ",
            "status": "Failed",
        }
    return jsonify(response), 202
