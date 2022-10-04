from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory,abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'MyBestsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#configuring Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
    name = db.Column(db.String(1000),nullable=False)
#Line below only required once, when creating DB.
#db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        user = User().query.filter_by(email=request.form.get('email')).first()
        if not user:
            register = User(
                email=request.form.get('email'),
                password=generate_password_hash(password=request.form.get('password'),method='pbkdf2:sha256',salt_length=8) ,
                name=request.form.get('name')
            )
            db.session.add(register)
            db.session.commit()
            login_user(register)
            return redirect(url_for('secrets'))
        else:
            flash("This email exist, Maybe You are already registered")
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():

    if request.method == "POST":
        user = User().query.filter_by(email=request.form.get('email')).first()
        if user:
            if check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                flash('Logged in successfully.','error')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
                return redirect(url_for('secrets'))
            else:
                flash('Password Incorrect, please try again','error')
                return redirect(url_for('login'))
        else:
            flash('That Email Does Not Exist','error')
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    #edin nachin za vzimane na poslednoto
        #user = User().query.all()[-1].name
    #tova vzima imeto na lognatiqt user
    user =current_user.name
    return render_template("secrets.html",name=user)


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', "files/cheat_sheet.pdf")
    #Tova moje da bude sushto
    #return send_from_directory('','static/files/cheat_sheet.pdf',as_attachment=True)

# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)
