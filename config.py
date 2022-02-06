import os
SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# 1st method
# SQLALCHEMY_DATABASE_URI = 'postgres:///fyyur'

# better method
class DatabaseURI:
    DATABASE_NAME = "fyyur"
    username = ''
    password = ''
    url = ''
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)


