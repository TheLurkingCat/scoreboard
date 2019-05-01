from os import environ

from flask import (Flask, abort, make_response, redirect, render_template,
                   request, url_for)
from pymongo import MongoClient

from scoreboard import Scoreboard

app = Flask(__name__)


@app.route('/scoreboard', methods=['GET', 'POST'])
def visualize():
    if request.cookies.get('token') is None:
        token = request.form.get('token')
    else:
        token = request.cookies.get('token')

    if token is None:
        return redirect(url_for('homepage', _external=True, _scheme='https'), code=302)

    try:
        scoreboard = Scoreboard(token, problems, problem_name)
    except TypeError:
        return redirect(url_for('homepage', _external=True, _scheme='https'), code=302)

    scoreboard.update()
    css = '<style type="text/css">html,body{margin:0;padding:0;height:100%;width:100%;}.row_heading{width:70px;}</style>'
    response = make_response(css + scoreboard.visualize())
    response.set_cookie('token', token, max_age=365 * 86400)

    return response


@app.route('/index', methods=['GET'])
def homepage():
    if request.cookies.get('token') is not None:
        return redirect(url_for('visualize', _external=True,  _scheme='https'), code=302)
    return render_template('index.html')


@app.route('/', methods=['GET'])
def redirect_homepage():
    return redirect(url_for('homepage', _external=True,  _scheme='https'), code=301)


if __name__ == '__main__':
    url = 'mongodb+srv://FOJ_problem:VUzKFBG9UanMJ5o1@meow-jzx99.mongodb.net/meow'
    database = MongoClient(url).FOJ
    problems = database.problems.find_one()['problems']
    problem_name = database.problem_name.find_one()
    try:
        app.run(host='0.0.0.0', port=int(environ['PORT']))
    except KeyError:
        app.run()
