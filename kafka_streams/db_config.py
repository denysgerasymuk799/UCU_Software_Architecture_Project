import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "<SECRET_KEY>"
    host = "127.0.0.1"
    database = "db_course_project"
    user = "postgres"
    password = "postgres"
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}/{}'.format(user, password, host, database)
