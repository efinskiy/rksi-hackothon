from flask import Blueprint, flash, render_template, redirect, url_for, session, request
from flask_login import login_user
from . import db 
from .models import User

auth = Blueprint('auth', __name__)

@auth.route("/kitchen/login")
def login_get():
    return render_template('login.html')

@auth.route('/kitchen/login', methods=['POST'])
def login_post():
    login = request.form['login']
    password = request.form['password']
    user = User.query.filter_by(username=str(login), password=str(password)).first()
    if not user:
        flash("Неправильный логин или пароль")
        return redirect(url_for('auth.login_get'))
    else:
        session['user'] = user
        login_user(user, remember=True)
        if user.is_admin==True:
            return redirect(url_for('admin.adminpanel'))
        else:
            return redirect(url_for('admin.kitchenpanel'))