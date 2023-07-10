import sqlalchemy as db
import pandas as pd

engine = db.create_engine('sqlite:///db.tide_work')

results = engine.execute("""SELECT * FROM "tide_work" where customs_release_status =="CLEARED" and line_release_status =='PAID' and
                    holds_status =='NONE' and addt_hold_info =='NONE' and email =='No'""").fetchall()

df = pd.DataFrame(results)
print(df)
# sql="""update 'tide_work' set email='No' where email=='No0'"""
# engine.execute(sql)
#
# results = engine.execute("""SELECT * FROM "tide_work" where customs_release_status =="CLEARED" and line_release_status =='PAID' and
#         holds_status =="NONE" and addt_hold_info =='NONE' and email =='No'""").fetchall()
#
# df = pd.DataFrame(results)
# print(df)
# user_email='admin@bonnie.com'
# password='admin123'
# sql = "DELETE FROM quick_check where reference_no == 'UACU8420310 UACU8202962 SGCU5268416 HLXU5266063'"
# engine.execute(sql)
# df = pd.DataFrame(results)
# df.columns = results[0].keys()
# sql = """insert into users(user_email,password,name,is_admin,creation_date) VALUES(?,?, ?, ?, ?);"""
#
# engine.execute(sql, ('admin@bonnie.com', "admin123",
#                      "Admin", "1", "07/01/2022 06:03:16 PDT"))

# email='a@gmail.com'
# sql="ALTER TABLE quick_check ADD is_delete varchar(255);"
# engine.execute(sql)
# results = engine.execute(
#     "SELECT * FROM users").fetchall()
# df = pd.DataFrame(results)
# df.columns = results[0].keys()
# sql = "SELECT * FROM users"
# results = engine.execute(sql).fetchall()
# df = pd.DataFrame(results)
# print(df)