
from quickbot_func import * 


email_sender = 'bonniecruz4589@gmail.com'
email_password ='msvhwmxnmtxikamm'
email_receiver = 'bonniecruz4589@gmail.com'

username = 'a.romo1988@yahoo.com'
password = 'SEATTLE1!'

driver=start_chrome_driver()
login_session(driver,username,password)

while True:
    results = engine.execute("""SELECT reference_no FROM "tide_work" where customs_release_status !="CLEARED" or line_release_status !='PAID' or
            holds_status !="NONE" or addt_hold_info !='NONE'""").fetchall()
    if len(results) > 0:
        df = pd.DataFrame(results)
        df.columns = results[0].keys()
        containers = list(df['reference_no'])
        time.sleep(5)

        if (len(containers) >= 5):
            a = 0
            for i in range(math.ceil(len(containers) / 5)):
                listToStr = ' '.join([str(elem) for elem in containers[a: a + 5]])
                driver = start_session_container(listToStr, driver,username,password)

                information = information_extract(driver)
                a += 5
        else:
            listToStr = ' '.join([str(elem) for elem in containers])
            driver = start_session_container(listToStr, driver,username,password)
            information = information_extract(driver)


    else:
        print("No New Records Found in DATABASE")

    try:
        results = engine.execute("""SELECT * FROM "tide_work" where customs_release_status =="CLEARED" and line_release_status =='PAID' and
                holds_status =="NONE" and addt_hold_info =='NONE' and email =='No'""").fetchall()

        df = pd.DataFrame(results)
        
        df.columns = results[0].keys()
        df.rename(columns={'last_visit_bot': 'last_visit_tool'}, inplace=True)
        df.columns = df.columns.str.upper()
        for i in range(len(df)):
            email_det = df.iloc[i]
            new_df = pd.DataFrame(email_det)
            new_df = new_df.drop(new_df.index[17])

            text = new_df.to_html(header="true", classes='table table-stripped').replace('\n', '')
            text = text.replace('<td>', '<td class="th-style">')
            text = text.replace('<table border="1" class="table table-bordered">', '<table border="1" class="center">')
            text = re.sub('<th>[0-9]</th>', '', text).replace('<th></th>', '')

            subject = 'Success! Tool has found Record #' + email_det['REFERENCE_NO'] + '| Status Tracker'
            sent_flag = send_mail(subject, email_sender, email_receiver, email_det, text, email_password)

            print("Email Status: " + str(sent_flag))

            sql = """update 'tide_work' set email = (?) where reference_no = (?)"""

            engine.execute(sql, ('Yes', email_det['REFERENCE_NO']))

    except Exception as e:
        print('Exception occured',e,'No New Record Exists for Email')

    s = random.randint(20,60)
    print("BOT Sleeping for {} Seconds".format(s))
    time.sleep(s)