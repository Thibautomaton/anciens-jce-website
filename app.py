# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from flask import Flask, request, url_for, redirect, render_template, flash, session
from forms import MemberForm, IntervenantForm, PeopleForm, LoginForm, ProjectForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask import jsonify
import json
from flask_mail import Mail, Message
import sqlite3 as sql

app = Flask(__name__, template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jcedb.sqlite3' #'postgresql://postgres:Guildwars3@localhost:5432/jce-db'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME']='jceanciens@gmail.com'
app.config['MAIL_PASSWORD']='%0Iq3Tt7wuz7W7Y7zAjK'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

app.config['SECRET_KEY'] = 'exRR92jFvMtofXPGCFKNT12mA1'
app.config['SECURITY_REGISTERABLE'] = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.debug = True

mail = Mail(app)

db = SQLAlchemy(app)


class Members(db.Model):
    identifiant = db.Column(db.String(75), primary_key=True)
    name = db.Column(db.String(75))
    first_name = db.Column(db.String(75))
    notification = db.Column(db.Boolean(False))
    email = db.Column(db.String(75))
    promo = db.Column(db.Integer)
    role = db.Column(db.String(75))
    type = db.Column(db.String(30))

    def __init__(self, identifiant, name, first_name, notification, email, promo, role, type):
        self.identifiant = identifiant
        self.name = name
        self.first_name = first_name
        self.notification = True if notification == 'Y' else False
        self.email = email
        self.promo = promo
        self.role = role
        self.type = type

    def __repr__(self):
        return '<Member %r>' % self.identifiant

    def as_dict(self):
        return {c.name : getattr(self, c.name) for c in self.__table__.columns}

class Projets(db.Model):
    title = db.Column(db.String(80), primary_key=True)
    id_intervenants = db.Column(db.String(75))
    client = db.Column(db.String(75))
    montant = db.Column(db.Integer)

    def __init__(self, title, id_intervenants, client, montant):
        self.title = title
        self.id_intervenants = id_intervenants
        self.client = client
        self.montant = montant

    def __repr__(self):
        return '<Projet %s>' % self.title

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ProjetIntervenant(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    intervenant_id = db.Column(db.String(80), ForeignKey(Members.identifiant))
    project_title = db.Column(db.String(80), ForeignKey(Projets.title))

    def __init__(self, id, intervenant_id, project_title):
        self.id = id
        self.intervenant_id = intervenant_id
        self.project_title = project_title

    def __repr__(self):
        return '<Intervenants %s>' %self.intervenant_id

# Press the green button in the gutter to run the script.

@app.route('/')
def index():
    username = "none"

    if 'username' in session:
        username = session['username']
        return render_template("welcome.html", name=username, identifiant=session['dict']['id'])

    else:
        return render_template("welcome.html", name=username)



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/welcome")
def welcome():
    redirect(url_for("login"))


@app.route('/show_all')
def show_all():
    if(session['dict']['id']):
        return render_template("show_all.html", name = session['dict']['id'])
    else:
        return render_template("show_all.html")

@app.route('/list_members')
def list_members():
    return render_template("list_members.html", members = Members.query.all())

@app.route('/member_json/<name>')
def member_json(name):
    member = Members.query.get(name)
    dict_data = member.as_dict()

    projets = db.session.query(ProjetIntervenant).where(ProjetIntervenant.intervenant_id==member.identifiant).all()

    project_list = []
    for projet in projets:
        proj = Projets.query.get(projet.project_title)

        project_list.append(proj.as_dict())

    dict_data["projets"] = project_list
    print(dict_data)
    json_data = str(json.dumps(dict_data))
    return render_template("member.html", name=json_data)

@app.route('/new_proj', methods=["GET", "POST"])
def new_proj():
    proj_form = ProjectForm()
    if request.method == "POST":
        if proj_form.validate == False:
            flash("Fill all the required fields")
            return render_template("new_proj.html", form=proj_form, name = session['dict']['id'])
        else:
            project = Projets.query.get(request.form['Title'])
            print(project)
            if (project):
                print("project exists")

                id_intervenants = eval(project.Second())
                if session['dict']['id'] in id_intervenants:
                    pass
                else:
                    id_intervenants.append(session['dict']['id'])

                    id_int = (request.form['Title'][0:3]).upper() + '_' + session['dict']['id']
                    print("id project"+id_int)
                    int_proj = ProjetIntervenant(id_int, session['dict']['id'], request.form['Title'])
                    db.session.add(int_proj)

                project = Projets(request.form['Title'], str(id_intervenants), request.form['Client'],
                                  request.form['Montant'])

                db.session.commit()
                flash("the record was updated successfully")

            else:
                id_intervenants = []
                id_intervenants.append(session['dict']['id'])
                project = Projets(request.form['Title'], str(id_intervenants), request.form['Client'],
                                  request.form['Montant'])

                id_int = (request.form['Title'][0:3]).upper() + '_' + session['dict']['id']
                int_proj = ProjetIntervenant(id_int, session['dict']['id'], request.form['Title'])
                db.session.add(project)
                db.session.commit()
                db.session.add(int_proj)

                db.session.commit()
                flash("record inserted successfully")

                if request.form["submit2"]:
                    return redirect(url_for('show_all'))

                else:
                    return redirect(url_for('new_proj'))

    elif request.method == "GET":
        return render_template("new_proj.html", form=proj_form, name = session['dict']['id'])


@app.route('/register_member', methods=["GET", "POST"])
def register_member():
    mem_form = MemberForm()
    if request.method == "POST":
        if mem_form.validate() == False:
            flash("Fill all the required fields")
            return render_template("register_mem.html", form=mem_form)
        else:
            member = Members.query.get(session['dict']['id'])
            if (member):
                print("exists")
                member = Members(session['dict']['id'], session['dict']['name'], session['dict']['firstname'],
                                 request.form['Notification'], \
                                 request.form['Email'], request.form['Promo'], request.form['Role'], 'member')
                db.session.commit()
            else:
                member = Members(session['dict']['id'], session['dict']['name'], session['dict']['firstname'],
                                 request.form['Notification'], \
                                 request.form['Email'], request.form['Promo'], request.form['Role'], 'member')
                db.session.add(member)
                db.session.commit()
                flash("The record was inserted successfully")

            name = session['dict']['name']
            firstname = session['dict']['firstname']
            email = request.form['Email']

            msg_content = str(firstname) +" "+str(name) +" registered him(her)self with email "+str(email)+". Send a message to say hello and welcome him(her) in the community :)"
            msg_recipients = db.session.execute("SELECT email from Members where notification=True;")

            msg_recipients = list(msg_recipients)
            msg_recipients = list(map(lambda x: x[0], msg_recipients))
            print(msg_recipients)

            msg = Message("NOTIF[new member]", sender = "anciens6jce@gmail.com", recipients =msg_recipients)

            msg.body = msg_content

            mail.send(msg)

            return redirect(url_for('show_all'))

    elif request.method == "GET":
        return render_template("register_mem.html", form=mem_form)


@app.route('/register_intervenant', methods=["GET", "POST"])
def register_intervenant():
    int_form = IntervenantForm()
    if request.method == "POST":
        if int_form.validate() == False:
            flash("Fill all the required fields")
            return render_template("register.html", int_form=int_form)
        else:
                intervenant = Members.query.get(session['dict']['id'])
                if (intervenant):
                    intervenant = Members(session['dict']['id'], session['dict']['name'], session['dict']['firstname'],
                                          request.form['Notification'], \
                                          request.form['Email'], request.form['Promo'], 'intervenant', 'intervenant')
                    db.session.commit()
                else:
                    intervenant = Members(session['dict']['id'], session['dict']['name'], session['dict']['firstname'],
                                          request.form['Notification'], \
                                          request.form['Email'], request.form['Promo'], 'intervenant', 'intervenant')
                    db.session.add(intervenant)
                    db.session.commit()
                    flash("the record was inserted sucessfully")

                name = session['dict']['name']
                firstname = session['dict']['firstname']
                email = request.form['Email']

                msg_content = str(firstname) + " " + str(name) + " registered him(her)self with email " + str(
                    email) + ". Send a message to say hello and welcome him(her) in the community :)"
                msg_recipients = db.session.execute("SELECT email from Members where notification=True;")

                msg_recipients = list(msg_recipients)
                msg_recipients = list(map(lambda x: x[0], msg_recipients))
                print(msg_recipients)

                msg = Message("NOTIF[new member]", sender="anciens6jce@gmail.com", recipients=msg_recipients)

                msg.body = msg_content

                mail.send(msg)
                return redirect(url_for('new_proj'))

    elif request.method == "GET":
        return render_template("register.html", int_form=int_form)


@app.route('/side', methods=["GET", "POST"])
def side():
    side_form = PeopleForm()
    if request.method == "POST":
        if side_form.validate() == False:
            flash("Fill all the required fields")
            return render_template("side.html", side_form=side_form)
        else:
            session['dict']['type'] = request.form['Side']
            print(session['dict'])
            if request.form['Side'] == "member":
                return redirect(url_for('register_member'))
            else:
                return redirect(url_for('register_intervenant'))

    elif request.method == "GET":
        return render_template("side.html", side_form=side_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate() == False:
            flash("validate all fields")
            return render_template("login.html", form=form)
        else:
            identifiant = (request.form['Firstname'] + request.form['Name']).lower()

            session['username'] = identifiant
            session['dict'] = {'id': identifiant, 'name': request.form['Name'], 'firstname': request.form['Firstname']}

            member = Members.query.get(session['dict']['id'])
            if(member):
                return redirect(url_for('index'))
            else:
                return redirect(url_for('side'))

    elif request.method == "GET":
        return render_template("login.html", form=form)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


