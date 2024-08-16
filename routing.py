from flask import Flask, render_template, request, redirect, session, url_for
from models import User, create_tables, Admin
from config import Config
from werkzeug.security import check_password_hash
from otp import sendotp, codeotp
from register import regis_admin

app = Flask(__name__)
app.config.from_object(Config)


@app.before_request
def setup_database():
    if not hasattr(app, 'first_request'):
        create_tables()
        app.first_request = True


@app.route("/")
def web_application():
    return render_template("web_application/index.html")


@app.route("/register", methods=["GET", "POST"])
def Register():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not (username and password and email):
            return render_template("register & otp/register.html", pesan="Form Tidak Boleh Kosong.")
        user_terpakai = User.get(username) or User.get(email=email)
        if user_terpakai:
            return render_template("register & otp/register.html", pesan="Username atau Email Sudah Terpakai.")
        session['data_registrasi'] = {
            'username': username, 'email': email, 'password': password}
        session['email'] = email
        return redirect("/otp")
    return render_template("register & otp/register.html")


@app.route("/registeradmin", methods=["GET", "POST"])
def Registeradmin():
    return regis_admin()


@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        input_otp = request.form.get('otp')
        if input_otp == session.get('otp'):
            registrasi_take = session.get('data_registrasi')
            registrasi_admin = session.get('data_admin')
            if registrasi_take:
                User.create(username = registrasi_take['username'], password = registrasi_take['password'], email = registrasi_take['email'])
                session.pop('data_registrasi', None)
            if registrasi_admin:
                Admin.create(username = registrasi_admin['username'], password = registrasi_admin['password'], email = registrasi_admin['email'])
                session.pop('data_admin', None)
            return redirect('/otp_sukses')
        else:
            return render_template("register & otp/otp.html", pesan="Invalid cuy")

    otp_code = codeotp()
    session['otp'] = otp_code
    sendotp(otp_code)
    return render_template("register & otp/otp.html")


@app.route("/otp_sukses")
def otp_sukses():
    return render_template("register & otp/otp_sukses.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.getadmin(username)
        member = User.get(username)
        if member and check_password_hash(member.password, password):
            return redirect("/dash")
        elif admin and check_password_hash(admin.password, password):
            return redirect("/dashboardadmin")
        else:
            return render_template('register & otp/login.html', error='username atau password salah')
        
    return render_template('register & otp/login.html')


@app.route("/dash")
def dash():
    return render_template('dashboard/dash.html')

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('level', None)
    return redirect(url_for('web_application'))


@app.route("/dashboardadmin")
def dashboardadmin():
    return render_template("dashboard/dashadmin.html")


if __name__ == "__main__":
    app.run(debug=True)
