from wtforms import Form, BooleanField, StringField, PasswordField, validators

class LoginForm(Form):
	email = StringField('Email',
						[validators.DataRequired(message="Email field is required!")])
	password = StringField('Password',
							[validators.DataRequired(message="Password field is required!")])