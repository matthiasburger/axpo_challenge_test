import os

SECRET_KEY = os.getenv('SECRET_KEY')
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DATABASE_NAME = os.environ['DATABASE_NAME']
DB_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DATABASE_NAME}'
print("> " + DB_URI)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True
MYSQL_ROOT_PASSWORD = os.environ['MYSQL_ROOT_PASSWORD']
