'''
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

'''
from asyncio import gather, get_event_loop
from configparser import ConfigParser
from functools import reduce
from os.path import isfile

from flask import Flask, current_app, render_template
from numpy import isnan, nan
from pandas import HDFStore, Series, merge, set_option

from online_judge import OnlineJudge

app = Flask(__name__)


def generate():
    last = oj.get_last_submission(1)[0]['id']
    tasks = []
    problems = oj.get_problems().keys()

    async def crawl(problem_id):
        return await loop.run_in_executor(None, oj.get_submission, problem_id)

    for problem_id in problems:
        task = loop.create_task(crawl(problem_id))
        tasks.append(task)

    df_list = loop.run_until_complete(gather(*tasks))
    z = zip(*df_list)
    scoreboard = reduce(lambda x, y: merge(x, y, left_index=True,
                                           right_index=True, how='outer'), next(z))
    first = Series(next(z), index=next(z))
    for x, y in first.items():
        scoreboard[x][y] = 11
    with HDFStore('cache.h5') as store:
        store.put('board', scoreboard)
        store.put('last', Series(last))
        store.put('first', first)


def update():
    last = scoreboard = None
    with HDFStore('cache.h5') as store:
        last = store.get('last')[0]
        scoreboard = store.get('board')
        first = store.get('first')

    temp = oj.get_last_submission(8192)
    if temp[0]['id'] == last:
        print("Already up-to-date")
        return scoreboard

    if temp[-1]['id'] > last:
        print("Data too old, regenerating cache")
        generate()
        return update()

    print("Updating cache...")
    left = 0
    right = 8191
    mid = (left + right) // 2
    while left != right:
        if temp[mid]['id'] > last:
            right = mid
        else:
            left = mid + 1
        mid = (left + right) // 2

    problems = oj.get_problems()

    for i in range(left):
        name = oj.user.get(temp[i]['user_id'], None)
        problem_id = temp[i]['problem_id']
        verdict = temp[i]['verdict_id']
        if verdict > 4 and name is not None and problems.get(problem_id, None) is not None:
            if isnan(scoreboard.get(problem_id, {}).get(name, nan)):
                scoreboard.at[name, problem_id] = verdict
            else:
                scoreboard.at[name, problem_id] = max(
                    scoreboard.at[name, problem_id], verdict)
            if first[problem_id] != first[problem_id] and verdict == 10:
                first[problem_id] = name

    scoreboard.sort_index(axis=1, inplace=True)

    for x, y in first.items():
        scoreboard[x][y] = 11

    print("Update completed, saving to cache.")
    with HDFStore('cache.h5', mode='w') as store:
        store.put('board', scoreboard)
        store.put('last', Series(temp[0]['id']))
        store.put('first', first)
    print("Update finished!")

    return scoreboard


def render():
    scoreboard = update()
    scoreboard['Total'] = scoreboard.applymap(
        lambda x: x >= 10).sum(axis=1)
    scoreboard.index.name = 'Student_ID'
    scoreboard.sort_values(by=['Total', 'Student_ID'],
                           inplace=True,
                           ascending=[False, True])
    scoreboard.drop(columns='Total', inplace=True)
    scoreboard.index.name = None
    scoreboard = scoreboard.applymap(lambda x: icon.get(x, 'help_outline'))
    return scoreboard.to_html(border=0, max_cols=None, max_rows=None, escape=False)


@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


@app.route('/table_only/')
def table():
    return render_template('index.html', full=False, **param)


@app.route('/')
def index():
    return render_template('index.html', full=True, **param)


if __name__ == '__main__':
    if(isfile('app.config')):
        config = ConfigParser()
        config.read('app.config')
    else:
        raise FileNotFoundError('No configuration file found!')
    set_option('display.max_colwidth', None)
    loop = get_event_loop()
    oj = OnlineJudge(config)
    param = {
        'group_id': config['Config']['group'],
        'render': render
    }
    icon = {
        5: 'bug_report',
        6: 'dynamic_feed',
        7: 'alarm',
        8: 'file_copy',
        9: 'clear',
        10: 'done',
        11: 'check',
        'help_outline': 'help_outline'
    }
    if not isfile('cache.h5'):
        print("Building cache...")
        generate()
        print("Cache built!")
    else:
        print("Cache found!")
    app.run(port=8080)
