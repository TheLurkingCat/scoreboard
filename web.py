from os import environ

from flask import (Flask, abort, make_response, redirect, render_template,
                   request, url_for)
from pymongo import MongoClient

from scoreboard import Scoreboard

APP = Flask(__name__)


@APP.route('/scoreboard', methods=['GET', 'POST'])
def visualize():
    url = 'mongodb+srv://FOJ_problem:VUzKFBG9UanMJ5o1@meow-jzx99.mongodb.net/meow'
    problems = MongoClient(url).FOJ.problems.find_one()['problems']

    if request.cookies.get('token') is None:
        token = request.form.get('token')
    else:
        token = request.cookies.get('token')

    if token == None:
        redirect('/', code=302)

    try:
        scoreboard = Scoreboard(token, problems)
    except TypeError:
        abort(401)

    scoreboard.update()
    response = make_response(scoreboard.visualize())
    if request.cookies.get('token') is None:
        response.set_cookie('token', token)
    return response


@APP.before_request
def force_https():
    if request.endpoint in APP.view_functions and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))


@APP.route('/', methods=['GET'])
def homepage():

    if request.cookies.get('token') is not None:
        return redirect('/scoreboard', code=302)
    return render_template('index.html')


if __name__ == '__main__':
    APP.debug = False
    try:
        APP.run(host='0.0.0.0', port=int(environ['PORT']))
    except KeyError:
        APP.run()
