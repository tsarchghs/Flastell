from flask import Flask,render_template,redirect,request,url_for
from flask_login import LoginManager, UserMixin, login_required,current_user,login_user,logout_user
from collections import OrderedDict
from models import db
import os
import sqlite3 
import bcrypt
from sqlalchemy.orm import exc
from models import User, Email
from forms import LoginForm

dbPath = "db.sqlite3"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/db.sqlite3'.format(str(os.getcwd()))
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
with app.app_context():
	db.init_app(app)
	db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(ID):
	return User.query.get(ID)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route("/")
def redirectToIndex():
	return redirect(url_for("index"))

@app.route("/login",methods=["GET","POST"])
def login():
	form = LoginForm(request.form)
	if not current_user.is_authenticated:
		if request.method == "POST" and form.validate():
			user = User.query.filter_by(email=form.email.data).first()
			if user:
				access = bcrypt.checkpw(form.password.data.encode("utf8"),user.password)
				if access:
					print('bals')
					login_user(load_user(user.id))
					return redirect("/index")
					print("5")

			return render_template("auth/login.html",invalid_credentials=True,form=form)
		return render_template("auth/login.html",invalid_credentials=False,form=form)
	else:
		return redirect("/index")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register",methods=["GET","POST"])
def register():
	if not current_user.is_authenticated:
		if request.method == "GET":
			return render_template("auth/register.html")
		elif request.method == "POST":
			email = request.form["email"]
			password = request.form["password"]
			password_repeat = request.form["password_repeat"]
			if User.query.filter_by(email=email).all():
				return render_template("auth/register.html",email_taken=True)
			if password != password_repeat:
				return render_template("auth/register.html",passwords_match=False)
			else:
				hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
				conn = sqlite3.connect(dbPath)
				c = conn.cursor()
				c.execute("INSERT INTO user(email,password) VALUES(?,?)",[email,hashed])
				c.execute("SELECT * FROM user WHERE email=? and password=?",[email,hashed])
				user = c.fetchone()
				conn.commit()
				conn.close()
				if user:
					login_user(load_user(user[0]))
					return redirect("/index")
				else:
					return render_template("auth/register.html",error=True)
	else:
		return redirect("/index")
@app.route("/index")
@login_required
def index():
	#c.execute("SELECT * FROM Email WHERE sender_id=? OR receiver_id=?",[current_user.id,current_user.id])
	user_emails = Email.query.filter(Email.sender_id == current_user.id or
									    Email.receiver_id == current_user.id).all()
	emails = OrderedDict()
	for email in user_emails:
		#c.execute("""SELECT * FROM Email WHERE (sender_id=? OR sender_id=?)
		#			 AND (receiver_id=? or receiver_id=?)""",[email[1],email[2],email[1],email[2]])
		emailsList = Email.query.filter(Email.sender_id == email.sender_id or
										   Email.sender_id == email.receiver_id and
										   Email.receiver_id == email.sender_id or
										   Email.receiver_id == email.receiver_id).order_by("-id")
		lastEmail = emailsList[-1]
		try:
			if emails[lastEmail.id,lastEmail.sender_id,lastEmail.receiver_id]:
				pass
		except KeyError:
			emails[lastEmail.id,lastEmail.sender_id,lastEmail.receiver_id] = lastEmail.title
	user_email = OrderedDict()
	for email,title in emails.items():
		print(email)
		id_ = email[0]
		sender = load_user(email[1])
		receiver = load_user(email[2])
		user_email[id_,sender,receiver] = title
	return render_template("index.html",emails=user_email)

@app.route("/showEmails/<int:receiver_id>")
@login_required
def showEmails(receiver_id):
	#c.execute("""SELECT * FROM Email WHERE (sender_id=? OR sender_id=?)
	#			AND (receiver_id=? or receiver_id=?) ORDER BY -id""",[current_user.id,receiver_id,receiver_id,current_user.id])
	#emails = db.engine.execute("""SELECT * FROM Email WHERE (sender_id=? OR sender_id=?)
	#			AND (receiver_id=? or receiver_id=?) ORDER BY -id""",[current_user.id,receiver_id,receiver_id,current_user.id])	
	emails = Email.query.filter(Email.sender_id == current_user.id or
								   Email.sender_id == receiver_id and
								   Email.receiver_id == current_user.id or
								   Email.receiver_id == receiver_id)
	sender_email = OrderedDict()
	for email in emails:
		sender = load_user(email.sender_id)
		sender_email[email] = sender
	receiver = load_user(int(receiver_id))
	return render_template("emails/showEmails.html",emails=sender_email,receiver=receiver)

@app.route("/compose/<string:type_>",methods=["GET","POST"])
@login_required
def compose(type_):
	if request.method == "GET" and type_ == "new":
		return render_template("emails/compose.html")
	elif request.method == "POST":
		receiver_email = request.form["receiver_email"]
		receiver = User.query.filter_by(email=receiver_email).first()
		if not receiver:
			if type_ == "new":
				return render_template("emails/compose.html",invalid_email=True)
			elif type_ == "email":
				return render_template("emails/showEmails.html",invalid_email=True)
		title = request.form["title"]
		description = request.form["description"]
		email = Email(sender_id=current_user.id,
					  receiver_id=receiver.id,
					  title=title,
					  description=description)
		session = db.create_scoped_session()
		session.add(email)
		session.commit()
		return redirect(url_for("showEmails",receiver_id=receiver.id))

@app.route("/account/edit",methods=["GET","POST"])
@login_required
def editAccount():
	if request.method == "GET":
		return render_template("accounts/editAccount.html")
	elif request.method == "POST":
		email = request.form["email"]
		account = User.query.filter_by(id=current_user.id).update({User.email:email})
		return render_template("accounts/editAccount.html",success=True)

if __name__ == "__main__":
	app.run(debug=True,port=8080)