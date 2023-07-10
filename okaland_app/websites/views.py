from flask import Blueprint, render_template, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from . import db
import re
from datetime import date, datetime
from pytz import timezone
import pytz

import time
import pandas as pd
from flask import flash, session, redirect, url_for
import numpy as np
from .models import Note
import json
from flask import request
from sqlalchemy import create_engine
import sqlalchemy as db
from flask_session import Session
from datetime import datetime
from pytz import timezone
import pytz
from . import acct_send
import sqlalchemy as db
engine = db.create_engine('sqlite:///db.tide_work')


views = Blueprint('views', __name__)
auth = Blueprint('auth', __name__)


@views.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':
        flag = 0
        if not session.get("email"):
            return redirect(url_for('auth.login'))
        try:
            email=session['email']
            sql = "SELECT * FROM users where user_email== ?"
            results = engine.execute(sql, (email)).fetchall()
            df = pd.DataFrame(results)
            df.columns = results[0].keys()
            if (df.is_admin[0] == '1'):
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            results = engine.execute("""SELECT * FROM "tide_work2" where customs_release_status =="CLEARED" and line_release_status =='PAID' and
                    holds_status =='NONE' and addt_hold_info =='NONE'""").fetchall()

            df = pd.DataFrame(results)
            df.columns = results[0].keys()
            list_of_dics = df.to_dict(orient='records')

        except:
            list_of_dics = [{'reference_no': 'Not Found',
                              'search_status': 'Not Found',
                              'available': 'Not Found',
                              'size': 'Not Found',
                              'customs_release_status': 'Not Found',
                              'line_release_status': 'Not Found',
                              'holds_status': 'Not Found',
                              'addt_hold_info': 'Not Found',
                              'location': 'Not Found',
                              'status_exists': 'Not Found',
                              'hold': 'Not Found',
                              'email': 'Not Found',
                              'current_date': 'Not Found',
                              'last_visit_bot': 'Not Found'}]

        try:
            results2 = engine.execute("""SELECT * FROM "tide_work2" where customs_release_status !="CLEARED" or line_release_status !='PAID' or
                    holds_status !="NONE" or addt_hold_info !='NONE'""").fetchall()
            df2 = pd.DataFrame(results2)
            df2.columns = results2[0].keys()
            list_of_dics2 = df2.to_dict(orient='records')
        except:
            list_of_dics2 = [{'reference_no': 'Not Found',
                             'search_status': 'Not Found',
                             'available': 'Not Found',
                             'size': 'Not Found',
                             'customs_release_status': 'Not Found',
                             'line_release_status': 'Not Found',
                             'holds_status': 'Not Found',
                             'addt_hold_info': 'Not Found',
                             'location': 'Not Found',
                             'status_exists': 'Not Found',
                             'hold': 'Not Found',
                             'email': 'Not Found',
                             'current_date': 'Not Found',
                             'last_visit_bot': 'Not Found'}]
        date_format = '%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))

        return render_template("home.html", user='admin@quickbot.com', list_of_dics=list_of_dics,
                               list_of_dics2=list_of_dics2,update_time=format(date.strftime(date_format)))


