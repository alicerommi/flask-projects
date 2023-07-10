import re
from itertools import repeat
from functools import reduce  # Python3
import pandas as pd
import math
import os
import string, random
from datetime import date, datetime
from pytz import timezone
import pytz

import time
from IPython.display import HTML
import smtplib
import ssl
from email.message import EmailMessage
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from collections import defaultdict
from sqlalchemy import create_engine
import sqlalchemy as db


engine = db.create_engine('sqlite:///db.tide_work')
context = ssl.create_default_context()


def start_chrome_driver():
    driver = webdriver.Chrome(executable_path="C:/python_app/trapac-quickcheck-2/chromedriver")
    url = "https://b58.tideworks.com/fc-OICT/default.do"
    driver.get(url)
    driver.maximize_window()
    return driver
    print('Chrome driver started')


def login_session(driver,username,password):
    time.sleep(5)

    driver.find_element(By.ID, "j_username").send_keys(username)
    driver.find_element(By.ID, "j_password").send_keys(password)
    time.sleep(5)
    driver.find_element(By.ID, "signIn").click()
    time.sleep(2)
    try:
        if driver.find_element(By.CLASS_NAME, "modal-content").text != '':
            driver.find_element(By.XPATH, "//button[@class='btn btn-default']").click()
    except:
        pass
    time.sleep(5)
    driver.find_element(By.ID, "menu-import").click()
    time.sleep(5)

def start_session_container(listToStr, driver,username,password):
    try:
        login_session(driver,username,password)
        time.sleep(5)
    except:
        pass

    driver.find_element(By.XPATH, "//textarea[@id='numbers']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//textarea[@id='numbers']").clear()
    driver.find_element(By.XPATH, "//textarea[@id='numbers']").send_keys(listToStr)
    time.sleep(3)
    driver.find_element(By.ID, "search").click()
    time.sleep(1)
    return driver


def information_extract(driver):
    information = defaultdict(list)
    keys = ['containers', 'available', 'size', 'crs', 'lrs', 'holds', 'adi', 'tf', 'st', 'loc', 'vv', 'line',
            'ra','status_exists', 'hold', 'email', 'current_date', 'last_visit_bot']

    for con in driver.find_elements(By.XPATH, "//td[@colspan='5']//strong"):
        information['containers'].append(con.text)
        for k in keys[1:13]:
            information[k].append('Not Found')

        date_format = '%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))


        information['status_exists'].append('No')
        information['hold'].append('Yes')
        information['email'].append('No')
        information['current_date'].append(format(date.strftime(date_format)))
        information['last_visit_bot'].append(format(date.strftime(date_format)))

    inf_list = [(a.text.split('\n')) for a in driver.find_elements(By.XPATH, "//div[@id='result']//table//td") if
                len(a.text) > 1 and 'could not be found' not in a.text]

    point = 0
    found = int(len(inf_list) / 5)
    for i in range(found):
        information['containers'].append(inf_list[0 + point][0])
        information['available'].append(inf_list[1 + point][0])
        information['size'].append(inf_list[2 + point][0])

        result = [(i) for i in inf_list[3 + point] if ':' in i]
        for res, k in zip(result, keys[3:9]):
            st = res.split(':')
            information[k].append(st[1].strip())

        result = [(i) for i in inf_list[4 + point] if ':' in i]
        for res, k in zip(result, keys[9:13]):
            st = res.split(':')
            information[k].append(st[1].strip())

        date_format = '%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))


        information['status_exists'].append('Yes')
        information['hold'].append('No')
        information['email'].append('No')
        information['current_date'].append(format(date.strftime(date_format)))
        information['last_visit_bot'].append(format(date.strftime(date_format)))

        point = point + 5

    df = pd.DataFrame(information)
    for index, row in df.iterrows():
        sql = """update 'tide_work2' set search_status = (?),available = (?),size = (?),customs_release_status = (?)
                    ,line_release_status = (?),holds_status = (?),addt_hold_info = (?),total_fee=(?), satisfied_th = (?)
                    ,location = (?),ves_voy = (?),line_status = (?),trucker = (?),req_acc = (?),status_exists = (?)
                    ,hold = (?),email = (?),current_date = (?) ,last_visit_bot = (?)
                    where reference_no = (?)"""

        engine.execute(sql, ('Searched', row['available'], row['size'], row['crs']
                             , row['lrs'], row['holds'], row['adi'], row['tf'], row['st']
                             , row['loc'], row['vv'], row['line'], "Not", row['ra']
                             , row['status_exists'], row['hold'], row['email'], row['current_date'],
                             row['last_visit_bot'], row['containers']))

    sql = """update 'tide_work2' set hold='Yes' where customs_release_status!='CLEARED' and line_release_status !='PAID'
            and holds_status!='NONE' and addt_hold_info !='NONE' """

    engine.execute(sql)

    return information


