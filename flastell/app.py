from flask import Flask
import database as db
import flask_login

dbPath = "db.sqlite3"
database = db.Database(dbPath)
database.connect()
database.execute("CREATE TABLE IF NOT EXISTS User({});".format(db.getUserSchema()))
database.close()

app = Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


if __name__ == "__main__":
	app.run(debug=True,port=8000)