# Database for Vester

import mysql.connector

config = {
	'user': 'alex',
	'password': 'Vester123',
	'host': 'localhost',
	'database': 'vester'
}

db = mysql.connector.connect(**config)  # identifies the database
cursor = db.cursor()  # used to execute queries


