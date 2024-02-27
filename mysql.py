from flask import (
    Blueprint,
    request,
    Flask,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    session,
)
from forms import (
    insertupdate_user,
    UploadFileForm,
    InsertUpdateDesa,
    UpdateKades,
    UpdateBelanjaKades,
    InsertUpdateNotification,
    InsertBelanjaKades,
)
from datetime import datetime
from models import db, User, Desa, Kades, Belanja_Camat_Kades, Notification
from flask_wtf.csrf import CSRFError
from werkzeug.utils import secure_filename
import os
from PIL import Image

insert_auth = Blueprint("insert_data", __name__)
update_auth = Blueprint("update_data", __name__)
delete_auth = Blueprint("delete_data", __name__)

insert_auth_desa = Blueprint("insert_data_desa", __name__)
update_auth_desa = Blueprint("update_data_desa", __name__)
delete_auth_desa = Blueprint("delete_data_desa", __name__)

update_auth_kades = Blueprint("update_data_kades", __name__)


delete_auth_camat = Blueprint("delete_data_camat", __name__)
update_auth_camat = Blueprint("update_data_camat", __name__)


insert_auth_notif = Blueprint("insert_data_notif", __name__)
update_auth_notif = Blueprint("update_data_notif", __name__)
delete_auth_notif = Blueprint("delete_data_notif", __name__)

insert_auth_kades_belanja = Blueprint("insert_data_belanja", __name__)
upload_fisio_auth = Blueprint("upload_fisio_auth", __name__)
updatepassword_auth = Blueprint("updatepassword_auth", __name__)

UPLOAD_FOLDER = "Data_Foto/Foto_User"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@insert_auth.route("/insert", methods=["POST"])
def insert():
    form = insertupdate_user()

    if form.validate_on_submit():
        # Use form data as needed in your logic
        email = form.email.data
        password = form.password.data
        full_name = form.full_name.data
        status = form.status.data

        # Create a new user with the required fields
        user = User(email=email, password=password, full_name=full_name, status=status)

        # Add the user to the session and commit the transaction
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("dashboard"))


@delete_auth.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    user_to_delete = User.query.get(id)

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("dashboard"))


@update_auth.route("/update/<id>", methods=["GET", "POST"], endpoint="update")
def update(id):
    user = None

    if id.isdigit():
        # If the identifier is a digit, assume it's an ID
        user = User.query.get(int(id))
    else:
        # If it's not a digit, assume it's a username
        user = User.query.filter_by(full_name=id).first()

    if user is None:
        return redirect(url_for("dashboard"))

    form = insertupdate_user(obj=user)

    if form.validate_on_submit():
        if request.method == "POST":
            if form.full_name.data:
                user.full_name = form.full_name.data
            if form.password.data:
                user.password = form.password.data
            if form.status.data:
                user.status = form.status.data
            if form.email.data:
                user.email = form.email.data

    if id.isdigit():
        db.session.commit()
        return redirect(url_for("dashboard"))

    else:
        db.session.commit()
        return redirect(url_for("profile"))


@insert_auth_desa.route("/insert_desa", methods=["POST"])
def insert_desa():
    form = InsertUpdateDesa()

    if form.validate_on_submit():
        # Use form data as needed in your logic
        nama_desa = form.nama_desa.data

        # Create a new user with the required fields
        desa = Desa(nama_desa=nama_desa)

        # Add the user to the session and commit the transaction
        db.session.add(desa)
        db.session.commit()

        return redirect(url_for("desa"))


@delete_auth_desa.route("/delete_desa/<int:id>", methods=["GET"])
def delete_desa(id):
    desa_to_delete = Desa.query.get(id)

    if desa_to_delete:
        db.session.delete(desa_to_delete)
        db.session.commit()
        return redirect(url_for("desa"))
    else:
        return redirect(url_for("desa"))