@views.route('/save_container_form', methods=['POST'])
def save_container_form():
    container = request.form.get('container')

    exist=[]
    no_exist=[]
    exceed=[]
    data = {}
    if ('\n' in container):
        container = container.split('\n')
        for i in container:
            i=i.strip()
            if (len(i) < 13):
                sql = "SELECT * FROM 'tide_work2' where reference_no == ?"
                results = engine.execute(sql, i).fetchall()
                try:
                    df = pd.DataFrame(results)
                    df.columns = results[0].keys()
                    # flash('Container already exist', category='error')
                    # data.update({'success': 0, 'msg': 'Error! Some Containers already exist'})
                    exist.append(i.strip())
                except:
                    no_exist.append(i.strip())
            else:
                exceed.append(i.strip())
    else:
        if (len(container) < 13 and ',' not in container):
            sql = "SELECT * FROM 'tide_work2' where reference_no == ?"
            results = engine.execute(sql, container).fetchall()
            try:
                df = pd.DataFrame(results)
                df.columns = results[0].keys()
                # flash('Container already exist', category='error')
                # data.update({'success': 0, 'msg': 'Error! Some Containers already exist'})
                exist.append(container.strip())
            except:
                no_exist.append(container.strip())
        else:
            data.update({'success': 0, 'msg': 'Container length must be under 13 digit with No ,'})


    listToStr=''
    listToStr3=''

    if (len(exceed) > 0):
        listToStr3 = ', '.join([str(elem) for elem in exceed])
    if(len(exist)>0):
        listToStr = ', '.join([str(elem) for elem in exist])

    if (len(exceed) > 0 and (len(no_exist) < 1 or len(exist) < 1)):
        exceed = np.unique(exceed)
        listToStr3 = ', '.join([str(elem) for elem in exceed])
        data.update({'success': 0, 'msg': 'Error! Containers (' + listToStr3 + ') size exceed'})

    if (len(exist) > 0 and len(no_exist) < 1):
        exist = np.unique(exist)
        listToStr = ', '.join([str(elem) for elem in exist])
        data.update({'success': 0, 'msg': 'Error! Containers (' + listToStr + ') already exist'})

    if (len(exceed) > 0 and len(exist) > 0 and len(no_exist) == 0):
        print(no_exist)
        print(exceed)
        print(exist)
        exist = np.unique(exist)
        listToStr = ', '.join([str(elem) for elem in exist])
        exceed = np.unique(exceed)
        listToStr3 = ', '.join([str(elem) for elem in exceed])
        data.update({'success': 0,'msg': 'Containers (' + listToStr + ') already exist, Containers (' + listToStr3 + ') size exceed'})

    if(len(no_exist)>0):
        no_exist=np.unique(no_exist)
        listToStr2 = ', '.join([str(elem) for elem in no_exist])
        for i in no_exist:
            sql = """insert into tide_work2(reference_no,search_status,available,size,customs_release_status,
                    line_release_status,holds_status,addt_hold_info,total_fee,satisfied_th,
                    location,ves_voy,line_status,trucker,req_acc,status_exists
                    ,hold,email,current_date,last_visit_bot) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            engine.execute(sql,
                           (i, "Required", "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found",
                            "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found"
                            , "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found", "Not_Found"))

            if(len(listToStr)>0 and len(exceed) > 0):
                data.update({'success': 1,'msg': 'Containers (' + listToStr + ') already exist, Containers (' + listToStr3 + ') size exceed, Containers (' + listToStr2 + ') Saved Successfully'})
            elif (len(listToStr) > 0):
                data.update({'success': 1,'msg': 'Containers (' + listToStr + ') already exist, Containers (' + listToStr2 + ') Saved Successfully'})
            elif(len(exceed) > 0):
                data.update({'success': 1,'msg': 'Containers (' + listToStr3 + ') size exceed, Containers (' + listToStr2 + ') Saved Successfully'})
            else:
                data.update({'success': 1,'msg': 'Containers (' + listToStr2 + ') Saved Successfully'})

    return jsonify(data)


@views.route('/users', methods=['GET'])
def users():
    if request.method == 'GET':
        flag = 0
        if not session.get("email"):
            return redirect(url_for('auth.login'))

        try:
            results = engine.execute("SELECT * FROM users where is_admin !='1' ").fetchall()
            df = pd.DataFrame(results)
            df.columns = results[0].keys()
            list_users = df.to_dict(orient='records')
        except:
            list_users = [{'user_email': 'Not Found',
                           'name': 'Not Found',
                           'password': 'Not Found',
                           'is_admin': 'Not Found',
                           'creation_date': 'Not Found'}]

        return render_template("users.html", user='admin@quickbot.com', list_users=list_users)


@views.route('/save_users', methods=['POST'])
def save_users():
    user_email = request.form.get('user_email')
    data = {}
    sql = "SELECT * FROM 'users' where user_email == ?"
    results = engine.execute(sql, user_email).fetchall()
    try:
        df = pd.DataFrame(results)
        df.columns = results[0].keys()
        # flash('Container already exist', category='error')
        data.update({'success': 0, 'msg': 'Error! Users already exist'})
    except:
        user_email = request.form.get('user_email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_admin = False
        matchs = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if (re.match(matchs, user_email)):
            date_format = '%m/%d/%Y %H:%M:%S %Z'
            date = datetime.now(tz=pytz.utc)
            date = date.astimezone(timezone('US/Pacific'))

            # creation_date = request.form.get('creation_date')

            sql = """insert into users(user_email,name,password,is_admin,creation_date) VALUES (?,?,?,?,?);"""

            engine.execute(sql, (user_email, name, password, is_admin, date.strftime(date_format)))
            data.update({'success': 1, 'msg': 'Account! Created Successfully'})
            acct_send.send_this_email(user_email, name, password, 'Created', user_email)
            # send_this_email(user_email, name, password)
        else:
            data.update({'success': 0, 'msg': 'Error! Please follow email format'})
    return jsonify(data)


@views.route("/update_ref", methods=["POST", "GET"])
def update_ref():
    data = {}
    if request.method == 'POST':
        try:
            reference = request.form['reference']
            reference_new = request.form['reference_new']
            print(reference, reference_new)
            sql = "SELECT * FROM 'tide_work2' where reference_no == ?"
            results = engine.execute(sql, reference_new).fetchall()
            try:
                df = pd.DataFrame(results)
                df.columns = results[0].keys()
                data.update({'success': 0, 'msg': 'Error! Refernce Number already exist'})
            except:
                sql = "UPDATE tide_work2 set reference_no=? where reference_no='" + reference + "'"
                engine.execute(sql, reference_new)
                data.update({'success': 1, 'msg': 'Reference! Updated Successfully'})
        except:
            data.update({'success': 0, 'msg': 'Error! Please enter correct information'})
        return jsonify(data)


@views.route("/delete_ref/<val>", methods=["POST", "GET"])
def delete_ref(val):
    data = {}
    if request.method == 'POST':
        try:
            print(val)
            sql = "DELETE FROM tide_work2 WHERE reference_no='" + val + "'"
            engine.execute(sql)
            data.update({'success': 1, 'msg': 'Reference! Delete Successfully'})
        except:
            data.update({'success': 0, 'msg': 'Error! There is an error'})
        return jsonify(data)


@views.route("/action", methods=["POST", "GET"])
def action():
    data = {}

    if request.method == 'POST':
        try:
            email1 = request.form['email1']
            username = request.form['username1']
            password = request.form['password1']
            sql = "UPDATE users set name=?, password= ? where user_email='" + email1 + "'"
            engine.execute(sql, (username, password))
            data.update({'success': 1, 'msg': 'Account! Updated Successfully'})
            acct_send.send_this_email(email1, username, password, 'Updated', email1)

        except:
            data.update({'success': 0, 'msg': 'Error! Please enter correct information'})
        return jsonify(data)


@views.route("/delete/<val>", methods=["POST", "GET"])
def delete(val):
    data = {}

    if request.method == 'POST':
        try:
            sql = "DELETE FROM users WHERE user_email='" + val + "'"
            engine.execute(sql)
            data.update({'success': 1, 'msg': 'Account! Delete Successfully'})
        except:
            data.update({'success': 0, 'msg': 'Error! There is an error'})
        return jsonify(data)
