from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String)
	password = db.Column(db.String)
	def __repr__(self):
		return "<User {}>".format(username)

class Email(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	sender_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	receiver_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	title = db.Column(db.String(500))
	description = db.Column(db.String)
	def __repr__(self):
		return "<Email {}>".format(id)

