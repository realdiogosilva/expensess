from flask import Flask, render_template, request, redirect, Response
from functools import wraps
import psycopg2
import psycopg2.extras
import datetime
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl
import urllib.reques

app = Flask(__name__)

connection_string = os.environ['DATABASE_URL']

def check_auth(username, password):
    '''THIS IS FOR THE USERNAME AND PASSWORD VARIABLE'''
    return username == os.environ['USERNAME']; password == os.environ['PASSWORD'];

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def hello_world():
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM temperature ORDER BY reading_date DESC LIMIT 5")
        records = cursor.fetchall()

        cursor.execute("SELECT * FROM temperature ORDER BY temperature DESC LIMIT 1 ")
        highest = cursor.fetchall()
        max = highest[0]

        cursor.execute("SELECT * FROM temperature ORDER BY temperature ASC LIMIT 1")
        lowest = cursor.fetchall()
        low = lowest[0]

        return render_template('index.html', temperature=36, records=records, highest=max, lowest=low)

@app.route('/handle',methods=['POST'])
@requires_auth
def handle():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    locationsss = float(request.form['locationsss'])
    temperature = float(request.form['temperature'])
    current_date = datetime.datetime.now()
    query = 'INSERT INTO temperature (reading_date, locationsss, temperature)  VALUES (\'%s\', %s)' % (current_date, locationsss, temperature)
    cursor.execute(query)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/deletedatabase',methods=['POST'])
@requires_auth
def deletedatabase():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = 'DELETE FROM temperature'
    cursor.execute(query)
    conn.commit()
    conn.close()
    return redirect('/')

@app.template_filter('format_date')
def reverse_filter(record_date):
    return record_date.strftime('%Y-%m-%d %H:%M')