@update_auth_desa.route("/update_desa/<id_desa>", methods=["GET", "POST"], endpoint="update_desa")
def update_desa(id_desa):
    selected_desa = None

    if id_desa.isdigit():
        # If the identifier is a digit, assume it's an ID
        selected_desa = Desa.query.get(int(id_desa))
    else:
        # If it's not a digit, assume it's a username
        selected_desa = Desa.query.filter_by(full_name=id_desa).first()

    if selected_desa is None:
        return redirect(url_for("desa"))

    form = InsertUpdateDesa(obj=selected_desa)

    if form.validate_on_submit():
        if request.method == "POST":
            if form.nama_desa.data:
                selected_desa.nama_desa = form.nama_desa.data

    if id_desa.isdigit():  # Check id_desa, not id
        db.session.commit()
        return redirect(url_for("desa"))
    else:
        db.session.commit()
        return redirect(url_for("profile"))


@update_auth_kades.route("/update_kades/<id_kepala>", methods=["GET", "POST"], endpoint="update_kades")
def update_kades(id_kepala):
    selected_kades = None

    if id_kepala.isdigit():
        # If the identifier is a digit, assume it's an ID
        selected_kades = Kades.query.get(int(id_kepala))
    else:
        # If it's not a digit, assume it's a username
        selected_kades = Kades.query.filter_by(full_name=id_kepala).first()

    if selected_kades is None:
        return redirect(url_for("menu_kades"))

    form = UpdateKades(obj=selected_kades)

    if form.validate_on_submit():
        if request.method == "POST":
            if form.Desa.data:
                selected_kades.Desa = form.Desa.data

    if id_kepala.isdigit():  # Check id_desa, not id
        db.session.commit()
        return redirect(url_for("menu_kades"))
    else:
        db.session.commit()
        return redirect(url_for("profile"))


@insert_auth_kades_belanja.route("/insert_belanja", methods=["POST"])
def insert_belanja():
    full_name = session["full_name"]
    form = InsertBelanjaKades()

    if form.validate_on_submit():
        # Use form data as needed in your logic
        nama_barang = form.nama_barang.data
        jumlah = int(form.jumlah.data)  # Convert to integer
        harga_satuan = int(form.harga_satuan.data)  # Convert to integer
        total_harga = jumlah * harga_satuan
        status = "Pengajuan"
        Desa = Kades.query.filter_by(nama_kades=full_name).first()

        # Create a new user with the required fields
        desa = Belanja_Camat_Kades(
            nama_barang=nama_barang,
            jumlah=jumlah,
            harga_satuan=harga_satuan,
            total_harga=total_harga,
            status=status,
            desa=Desa.Desa,
        )

        # Add the user to the session and commit the transaction
        db.session.add(desa)
        db.session.commit()

        return redirect(url_for("kades"))


@delete_auth_camat.route("/delete_camat/<int:id_belanja>", methods=["GET"])
def delete_camat(id_belanja):
    camat_to_delete = Belanja_Camat_Kades.query.get(id_belanja)

    if camat_to_delete:
        db.session.delete(camat_to_delete)
        db.session.commit()
        return redirect(url_for("camat"))
    else:
        return redirect(url_for("camat"))


@update_auth_camat.route("/update_camat/<id_belanja>", methods=["GET", "POST"], endpoint="update_camat")
def update_camat(id_belanja):
    selected_camat = None

    if id_belanja.isdigit():
        # If the identifier is a digit, assume it's an ID
        selected_camat = Belanja_Camat_Kades.query.get(int(id_belanja))
    else:
        # If it's not a digit, assume it's a username
        selected_camat = Belanja_Camat_Kades.query.filter_by(
            full_name=id_belanja
        ).first()

    if selected_camat is None:
        return redirect(url_for("camat"))

    form = UpdateBelanjaKades(obj=selected_camat)

    if form.validate_on_submit():
        if request.method == "POST":
            if form.status.data:
                selected_camat.status = form.status.data

    if id_belanja.isdigit():  # Check id_desa, not id
        db.session.commit()
        return redirect(url_for("camat"))
    else:
        db.session.commit()
        return redirect(url_for("profile"))


@insert_auth_notif.route("/insert_notif", methods=["POST"])
def insert_notif():
    form = InsertUpdateNotification()

    if form.validate_on_submit():
        # Use form data as needed in your logic
        pesan = form.pesan.data
        desa = form.Desa.data
        current_time = datetime.now()

        # Create a new user with the required fields
        notifikasi_data = Notification(
            pesan=pesan, desa=desa, tanggal_notif=current_time
        )
        # Add the user to the session and commit the transaction
        db.session.add(notifikasi_data)
        db.session.commit()

        return redirect(url_for("menu_notifikasi"))


