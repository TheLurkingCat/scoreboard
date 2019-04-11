from os import environ

from flask import (Flask, abort, make_response, redirect, render_template,
                   request, url_for)
from flask_sslify import SSLify
from pymongo import MongoClient

from scoreboard import Scoreboard

APP = Flask(__name__)
sslify = SSLify(APP)
APP.config.update(dict(PREFERRED_URL_SCHEME='https'))


@APP.route('/scoreboard', methods=['GET', 'POST'])
def visualize():
    url = 'mongodb+srv://FOJ_problem:VUzKFBG9UanMJ5o1@meow-jzx99.mongodb.net/meow'
    problems = MongoClient(url).FOJ.problems.find_one()['problems']

    if request.cookies.get('token') is None:
        token = request.form.get('token')
    else:
        token = request.cookies.get('token')

    if token == None:
        return render_template('index.html')

    try:
        scoreboard = Scoreboard(token, problems)
    except TypeError:
        return render_template('index.html')

    scoreboard.update()
    response = make_response(scoreboard.visualize())
    if request.cookies.get('token') is None:
        response.set_cookie('token', token)
    return response


@APP.route('/index', methods=['GET'])
def homepage():
    if request.cookies.get('token') is not None:
        return redirect(url_for('/scoreboard'), code=302)
    return render_template('index.html')


if __name__ == '__main__':
    APP.debug = False
    try:
        APP.run(host='0.0.0.0', port=int(environ['PORT']))
    except KeyError:
        APP.run()
