from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, abort, session

app = Flask('__file__')

app.config.from_object('config')
db = SQLAlchemy(app)

class Hello(db.Model):
	id = db.Column('id',db.Integer(),primary_key=True)
	name = db.Column('name',db.String())

@app.route('/hello')
def hell():
	return render_template('hello.html')









if __name__ == "__main__":
	app.run(debug=True)