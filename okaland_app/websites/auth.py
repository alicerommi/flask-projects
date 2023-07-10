from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
import functools
from flask_session import Session
from sqlalchemy import create_engine
import sqlalchemy as db
import pandas as pd

engine = db.create_engine('sqlite:///db.tide_work')

auth = Blueprint('auth', __name__)
views = Blueprint('views', __name__)


@auth.route('/', methods=['GET', 'POST'])
def login():
    data = {}
    data.update({'success': 1, 'msg': 'Account! Login Successfully'})
    if session.get("email"):
        return redirect(url_for('views.home'))
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        sql = "SELECT * FROM users where user_email== ? and password== ?"
        results = engine.execute(sql, (email, password)).fetchall()
        df = pd.DataFrame(results)
        if request.method == 'POST':
            if len(df) == 1:
                session["email"] = request.form.get("email")
                session['is_login'] = True
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Email and Password, try again.', category='error')
                data.update({'success': 0, 'msg': 'Incorrect Email and Password, try again.'})
    return render_template("login.html", dataset=data, is_login=True)


@auth.route('/logout')
def logout():
    session["email"] = None
    return redirect(url_for('auth.login'))