@delete_auth_notif.route("/delete_notif/<int:id_notifikasi>", methods=["GET"])
def delete_notif(id_notifikasi):
    Notification_to_delete = Notification.query.get(id_notifikasi)

    if Notification_to_delete:
        db.session.delete(Notification_to_delete)
        db.session.commit()
        return redirect(url_for("menu_notifikasi"))
    else:
        return redirect(url_for("menu_notifikasi"))


@update_auth_notif.route("/update_notif/<id_notifikasi>", methods=["GET", "POST"], endpoint="update_notif")
def update_notif(id_notifikasi):
    selected_pesan = None

    if id_notifikasi.isdigit():
        # If the identifier is a digit, assume it's an ID
        selected_pesan = Notification.query.get(int(id_notifikasi))
    else:
        # If it's not a digit, assume it's a username
        selected_pesan = Notification.query.filter_by(full_name=id_notifikasi).first()

    if selected_pesan is None:
        return redirect(url_for("menu_notifikasi"))

    form = InsertUpdateNotification(obj=selected_pesan)

    if form.validate_on_submit():
        if request.method == "POST":
            if form.pesan.data:
                selected_pesan.pesan = form.pesan.data
                selected_pesan.desa = form.Desa.data

    if id_notifikasi.isdigit():  # Check id_desa, not id
        db.session.commit()
        return redirect(url_for("menu_notifikasi"))
    else:
        db.session.commit()
        return redirect(url_for("profile"))


@upload_fisio_auth.route("/upload_fisio/<id>", methods=["GET", "POST"])
def upload_fisio(id):
    form = UploadFileForm()

    if form.validate_on_submit():
        try:
            file = form.foto_fisio.data
            username = form.full_name.data
            status = form.status.data

            if file and allowed_file(file.filename):
                upload_folder = os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    "static",
                    UPLOAD_FOLDER,
                    status,
                    username,
                )
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Change this to your desired new filename and extension
                new_filename = username + ".png"

                file_path = os.path.join(upload_folder, secure_filename(new_filename))
                file.save(file_path)

                if new_filename.lower().endswith(
                    ".jpg"
                ) or new_filename.lower().endswith(".jpeg"):
                    image = Image.open(file_path)
                    image.save(file_path, "PNG")

                if id.isdigit():
                    FotoUpload = os.path.join(
                        UPLOAD_FOLDER, status, username, new_filename
                    )
                    user = User.query.get(int(id))
                    user.Foto_Profile = FotoUpload  # Use capital "F" for Foto_Profile
                else:
                    FotoUpload = os.path.join(
                        UPLOAD_FOLDER, status, username, new_filename
                    )
                    user = User.query.filter_by(full_name=id).first()
                    user.Foto_Profile = FotoUpload  # Use capital "F" for Foto_Profile

                    if id.isdigit():
                        db.session.commit()
                        return redirect(url_for("profile"))
                    else:
                        db.session.commit()
                        return redirect(url_for("profile"))

        except Exception as e:
            db.session.rollback()  # Rollback changes in case of an error
            print(f"An error occurred while processing the file: {str(e)}")

    return redirect(url_for("profile"))


@updatepassword_auth.route("/change_password/<string:id>", methods=["POST"])
def change_password(id):
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    # Retrieve the user from the database (you should adapt this based on your authentication method)
    user = User.query.filter_by(email=id).first()

    if user:
        # Check if the current password matches the one stored in the database
        if user.password == current_password:
            if new_password == confirm_password:
                # Update the password in the database
                user.password = (
                    new_password  # Replace this line with your database update logic
                )
                db.session.commit()
                flash("Password updated successfully", "success")
                return redirect(url_for("profile"))
            else:
                flash("New password and confirmation password do not match", "danger")
                return redirect(url_for("profile"))

        else:
            flash("Incorrect current password", "danger")
            return redirect(url_for("profile"))
    else:
        flash("User not found", "danger")
        return redirect(url_for("profile"))
