from os import environ

from flask import (Flask, abort, make_response, redirect, render_template,
                   request, url_for)
from flask_sslify import SSLify
from pymongo import MongoClient

from scoreboard import Scoreboard

APP = Flask(__name__)
# sslify = SSLify(APP)


@APP.route('/scoreboard', methods=['GET', 'POST'])
def visualize():
    url = 'mongodb+srv://FOJ_problem:VUzKFBG9UanMJ5o1@meow-jzx99.mongodb.net/meow'
    problems = MongoClient(url).FOJ.problems.find_one()['problems']

    if request.cookies.get('token') is None:
        token = request.form.get('token')
    else:
        token = request.cookies.get('token')

    if token == None:
        return redirect(url_for('homepage', _external=True,  _scheme='https'), code=302)

    try:
        scoreboard = Scoreboard(token, problems)
    except TypeError:
        return redirect(url_for('homepage', _external=True,  _scheme='https'), code=302)

    scoreboard.update()
    response = make_response(scoreboard.visualize())
    response.set_cookie('token', token, max_age=365*86400)

    return response


@APP.route('/index', methods=['GET'])
def homepage():
    if request.cookies.get('token') is not None:
        return redirect(url_for('visualize', _external=True,  _scheme='https'), code=302)
    return render_template('index.html')


if __name__ == '__main__':
    try:
        APP.run(host='0.0.0.0', port=int(environ['PORT']))
    except KeyError:
        APP.run()
