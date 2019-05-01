from json import loads
from os import environ

from flask import (Flask, abort, make_response, redirect, render_template,
                   request, url_for)

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
    response = make_response(scoreboard.visualize())
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
    problems = eval(environ['problem_ids'])
    problem_name = loads(environ['problem_names'])
    app.run(host='0.0.0.0', port=int(environ['PORT']))
