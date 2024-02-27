from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    Foto_Profile = db.Column(
        db.String(128), nullable=False
    )  # Capital "F" for Foto_Profile
    status = db.Column(db.Integer, default=3)

    def __init__(self, full_name, email, password, status):
        self.full_name = full_name
        self.email = email
        self.password = password
        self.status = status


class Sidebar(db.Model):
    __tablename__ = "side_bar"
    id_side = db.Column(db.Integer, primary_key=True)
    name_side = db.Column(db.String(50))
    icon_side = db.Column(db.String(50))
    url_side = db.Column(db.String(50))
    level_user = db.Column(db.String(50))


class Desa(db.Model):
    __tablename__ = "desa"
    id_desa = db.Column(db.Integer, primary_key=True)
    nama_desa = db.Column(db.String(50))


class Kades(db.Model):
    __tablename__ = "kepaladesa"
    id_kepala = db.Column(db.Integer, primary_key=True)
    nama_kades = db.Column(db.String(50))
    Desa = db.Column(db.String(50))


class Belanja_Camat_Kades(db.Model):
    __tablename__ = "belanja"
    id_belanja = db.Column(db.Integer, primary_key=True)
    nama_barang = db.Column(db.String(50))
    jumlah = db.Column(db.Integer)
    harga_satuan = db.Column(db.Integer)
    total_harga = db.Column(db.Integer)
    status = db.Column(db.String(50))
    tanggal_pengajuan = db.Column(db.DateTime)  # Use DateTime for timestamp
    desa = db.Column(db.String(50))


class Notification(db.Model):
    __tablename__ = "notifikasi"
    id_notifikasi = db.Column(db.Integer, primary_key=True)
    pesan = db.Column(db.String(200))
    desa = db.Column(db.String(100))
    tanggal_notif = db.Column(db.DateTime, default=datetime.utcnow)
