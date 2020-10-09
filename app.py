# Django Flask

# Create app.py that leads to every other file
# from database import cursor, db
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles

# from flask_mysqldb import MySQL
from flaskext.mysql import MySQL

from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime
from functools import wraps

import json

# to create an instance of the Flask class
app = Flask(__name__)   # placeholder for the current module
# app.debug = True  # So don't have to restart server each time, put app in debug mode
app.secret_key = 'maybe'


# Config MySQL
# ------------
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'alex'
# app.config['MYSQL_PASSWORD'] = 'Vester123'
# app.config['MYSQL_DB'] = 'myflaskapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Sets the default class to dictionary

# Initialize MySQL
# mysql = MySQL(app)  # Old???

# Second Config MySQL
# ------------
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'alex'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Vester123'
app.config['MYSQL_DATABASE_DB'] = 'myflaskapp'

mysql = MySQL()
mysql.init_app(app)

# Config SQLAlchemy
# ------------------
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Makes it so a warning message doesn't appear when we run the app (and all changes aren't tracked)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://alex:Vester123@localhost/myflaskapp'
# Is in the format of username, pass, locaiton, database

# Instantiating SQLAlchemy object
dbA = SQLAlchemy(app)
# session = db.session()
# curA = session.execute(sql).cursor

class Users(dbA.Model):  # has some methods that are inherited
    id = dbA.Column(dbA.Integer, primary_key=True)
    name = dbA.Column(dbA.String(50))
    username = dbA.Column(dbA.String(25))
    email = dbA.Column(dbA.String(50))
    password = dbA.Column(dbA.String(100))
    register_date = dbA.Column(dbA.DateTime, default=datetime.now)  # don't need parenthesis becuase this function will be executed
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
    cur2 = mysql.get_db().cursor()
    result = cur2.execute("SELECT * FROM articles")
    articles = cur2.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    cur2.close()
    # return render_template('articles.html', articles = Articles)  # if want to pass in data can add a second parameter - OLD placeholder

# Single article
@app.route('/article/<string:id>/')  # add angle brackets to make it dynamic. Tells this it wants a string with a parameter of 'id'
def article(id):
    cur2 = mysql.get_db().cursor()
    result = cur2.execute("SELECT * FROM articles WHERE id = %s", (id))
    article = cur2.fetchone()
    if result > 0:
        return render_template('article.html', article=article)
    else:
        msg = 'Article Does Not Exist'
        return render_template('article.html', msg=msg)
    cur2.close()



# Register form Class
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

# User register
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

        # ** My way
        # cursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        # db.commit()
        # cursor.close()

        flash('You are now registered and can log in', 'success')  # Want to send a flash message once registered. Also am creating a category of success

        return redirect(url_for('login'))  # redirect where you want to go after

    return render_template('register.html', form=form)

# User login
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

        # ** Using my way
        # result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:   # if any rows found
            # Get stored hash
            data = cur2.fetchone()
            password = data[3]

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # app.logger.info('PASSWORD MATCHED')  # How you log things to the consol
                # Passed login
                session['logged_in'] = True  # Will make the session true
                session['username'] = username # stores user name
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur2.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # check session for logged in value
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please log in', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()  # Kills the session
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
# Can add a "decorator" to any route you want so people can't access this link without being logged in
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur2 = mysql.get_db().cursor()
    result = cur2.execute("SELECT * FROM articles WHERE author = %s", (session['username']))
    articles = cur2.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    cur2.close()

# Article form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=255)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        author = session['username']
        body = form.body.data

        cur2 = mysql.get_db().cursor()
        cur2.execute("INSERT INTO articles(title, author, body) values(%s, %s, %s)", (title, author, body))
        mysql.get_db().commit()
        cur2.close()

        flash('Article added!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>/', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Get data
    cur2 = mysql.get_db().cursor()
    result = cur2.execute("SELECT * FROM articles WHERE id = %s", (id))
    article = cur2.fetchone()
    # Get form
    form = ArticleForm(request.form)
    # Populate fields - can do that from here
    form.title.data = article[1]
    form.body.data = article[3]

    if result > 0:
        if session['username'] == article[2]:
            if request.method == 'POST' and form.validate():
                title = request.form['title']
                body = request.form['body']

                cur2.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))
                mysql.get_db().commit()
                cur2.close()

                flash('Article edited!', 'success')

                return redirect(url_for('dashboard'))

            return render_template('edit_article.html', form=form)
        else:
            flash("You don't have permissions to edit this article", 'danger')
            return render_template('edit_article.html')
    else:
        flash('Article Does Not Exist', 'danger')
        return render_template('edit_article.html')


@app.route('/delete_article/<string:id>/', methods=['POST'])
@is_logged_in
def delete_article(id):
    cur2 = mysql.get_db().cursor()
    cur2.execute("DELETE FROM articles WHERE id = %s", (id))
    mysql.get_db().commit()
    cur2.close()

    flash('Article deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':  # checking if 'name' is equal to main which means it will be the script that is executed
    app.run(debug=True)  # if so run the app  # Added debug to have in debug mode



# For mysql downloaded 'pip install flask-mysqldb' for flask with mysql,
# as well as 'pip install Flask-WTF' for form validation
# as well as 'pip install passlib' to hash our passwords
