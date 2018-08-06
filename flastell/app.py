from flask import Flask,render_template,redirect,request,url_for
import database as db
import flask_login
import sqlite3 

dbPath = "db.sqlite3"
conn = sqlite3.connect(dbPath)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS User({});".format(db.getUserSchema()))
conn.commit()
conn.close()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
	def __init__(self,ID,username,password):
		self.id = ID
		self.username = username
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

@app.route("/login",methods=["GET","POST"])
def login():
	if not flask_login.current_user.is_authenticated:
		if request.method == "GET":
			return render_template("auth/login.html")
		elif request.method == "POST":
			username = request.form["username"]
			password = request.form["password"]
			conn = sqlite3.connect(dbPath)
			c = conn.cursor()
			c.execute("SELECT * FROM User WHERE username=? and password=?",[username,password])
			user = c.fetchone()
			conn.close()
			if user:
				flask_login.login_user(load_user(user[0]))
				return redirect("/index")
			return redirect("/login")
	else:
		return redirect("/index")


if __name__ == "__main__":
	app.run(debug=True,port=8000)