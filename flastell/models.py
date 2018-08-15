from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String,unique=True)
	password = db.Column(db.String)
	registered_on = db.Column('registered_on' , db.DateTime)
	def __init__(self,email,password):
		self.email = email
		self.password = password
		self.registered_on = datetime.utcnow()


	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	def __repr__(self):
		return '<User %r>' % (self.email)

class Email(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	sender_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	receiver_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	title = db.Column(db.String(500))
	description = db.Column(db.String)
	def __repr__(self):
		return "<Email {}>".format(self.id)

