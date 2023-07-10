import sqlalchemy as db
engine=db.create_engine('sqlite:///db.quick_check')
engine.execute(""" CREATE TABLE users ("user_email" VARCHAR,
"password" VARCHAR,
"name" VARCHAR,
"is_admin" VARCHAR,
"creation_date" VARCHAR);""")
