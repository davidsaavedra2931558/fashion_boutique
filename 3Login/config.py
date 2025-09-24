# config.py

class Config:
    # This line of code is setting the SQLALCHEMY_DATABASE_URI configuration variable to a specific
    # database URI. In this case, it is specifying a MySQL database connection using the PyMySQL
    # driver, with the username 'root', an empty password, connecting to the localhost on port 3306,
    # and using the database named 'login'. This URI will be used by the application to connect to the
    # specified database.
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False