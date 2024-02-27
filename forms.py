from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,PasswordField,SubmitField,validators
from flask_wtf.file import FileField 
from wtforms.validators import DataRequired,Email,InputRequired


class insertupdate_user(FlaskForm):
    email = StringField('email')
    password = PasswordField('password')  
    status   = IntegerField('status')
    full_name = StringField('full_name')
    foto_profile = StringField('foto_profile')
    submit = SubmitField('submit_register')
    


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit_login = SubmitField('submit_login')


class UploadFileForm(FlaskForm):
    foto_fisio = FileField("foto_fisio", validators=[InputRequired()])
    full_name = StringField('full_name')  # Change 'username' to 'fullname'
    status = StringField('status')  # Change 'username' to 'fullname'



class UpdatePasswordForm(FlaskForm):
    current_password = StringField('current_password')
    new_password = StringField('new_password')
    confirm_password = StringField('confirm_password')
    email = StringField('email') 
    
    
class UpdateKades(FlaskForm):
     Desa = StringField('Desa')
 
  

class InsertUpdateDesa(FlaskForm):
        nama_desa = StringField('nama_desa')
        

class InsertUpdateNotification(FlaskForm):
    pesan = StringField("pesan", validators=[DataRequired()])
    Desa = StringField("desa", validators=[DataRequired()])

    
 
class InsertBelanjaKades(FlaskForm):
    nama_barang = StringField('nama_barang')
    jumlah = StringField('jumlah')
    harga_satuan = StringField('total_harga')
    
class UpdateBelanjaKades(FlaskForm):
    status = StringField('status')
    
    
           