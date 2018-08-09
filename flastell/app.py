from flask import Flask,render_template,redirect,request,url_for
import database as db
from flask_login import LoginManager, UserMixin, login_required,current_user,login_user,logout_user
import sqlite3 
import bcrypt
from collections import OrderedDict

dbPath = "db.sqlite3"
conn = sqlite3.connect(dbPath)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS User({});".format(db.getUserSchema()))
c.execute("CREATE TABLE IF NOT EXISTS Email({});".format(db.getEmailSchema()))
conn.commit()
conn.close()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
	def __init__(self,ID,email,password):
		self.id = ID
		self.email = email
		self.password = password

@login_manager.user_loader
def load_user(id):
	conn = sqlite3.connect(dbPath)
	c = conn.cursor()
	c.execute("SELECT * FROM User WHERE id=(?)", [id])
	user = c.fetchone()
	conn.commit()
	conn.close()
	if user:
		return User(user[0],user[1],user[2])

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route("/")
def redirectToIndex():
	return redirect(url_for("index"))

@app.route("/login",methods=["GET","POST"])
def login():
	if not current_user.is_authenticated:
		if request.method == "GET":
			return render_template("auth/login.html")
		elif request.method == "POST":
			email = request.form["email"]
			password = request.form["password"]
			conn = sqlite3.connect(dbPath)
			c = conn.cursor()
			c.execute("SELECT * FROM User WHERE email=?",[email])
			user = c.fetchone()
			conn.close()
			if user:
				access = bcrypt.checkpw(password.encode("utf8"),user[2])
				if access:
					login_user(load_user(user[0]))
					return redirect("/index")
			return render_template("auth/login.html",invalid=True)
	else:
		return redirect("/index")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register",methods=["GET","POST"])
def register():
	if request.method == "GET":
		return render_template("auth/register.html")
	elif request.method == "POST":
		email = request.form["email"]
		password = request.form["password"]
		password_repeat = request.form["password_repeat"]
		if password != password_repeat:
			return render_template("auth/register.html",password_correct=False)
		else:
			hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
			conn = sqlite3.connect(dbPath)
			c = conn.cursor()
			c.execute("INSERT INTO User(email,password) VALUES(?,?)",[email,hashed])
			c.execute("SELECT * FROM User WHERE email=? and password=?",[email,hashed])
			user = c.fetchone()
			conn.commit()
			conn.close()
			if user:
				login_user(load_user(user[0]))
				return redirect("/index")
			else:
				return render_template("auth/register.html",error=True)

@app.route("/index")
@login_required
def index():
	conn = sqlite3.connect(dbPath)
	c = conn.cursor()
	c.execute("SELECT * FROM Email WHERE sender_id=? OR receiver_id=?",[current_user.id,current_user.id])
	user_emails = c.fetchall()
	emails = OrderedDict()
	for email in user_emails:
		c.execute("""SELECT * FROM Email WHERE (sender_id=? OR sender_id=?)
					 AND (receiver_id=? or receiver_id=?)""",[email[1],email[2],email[1],email[2]])
		emailsList = c.fetchall()
		lastEmail = emailsList[-1]
		emails[lastEmail[0],lastEmail[1],lastEmail[2]] = lastEmail[3]
	user_email = OrderedDict()
	for email,title in emails.items():
		print(email)
		id_ = email[0]
		sender = load_user(email[1])
		receiver = load_user(email[2])
		user_email[id_,sender,receiver] = title
	conn.close()
	return render_template("index.html",emails=user_email)

@app.route("/showEmails/<int:receiver_id>")
@login_required
def showEmails(receiver_id):
	conn = sqlite3.connect(dbPath)
	c = conn.cursor()
	c.execute("""SELECT * FROM Email WHERE (sender_id=? OR sender_id=?)
				AND (receiver_id=? or receiver_id=?) ORDER BY -id""",[current_user.id,receiver_id,receiver_id,current_user.id])
	emails = c.fetchall()
	conn.close()
	sender_email = OrderedDict()
	for email in emails:
		sender = load_user(email[1])
		sender_email[sender] = email
	receiver = load_user(int(receiver_id))
	return render_template("emails/showEmails.html",emails=sender_email,receiver=receiver)

@app.route("/compose/<string:type_>",methods=["GET","POST"])
@login_required
def compose(type_):
	if request.method == "GET" and type_ == "new":
		return render_template("emails/compose.html")
	elif request.method == "POST":
		conn = sqlite3.connect(dbPath)
		c = conn.cursor()
		receiver_email = request.form["receiver_email"]
		c.execute("SELECT id FROM User WHERE email=?",[receiver_email])
		try:
			receiver_id = c.fetchone()[0]
		except TypeError:
			if type_ == "new":
				return render_template("emails/compose.html",invalid_email=True)
			elif type_ == "email":
				return render_template("emails/showEmails.html",invalid_email=True)
		print(receiver_email)
		title = request.form["title"]
		description = request.form["description"]
		c.execute("""INSERT INTO Email(sender_id,receiver_id,title,description)
							VALUES(?,?,?,?)""",(str(current_user.id),str(receiver_id),
												title,description,))
		conn.commit()
		conn.close()
		return redirect(url_for("showEmails",receiver_id=receiver_id))

if __name__ == "__main__":
	app.run(debug=True,port=8000)