def send_mail(subject, email_sender, email_receiver, email_det, text, email_password):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    html_string = '''<!DOCTYPE html>
                                <html>

                                <head>
                                    <title></title>
                                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                                    <meta name="viewport" content="width=device-width, initial-scale=1">
                                    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                                    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">

                                    <style type="text/css">
                                        @media screen {
                                            @font-face {
                                                font-family: 'Lato';
                                                font-style: normal;
                                                font-weight: 400;
                                                src: local('Lato Regular'), local('Lato-Regular'), url(https://fonts.gstatic.com/s/lato/v11/qIIYRU-oROkIk8vfvxw6QvesZW2xOQ-xsNqO47m55DA.woff) format('woff');
                                            }

                                            @font-face {
                                                font-family: 'Lato';
                                                font-style: normal;
                                                font-weight: 700;
                                                src: local('Lato Bold'), local('Lato-Bold'), url(https://fonts.gstatic.com/s/lato/v11/qdgUG4U09HnJwhYI-uK18wLUuEpTyoUstqEm5AMlJo4.woff) format('woff');
                                            }

                                            @font-face {
                                                font-family: 'Lato';
                                                font-style: italic;
                                                font-weight: 400;
                                                src: local('Lato Italic'), local('Lato-Italic'), url(https://fonts.gstatic.com/s/lato/v11/RYyZNoeFgb0l7W3Vu1aSWOvvDin1pK8aKteLpeZ5c0A.woff) format('woff');
                                            }

                                            @font-face {
                                                font-family: 'Lato';
                                                font-style: italic;
                                                font-weight: 700;
                                                src: local('Lato Bold Italic'), local('Lato-BoldItalic'), url(https://fonts.gstatic.com/s/lato/v11/HkF_qI1x_noxlxhrhMQYELO3LdcAZYWl9Si6vvxL-qU.woff) format('woff');
                                            }
                                        }

                                        /* CLIENT-SPECIFIC STYLES */
                                        body,
                                        table,
                                        td,
                                        a {

                                            -webkit-text-size-adjust: 100%;
                                            -ms-text-size-adjust: 100%;
                                        }

                                        table,
                                        td {
                                            mso-table-lspace: 0pt;
                                            mso-table-rspace: 0pt;
                                        }
                                        tr {
                                            mso-table-lspace: 0pt;
                                            mso-table-rspace: 0pt;
                                        }
                                        th {
                                        font-family: "Trebuchet MS", Verdana, sans-serif;
                                        font-style: normal;
                                        height: 40px;
                                        width: 260px;
                                        font-size: 17px;
                                        font-weight: 700;
                                        background: #2d2d71;
                                        color: white;
                                        text-align: center;
                                    }
                                    .th-style {
                                        font-family: "Trebuchet MS", Verdana, sans-serif;
                                        font-style: normal;
                                        font-size: 17px;
                                        height: 40px;
                                        width: 260px;
                                        font-weight: 700;
                                        background: white;
                                        color: black;
                                        text-color: black;
                                        text-align: center;
                                    }

                                        img {
                                            -ms-interpolation-mode: bicubic;
                                        }

                                        /* RESET STYLES */
                                        img {
                                            border: 0;
                                            height: auto;
                                            line-height: 100%;
                                            outline: none;
                                            text-decoration: none;
                                        }

                                        table {
                                            border-collapse: collapse !important;
                                        }

                                        body {
                                            height: 100% !important;
                                            margin: 0 !important;
                                            padding: 0 !important;
                                            width: 100% !important;
                                        }

                                        /* iOS BLUE LINKS */
                                        a[x-apple-data-detectors] {
                                            color: inherit !important;
                                            text-decoration: none !important;
                                            font-size: inherit !important;
                                            font-family: inherit !important;
                                            font-weight: inherit !important;
                                            line-height: inherit !important;
                                        }

                                        /* MOBILE STYLES */
                                        @media screen and (max-width:600px) {
                                            h1 {
                                                font-size: 32px !important;
                                                line-height: 32px !important;
                                            }
                                        }

                                        /* ANDROID CENTER FIX */
                                        div[style*="margin: 16px 0;"] {
                                            margin: 0 !important;
                                        }
                                    </style>
                                </head>

                                <body style="background-color: #f4f4f4; margin: 0 !important; padding: 0 !important;">
                                    <!-- HIDDEN PREHEADER TEXT -->
                                    <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: 'Lato', Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;"> We're thrilled to have you here! Get ready to dive into your new account.
                                    </div>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <!-- LOGO -->
                                        <tr>
                                            <td bgcolor="#FFA73B" align="center">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                                                    <tr>
                                                        <td align="center" valign="top" style="padding: 40px 10px 40px 10px;"> </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#2d2d71" align="center" style="padding: 0px 10px 0px 10px;">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                                                    <tr>
                                                        <td bgcolor="#ffffff" align="center" valign="top" style="padding: 40px 20px 20px 20px; border-radius: 4px 4px 0px 0px; color: #111111; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 400; letter-spacing: 4px; line-height: 48px;">
                                                            <h1 style="font-size: 48px; font-weight: 400; margin: 2;">''' + \
                  email_det['REFERENCE_NO'] + '''!</h1>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#f4f4f4" align="center" style="padding: 0px 10px 0px 10px;">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                                                    <tr>
                                                        <td bgcolor="#ffffff" align="left" style="padding: 20px 30px 40px 30px; color: #666666; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 25px;">
                                                            <p style="margin: 0;">Hey User, The tool found the record for <b>''' + \
                  email_det['REFERENCE_NO'] + '''</b>, Please see the further details:</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td bgcolor="#ffffff" align="center">

                                                             ''' + text + '''

                                                        </td>
                                                    </tr> <!-- COPY -->

                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#FFA73B" align="center" style="padding: 0px 10px 0px 10px;">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                                                    <tr>
                                                        <td bgcolor="#ffffff" align="center" valign="top" style="padding: 40px 20px 20px 20px; border-radius: 4px 4px 0px 0px; color: #111111; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 400; letter-spacing: 4px; line-height: 48px;">
                                                            <h1 style="font-size: 48px; font-weight: 400; margin: 2;">Thanks!</h1>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </body>

                                </html>'''

    em.set_content(html_string, subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        return 1