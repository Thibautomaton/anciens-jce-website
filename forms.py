from flask_wtf import Form
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, EmailField, SelectMultipleField, SelectFieldBase
from wtforms import validators, ValidationError

class MemberForm(Form):
    Notification = RadioField("Recieve e-mail notifications", choices=[('Y', 'Yes'), ('N', 'No')], default = 'Y')
    Email = EmailField("Email")#,[validators.Email("Please enter an email address")])
    Promo = IntegerField("promo")
    Role = SelectMultipleField('role', choices = [('chargé', "chargé"), ("secretaire", 'secretaire général'), ("tresorier", "tresorier"), ("pres", "president"), ("vice", "vice-president"), ("res communication", "responsable communication"), ("res projet", "responsable projet"), ("res devCom", "responsable devCom"), ("comptable", "comptable")])
    submit = SubmitField("Send")

class IntervenantForm(Form):
    Notification = RadioField("Receive e-mail notifications", choices=[('Y', 'Yes'), ('N', 'No')], default='Y')
    Email = EmailField("Lifetime email")#, [validators.Email("Please enter an email address")])
    Promo = IntegerField("promo")
    submit2 = SubmitField("Send")

class PeopleForm(Form):
    Side = SelectMultipleField("à la Jce vous étiez ..", choices = [('member', 'membre'), ("int", "intervenant")])
    submit_g = SubmitField("Enter")

class LoginForm(Form):
    Name = StringField("Name")
    Firstname = StringField("First Name")
    submit = SubmitField("login")

class ProjectForm(Form):
    Title = StringField("title")
    Client = StringField("client")
    Montant = IntegerField("montant")
    submit2 = SubmitField("add new project")
