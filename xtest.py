from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles

# from flask_mysqldb import MySQL
from flaskext.mysql import MySQL

from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maybe'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'alex'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Vester123'
app.config['MYSQL_DATABASE_DB'] = 'myflaskapp'
mysql = MySQL()
mysql.init_app(app)


cur2 = mysql.get_db().cursor()
username = 'alex'

# Get user by Username
result = cur2.execute("SELECT * FROM users")
print(result)
# if result > 0:   # if any rows found
#     # Get stored hash
#     data = cur2.fetchone()
#     password = data['password']





class Users(db.Model):  # has some methods that are inherited
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(25))
    email = db.Column(db.String(50))
    password = db.Column(db.String(100))
    register_date = db.Column(db.DateTime, default=datetime.now)  # don't need parenthesis becuase this function will be executed
# ------------------

Articles = Articles()

# When first run get "not found" because haven't created a route for home (or index)
@app.route('/')
def index():
    # return 'INDEXB'  # have to restart the server with ^C  (Ctrl+C)
      # Usuall don't have text but have a template, so need flask template module
      return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)  # if want to pass in data can add a second parameter

@app.route('/article/<string:id>/')  # add angle brackets to make it dynamic. Tells this it wants a string with a parameter of 'id'
def article(id):
    return render_template('article.html', id=id)

# Need to create a class for each form from wtforms documentaiton
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])   # inside is the readable version
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])  # All of these accept get requests (ie. going to page and loading), but also want POST requests
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():  # Check if POST or GET request
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))  # Need to encrypt

        # Create cursor
        # cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to db
        # mysql.connection.commit()

        # Close connection
        # cur.close()

        # Cursor test 2
        # -------------
        cur2 = mysql.get_db().cursor()
        cur2.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        mysql.get_db().commit()
        cur2.close()

        flash('You are now registered and can log in', 'success')  # Want to send a flash message once registered. Also am creating a category of success

        return redirect(url_for('login'))  # redirect where you want to go after

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password_candidate = request.form['password'] # put candidate because want correct password and compare

        # Create cursor
        cur2 = mysql.get_db().cursor()

        # Get user by Username
        result = cur2.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:   # if any rows found
            # Get stored hash
            data = cur2.fetchone()
            password = data['password']
    return render_template('login.html')

if __name__ == '__main__':  # checking if 'name' is equal to main which means it will be the script that is executed
    app.run(debug=True)
