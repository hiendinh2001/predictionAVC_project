import math
from flask import render_template, request, redirect, url_for, session, jsonify
from app import app, login
from app import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from flask_login import login_required 
from app.models import UserRole

from app.models import Formulaire

import joblib
import os
import numpy as np
import pickle
import sklearn

"""@app.route("/")
def home(): #index.html

    return render_template('index.html')"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/team")
def team():
    return render_template('team.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route('/result', methods=['POST','GET'])
def formulaire():
    err_msg = ""
    if request.method.__eq__('POST'):
        gender = int(request.form.get('gender'))
        age = int(request.form.get('age').strip())
        hypertension = int(request.form.get('hypertension'))
        heart_disease = int(request.form.get('heart_disease'))
        ever_married = int(request.form.get('ever_married'))
        work_type = int(request.form.get('work_type'))
        Residence_type = int(request.form.get('Residence_type'))
        avg_glucose_level = float(request.form.get('avg_glucose_level').strip())
        bmi = float(request.form.get('bmi').strip())
        smoking_status = int(request.form.get('smoking_status'))

        x = np.array([gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type,
                      avg_glucose_level, bmi, smoking_status]).reshape(1, -1)

        scaler_path = os.path.join('C:/Users/hien2/Downloads/github/predictionAVC_project/app/models/scaler.pkl')
        with open(scaler_path, 'rb') as scaler_file:
            scaler = pickle.load(scaler_file)

        x = scaler.transform(x)

        model_path = os.path.join('C:/Users/hien2/Downloads/github/predictionAVC_project/app/models/rf_model.sav')
        dt = joblib.load(model_path)

        Y_pred = dt.predict(x)

        # Extraire la valeur prédite de l'array numpy
        Y_pred_value = int(Y_pred[0])

        # Enregistrer la prédiction dans la base de données
        utils.add_formulaire(gender=gender,
                             age=age,
                             hypertension=hypertension,
                             heart_disease=heart_disease,
                             ever_married=ever_married,
                             work_type=work_type,
                             Residence_type=Residence_type,
                             avg_glucose_level=avg_glucose_level,
                             bmi=bmi,
                             smoking_status=smoking_status,
                             stroke=Y_pred_value)

        # Récupérer les dernières données soumises depuis la base de données
        last_submissions = Formulaire.query.order_by(Formulaire.id.desc()).limit(1).all()

        if Y_pred_value == 0:
            return render_template('nostroke_result.html', err_msg=err_msg, last_submissions=last_submissions)
            #return render_template('nostroke.html', err_msg=err_msg, last_submissions=last_submissions)
        else:
            return render_template('stroke_result.html', err_msg=err_msg, last_submissions=last_submissions)
            #return render_template('stroke.html', err_msg=err_msg, last_submissions=last_submissions)

    #return render_template('formulaire.html', err_msg=err_msg)

@app.route('/valide', methods=['get', 'post'])
def valide():

    return render_template('valide.html')

@app.route('/informations')
def informations():

    return render_template('informations.html')

@app.route('/register', methods=['get', 'post']) 
def user_register():
    err_msg = "" 
    if request.method.__eq__('POST'): 
        name = request.form.get('name') 
        username = request.form.get('username') 
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar_path = None

        try: 
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name,
                               username=username,
                               password=password,
                               email=email,
                               avatar=avatar_path)
                return redirect(url_for('user_signin')) 
            else:
                err_msg = 'Le mot de passe ressaisi est incorrect'
        except Exception as ex: 
            err_msg = 'Le système a une erreur' + str(ex)

    return render_template('register.html',
                           err_msg=err_msg)

@app.route('/user-login', methods=['get', 'post']) 
def user_signin():
    err_msg = "" 
    if request.method.__eq__('POST'):  
        username = request.form.get('username')  
        password = request.form.get('password')

        user = utils.check_login(username=username,
                                 password=password)
        if user: 
            login_user(user=user)
            if 'product_id' in request.args:
                return redirect(url_for(request.args.get('next', 'formulaire'), product_id=request.args['product_id']))

            return redirect(url_for(request.args.get('next', 'formulaire')))
        else:
            err_msg = "Identifiant ou mot de passe incorrect!!!"

    return render_template('login.html',
                           err_msg=err_msg)

@app.route('/admin-login', methods=['post']) 
def signin_admin():
    err_msg = "" 
    username = request.form['username']  
    password = request.form['password']

    user = utils.check_login(username=username,
                             password=password,
                             role=UserRole.ADMIN)
    if user: 
        login_user(user=user) 

    return redirect('/admin')

@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@login.user_loader 
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)

if __name__ == '__main__':
    from app.admin import *
    app.run(debug=True)