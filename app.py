from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    make_response,
    request,
    flash,
    session,
    jsonify,
)
import base64


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO


from constant import (
    LOGINPAGE,
    SERVER,
    USER_SERVER,
    PASSWORD_SERVER,
    DATABASE,
    column_names,
    DASHBOARD_ADMIN,
    colum_names_desa,
    DASHBOARD_DESA,
    DASHBOARD_MENU_KADES,
    DASHBOARD_CAMAT,
    colum_kades,
    colum_belanja_camat,
    DASHOARD_NOTIFIKASI,
    colum_notifikasi,
    DASHBOARD_KADES,
    colum_belanja_kades,
    DASHBOARD_PDF_KADES,
    PDF_TEMPLATE,
    DASHBOARD_PDF_CAMAT,
)

from forms import (
    LoginForm,
    insertupdate_user,
    UploadFileForm,
    UpdatePasswordForm,
    InsertUpdateDesa,
    UpdateKades,
    UpdateBelanjaKades,
    InsertUpdateNotification,
    InsertBelanjaKades,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf

from mysql import (
    insert_auth,
    delete_auth,
    update_auth,
    upload_fisio_auth,
    updatepassword_auth,
    delete_auth_desa,
    insert_auth_desa,
    update_auth_desa,
    update_auth_kades,
    delete_auth_camat,
    update_auth_camat,
    insert_auth_notif,
    update_auth_notif,
    delete_auth_notif,
    insert_auth_kades_belanja,
)

from API import (
    api,
    api_token,
    logout,
    registrasi,
    registrasi_desa,
    notifikasi,
    belanja,
    daftarbelanja,
    daftarbelanjakades,
    select_desa,
    select_kades,
    select_notifikasi,
    select_user_api,
    select_notifikasi_desa,
    delete_user,
    delete_desa,
    delete_notifikasi,
    delete_belanja,
    update_user,
    update_desa,
    update_kades,
    update_notifikasi,
    update_belanja,
    changepass,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
import os
from models import db, User, Sidebar, Notification, Desa, Kades, Belanja_Camat_Kades
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from flask_cors import CORS


app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5008"}})



app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{USER_SERVER}:{PASSWORD_SERVER}@{SERVER}/{DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.permanent_session_lifetime = timedelta(days=30)  # Adjust the lifetime as needed
app.register_blueprint(insert_auth)
app.register_blueprint(update_auth)
app.register_blueprint(delete_auth)
app.register_blueprint(insert_auth_desa)
app.register_blueprint(delete_auth_desa)
app.register_blueprint(update_auth_desa)
app.register_blueprint(update_auth_kades)
app.register_blueprint(delete_auth_camat)
app.register_blueprint(update_auth_camat)
app.register_blueprint(insert_auth_notif)
app.register_blueprint(update_auth_notif)
app.register_blueprint(delete_auth_notif)
app.register_blueprint(insert_auth_kades_belanja)
app.register_blueprint(api_token)
app.register_blueprint(api)
app.register_blueprint(logout)
app.register_blueprint(registrasi)
app.register_blueprint(registrasi_desa)
app.register_blueprint(notifikasi)
app.register_blueprint(belanja)
app.register_blueprint(daftarbelanja)
app.register_blueprint(daftarbelanjakades)
app.register_blueprint(select_desa)
app.register_blueprint(select_kades)
app.register_blueprint(select_notifikasi)
app.register_blueprint(select_notifikasi_desa)
app.register_blueprint(select_user_api)
app.register_blueprint(delete_user)
app.register_blueprint(delete_desa)
app.register_blueprint(delete_notifikasi)
app.register_blueprint(delete_belanja)
app.register_blueprint(update_user)
app.register_blueprint(update_desa)
app.register_blueprint(update_kades)
app.register_blueprint(update_notifikasi)
app.register_blueprint(update_belanja)
app.register_blueprint(changepass)

app.config["WTF_CSRF_ENABLED"] = False

app.secret_key = "many random bytes"

csrf = CSRFProtect(app)  # Inisialisasi CSRF protection
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # in seconds


@app.route("/", methods=["GET", "POST"])
def index():
    full_name = request.cookies.get("full_name")
    if full_name:
        return redirect(url_for("dashboard"))
    else:
        login_form = LoginForm()

    if request.method == "POST":
        if "submit_login" in request.form and login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            user = User.query.filter_by(email=email).first()

            if user and user.password == password:
                csrf_token = generate_csrf()
                session["full_name"] = user.full_name
                session["csrf_token"] = csrf_token
                session["status"] = user.status

                resp = make_response(redirect(url_for("dashboard")))
                expiration_date = datetime.now() + timedelta(days=30)
                resp.set_cookie("full_name", user.full_name, expires=expiration_date)
                resp.set_cookie("status", str(user.status), expires=expiration_date)
                return resp
            else:
                message = "Password atau Email Salah!!"
                flash(message, "error")  # Flash the error message
                return redirect(url_for("index"))

    html_content = render_template(LOGINPAGE, login_form=login_form)

    response = make_response(html_content)

    # Set the Cache-Control header to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, no-store"

    return response


@app.route("/pdf_kades", methods=["GET", "POST"])
def pdf_kades():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in
    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "3":
            form = InsertBelanjaKades()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]
            Desa = Kades.query.filter_by(nama_kades=full_name).first()
            kades = Belanja_Camat_Kades.query.filter_by(desa=Desa.Desa).all()
            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()
            count_result = Notification.query.filter_by(desa=Desa.Desa).count()
            notifikasi_nilai = Notification.query.filter_by(desa=Desa.Desa).all()

            modified_data_notifikasi = []

            for notifikasi_data in notifikasi_nilai:
                modified_user = [
                    notifikasi_data.id_notifikasi,
                    notifikasi_data.pesan,
                    notifikasi_data.desa,
                    notifikasi_data.tanggal_notif,
                ]
                modified_data_notifikasi.append(modified_user)

            modified_data_kades = []

            for data_kades in kades:
                modified_user = [
                    data_kades.id_belanja,
                    data_kades.nama_barang,
                    data_kades.jumlah,
                    data_kades.harga_satuan,
                    data_kades.total_harga,
                    data_kades.status,
                    data_kades.tanggal_pengajuan,
                ]
                modified_data_kades.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list1 = [
                {
                    "label": "Nama Barang",
                    "input_type": "text",
                    "name": "nama_barang",
                    "placeholder": "conntoh : nama_barang",
                },
                {
                    "label": "Harga Satuan",
                    "input_type": "text",
                    "name": "harga_satuan",
                    "placeholder": "conntoh : 10000",
                },
                {
                    "label": "Jumlah",
                    "input_type": "text",
                    "name": "jumlah",
                    "placeholder": "conntoh : 10",
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_PDF_KADES,  # Replace with your template name
                kades=modified_data_kades,
                colum_belanja_kades=colum_belanja_kades,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_hitung=count_result,
                notifikasi_nilai=modified_data_notifikasi,
                data_list1=data_list1,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/pdf_camat", methods=["GET", "POST"])
def pdf_camat():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string
        data_desa = Desa.query.all()
        desa_options = [(desa.nama_desa) for desa in data_desa]

        if status == "2":
            form = UpdateBelanjaKades()
            camat = Belanja_Camat_Kades.query.all()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data_camat = []

            for data_camat in camat:
                modified_user = [
                    data_camat.id_belanja,
                    data_camat.nama_barang,
                    data_camat.jumlah,
                    data_camat.harga_satuan,
                    data_camat.total_harga,
                    data_camat.status,
                    data_camat.tanggal_pengajuan,
                    data_camat.desa,
                ]
                modified_data_camat.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list = [
                {
                    "input_type": "select",
                    "name": "Desa",
                    "options": desa_options,
                }
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_PDF_CAMAT,  # Replace with your template name
                camat=modified_data_camat,
                colum_belanja_camat=colum_belanja_camat,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list1=data_list,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/generate_pdf", methods=["GET"])
def generate_pdf():
    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    image_file_ttd = open("static/images/ttd.jpg", "rb")

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string
        total_belanja = 0
        if status == "3":
            with open("static/images/logo.png", "rb") as image_file:
                startdate = request.args.get("startDate")
                enddate = request.args.get("endDate")

                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                image_ttd = base64.b64encode(image_file_ttd.read()).decode("utf-8")

                full_name = session["full_name"]

                Desa = Kades.query.filter_by(nama_kades=full_name).first()
                kades = Belanja_Camat_Kades.query.filter(
                    Belanja_Camat_Kades.desa == Desa.Desa,
                    Belanja_Camat_Kades.status == "Di Setujui",
                    Belanja_Camat_Kades.tanggal_pengajuan.between(startdate, enddate),
                ).all()

            modified_data_kades = []

            for data_kades in kades:
                modified_user = [
                    data_kades.id_belanja,
                    data_kades.nama_barang,
                    data_kades.jumlah,
                    data_kades.harga_satuan,
                    data_kades.total_harga,
                    data_kades.status,
                    data_kades.tanggal_pengajuan,
                ]
                modified_data_kades.append(modified_user)

                total_belanja += data_kades.total_harga

            rendered_html = render_template(
                PDF_TEMPLATE,
                data_desa=Desa.Desa,
                startdate=startdate,
                enddate=enddate,
                kades=modified_data_kades,
                total_belanja=total_belanja,
                image_data=image_data,
                image_ttd=image_ttd,
            )

            # Create a buffer to store the PDF
            buffer = BytesIO()

            # Convert HTML to PDF
            pisa.CreatePDF(rendered_html, dest=buffer)

            # Move the buffer's cursor to the beginning
            buffer.seek(0)

            # Create a Flask response with the PDF
            # Create a Flask response with the PDF
            response = make_response(buffer.getvalue())
            response.headers["Content-Type"] = "application/pdf"
            response.headers[
                "Content-Disposition"
            ] = f"inline; filename=Laporan_Anggaran_{Desa.Desa}_{startdate}_{enddate}.pdf"

            return response

    else:
        return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/generate_pdf_camat", methods=["GET"])
def generate_pdf_camat():
    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    image_file_ttd = open("static/images/ttd.jpg", "rb")

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string
        total_belanja = 0
        if status == "2":
            with open("static/images/logo.png", "rb") as image_file:
                startdate = request.args.get("startDate")
                enddate = request.args.get("endDate")
                Desa = request.args.get("Desa")

                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                image_ttd = base64.b64encode(image_file_ttd.read()).decode("utf-8")

                kades = Belanja_Camat_Kades.query.filter(
                    Belanja_Camat_Kades.desa == Desa,
                    Belanja_Camat_Kades.status == "Di Setujui",
                    Belanja_Camat_Kades.tanggal_pengajuan.between(startdate, enddate),
                ).all()

            modified_data_kades = []

            for data_kades in kades:
                modified_user = [
                    data_kades.id_belanja,
                    data_kades.nama_barang,
                    data_kades.jumlah,
                    data_kades.harga_satuan,
                    data_kades.total_harga,
                    data_kades.status,
                    data_kades.tanggal_pengajuan,
                ]
                modified_data_kades.append(modified_user)

                total_belanja += data_kades.total_harga

            rendered_html = render_template(
                PDF_TEMPLATE,
                data_desa=Desa,
                startdate=startdate,
                enddate=enddate,
                kades=modified_data_kades,
                total_belanja=total_belanja,
                image_data=image_data,
                image_ttd=image_ttd,
            )

            # Create a buffer to store the PDF
            buffer = BytesIO()

            # Convert HTML to PDF
            pisa.CreatePDF(rendered_html, dest=buffer)

            # Move the buffer's cursor to the beginning
            buffer.seek(0)

            # Create a Flask response with the PDF
            # Create a Flask response with the PDF
            response = make_response(buffer.getvalue())
            response.headers["Content-Type"] = "application/pdf"
            response.headers[
                "Content-Disposition"
            ] = f"inline; filename=Laporan_Anggaran_{Desa}_{startdate}_{enddate}.pdf"

            return response

    else:
        return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/profile", methods=["GET", "POST"])
def profile():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    # Get the currently logged-in user's username from the session

    form = insertupdate_user()
    form1 = UploadFileForm()
    form2 = UpdatePasswordForm()
    full_name = session["full_name"]
    csrf_token = session["csrf_token"]
    # Query the database to retrieve the user's data
    user = User.query.filter_by(full_name=full_name).first()
    status = session.get("status")

    data_hitung = 1  # Set the count_user value as needed

    sidebar_items = []  # Define it at the beginning
    sidebar_data = Sidebar.query.filter_by(level_user=status).all()
    # Fetch all sidebar items (replace 'Sidebar' with your actual model name)

    # Modify the sidebar data as needed
    for item in sidebar_data:
        sidebar_item = {
            "name": item.name_side,
            "icon": item.icon_side,
            "url": item.url_side,
        }
        sidebar_items.append(sidebar_item)

    html_content = render_template(
        "profile.html",
        sidebar_items=sidebar_items,
        data_hitung=data_hitung,
        user=user,
        form=form,
        form1=form1,
        form2=form2,
        csrf_token=csrf_token,
    )

    response = make_response(html_content)

    # Set the Cache-Control header to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, no-store"

    return response


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    session.permanent = True
    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")

    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "1":
            return redirect(url_for("admin"))
        elif status == "2":
            return redirect(url_for("camat"))
        elif status == "3":
            return redirect(url_for("kades"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "1":
            form = insertupdate_user()
            users = User.query.all()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data = []

            for user in users:
                modified_user = [user.id, user.email, "*******", user.status]
                modified_data.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list = [
                {
                    "label": "Email",
                    "input_type": "email",
                    "name": "email",
                    "value": "email",
                },
                {
                    "label": "Password",
                    "input_type": "password",
                    "name": "password",
                    "value": "password",
                },
                {
                    "label": "Status",
                    "input_type": "select",
                    "name": "status",
                    "options": [("Admin", "1"), ("Camat", "2"), ("Kades", "3")],
                },
            ]

            data_list1 = [
                {
                    "label": "Email",
                    "input_type": "email",
                    "name": "email",
                    "required": "1",
                },
                {
                    "label": "Full Name",
                    "input_type": "text",
                    "name": "full_name",
                    "required": "1",
                },
                {
                    "label": "Password",
                    "input_type": "password",
                    "name": "password",
                    "required": "1",
                },
                {
                    "label": "Status",
                    "input_type": "select",
                    "name": "status",
                    "required": "1",
                    "options": [("1", "Admin"), ("2", "Camat"), ("3", "Kades")],
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_ADMIN,  # Replace with your template name
                users=modified_data,
                column_names=column_names,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list=data_list,
                data_list1=data_list1,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))  # Redirect to the logout page


@app.route("/desa", methods=["GET", "POST"])
def desa():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "1":
            form = InsertUpdateDesa()

            data_desa = Desa.query.all()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data_desa = []

            for desa in data_desa:
                modified_desa = [
                    desa.id_desa,
                    desa.nama_desa,
                ]  # Assuming 'password' is the third column
                modified_data_desa.append(modified_desa)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list = [
                {
                    "label": "Nama Desa",
                    "input_type": "text",
                    "name": "nama_desa",
                    "value": "nama_desa",
                },
            ]

            data_list1 = [
                {
                    "label": "Nama Desa",
                    "input_type": "text",
                    "name": "nama_desa",
                    "required": "1",
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_DESA,  # Replace with your template name
                desa=modified_data_desa,
                colum_names_desa=colum_names_desa,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list=data_list,
                data_list1=data_list1,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))


@app.route("/menu_kades", methods=["GET", "POST"])
def menu_kades():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "1":
            form = UpdateKades()
            kades = Kades.query.all()
            data_desa = Desa.query.all()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data_kades = []

            for kades_desa in kades:
                modified_kades = [
                    kades_desa.id_kepala,
                    kades_desa.nama_kades,
                    kades_desa.Desa,
                ]  # Assuming 'password' is the third column
                modified_data_kades.append(modified_kades)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            desa_options = [(desa.nama_desa) for desa in data_desa]

            # Add the 'Desa' field options to the 'data_list' dictionary
            data_list = [
                {
                    "label": "Nama Desa",
                    "input_type": "select",
                    "name": "Desa",
                    "options": desa_options,
                }
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_MENU_KADES,  # Replace with your template name
                kades=modified_data_kades,
                colum_kades=colum_kades,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list=data_list,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))


@app.route("/kades", methods=["GET", "POST"])
def kades():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in
    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "3":
            form = InsertBelanjaKades()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]
            Desa = Kades.query.filter_by(nama_kades=full_name).first()
            kades = Belanja_Camat_Kades.query.filter_by(desa=Desa.Desa).all()
            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()
            count_result = Notification.query.filter_by(desa=Desa.Desa).count()
            notifikasi_nilai = Notification.query.filter_by(desa=Desa.Desa).all()

            modified_data_notifikasi = []

            for notifikasi_data in notifikasi_nilai:
                modified_user = [
                    notifikasi_data.id_notifikasi,
                    notifikasi_data.pesan,
                    notifikasi_data.desa,
                    notifikasi_data.tanggal_notif,
                ]
                modified_data_notifikasi.append(modified_user)

            modified_data_kades = []

            for data_kades in kades:
                modified_user = [
                    data_kades.id_belanja,
                    data_kades.nama_barang,
                    data_kades.jumlah,
                    data_kades.harga_satuan,
                    data_kades.total_harga,
                    data_kades.status,
                    data_kades.tanggal_pengajuan,
                ]
                modified_data_kades.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list1 = [
                {
                    "label": "Nama Barang",
                    "input_type": "text",
                    "name": "nama_barang",
                    "placeholder": "conntoh : nama_barang",
                },
                {
                    "label": "Harga Satuan",
                    "input_type": "text",
                    "name": "harga_satuan",
                    "placeholder": "conntoh : 10000",
                },
                {
                    "label": "Jumlah",
                    "input_type": "text",
                    "name": "jumlah",
                    "placeholder": "conntoh : 10",
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_KADES,  # Replace with your template name
                kades=modified_data_kades,
                colum_belanja_kades=colum_belanja_kades,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_hitung=count_result,
                notifikasi_nilai=modified_data_notifikasi,
                data_list1=data_list1,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/menu_notifikasi", methods=["GET", "POST"])
def menu_notifikasi():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string
        notifikasi_data = None

        if status == "2":
            form = InsertUpdateNotification()
            notifikasi_nilai = Notification.query.all()
            data_desa = Desa.query.all()
            desa_options = [(desa.nama_desa) for desa in data_desa]

            # Add the 'Desa' field options to the 'data_list' dictionary

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data_notifikasi = []

            for notifikasi_data in notifikasi_nilai:
                modified_user = [
                    notifikasi_data.id_notifikasi,
                    notifikasi_data.pesan,
                    notifikasi_data.desa,
                    notifikasi_data.tanggal_notif,
                ]
                modified_data_notifikasi.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list = [
                {
                    "label": "Pesan",
                    "input_type": "textArea",
                    "name": "pesan",
                    "value": notifikasi_data.pesan if notifikasi_data else "",
                },
                {
                    "label": "Nama Desa",
                    "input_type": "select",
                    "name": "Desa",
                    "options": desa_options,
                },
            ]

            data_list1 = [
                {
                    "label": "Pesan",
                    "input_type": "textArea",
                    "name": "pesan",
                    "value": notifikasi_data.pesan if notifikasi_data else "",
                },
                {
                    "label": "Nama Desa",
                    "input_type": "select",
                    "name": "Desa",
                    "options": desa_options,
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHOARD_NOTIFIKASI,  # Replace with your template name
                notifikasi_nilai=modified_data_notifikasi,
                colum_notifikasi=colum_notifikasi,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list=data_list,
                data_list1=data_list1,
                desa_options=desa_options,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))


@app.route("/camat", methods=["GET", "POST"])
def camat():
    session.permanent = True

    if "full_name" not in session:
        return redirect(
            url_for("logout")
        )  # Redirect to the login page if not logged in

    status = session.get("status")
    if status is not None:
        status = str(status)  # Convert status to a string

        if status == "2":
            form = UpdateBelanjaKades()
            camat = Belanja_Camat_Kades.query.all()

            full_name = session["full_name"]
            csrf_token = session["csrf_token"]

            # Query the database to retrieve the user's data
            user_data = User.query.filter_by(full_name=full_name).first()

            modified_data_camat = []

            for data_camat in camat:
                modified_user = [
                    data_camat.id_belanja,
                    data_camat.nama_barang,
                    data_camat.jumlah,
                    data_camat.harga_satuan,
                    data_camat.total_harga,
                    data_camat.status,
                    data_camat.tanggal_pengajuan,
                    data_camat.desa,
                ]
                modified_data_camat.append(modified_user)

            sidebar_items = []  # Define it at the beginning
            sidebar_data = Sidebar.query.filter_by(level_user=status).all()

            # Modify the sidebar data as needed
            for item in sidebar_data:
                sidebar_item = {
                    "name": item.name_side,
                    "icon": item.icon_side,
                    "url": item.url_side,
                }
                sidebar_items.append(sidebar_item)

            data_list1 = [
                {
                    "label": "Status",
                    "input_type": "select",
                    "name": "status",
                },
            ]

            # Assuming you have a 'DASHBOARD' template defined
            html_content = render_template(
                DASHBOARD_CAMAT,  # Replace with your template name
                camat=modified_data_camat,
                colum_belanja_camat=colum_belanja_camat,  # You need to define 'column_names'
                sidebar_items=sidebar_items,
                data_list1=data_list1,
                form=form,
                user=user_data,
                csrf_token=csrf_token,
            )

            response = make_response(html_content)

            # Set the Cache-Control header to prevent caching
            response.headers[
                "Cache-Control"
            ] = "no-cache, no-store, must-revalidate, no-store"

            return response
        else:
            return redirect(url_for("logout"))  # Redirect to the logout p

    return


@app.route("/logout")
def logout():
    session.pop("full_name", None)

    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("full_name")
    return resp


if __name__ == "__main__":
    app.register_blueprint(upload_fisio_auth, url_prefix="/upload_fisio_auth")
    app.register_blueprint(updatepassword_auth, url_prefix="/updatepassword_auth")
    app.run(debug=True, port=5008)
