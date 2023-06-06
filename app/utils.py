import json, os
from app import app, db
from app.models import User, UserRole, Formulaire
from flask_login import current_user 
from sqlalchemy import func 
from sqlalchemy.sql import extract
import hashlib 

def read_json(path): 
    with open(path, "r") as f:
        return json.load(f)

def add_user(name, username, password, **kwargs): 
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))
    db.session.add(user)
    db.session.commit()

def check_login(username, password, role=UserRole.USER): 
    if username and password: 
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_formulaire(gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status):
    formulaire = Formulaire(gender=gender,
                            age=age.strip(),
                            hypertension=hypertension,
                            heart_disease=heart_disease,
                            ever_married=ever_married,
                            work_type=work_type,
                            Residence_type=Residence_type,
                            avg_glucose_level=avg_glucose_level.strip(),
                            bmi=bmi.strip(),
                            smoking_status=smoking_status)
    db.session.add(formulaire)
    db.session.commit()