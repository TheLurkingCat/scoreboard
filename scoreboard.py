'''
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

'''
from asyncio import gather, get_event_loop
from functools import reduce
from os.path import isfile

from flask import Flask, render_template
from numpy import isnan, nan
from pandas import HDFStore, Series, merge, set_option

from online_judge import OnlineJudge

loop = get_event_loop()
set_option('display.max_colwidth', -1)
app = Flask(__name__)


@app.context_processor
def table_display():
    icon = {
        5: 'bug_report',
        6: 'dynamic_feed',
        7: 'alarm',
        8: 'file_copy',
        9: 'clear',
        10: 'done',
        'help_outline': 'help_outline'
    }

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
        scoreboard = reduce(lambda x, y: merge(x, y, left_index=True,
                                               right_index=True, how='outer'), df_list)
        with HDFStore('cache.h5') as store:
            store.put('board', scoreboard)
            store.put('last', Series(last))

    def update():
        last = scoreboard = None
        with HDFStore('cache.h5') as store:
            last = store.get('last')[0]
            scoreboard = store.get('board')

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

        scoreboard.sort_index(axis=1, inplace=True)

        print("Update completed, saving to cache.")
        with HDFStore('cache.h5', mode='w') as store:
            store.put('board', scoreboard)
            store.put('last', Series(temp[0]['id']))
        print("Update finished!")

        return scoreboard

    def render():
        scoreboard = update()
        scoreboard['Total'] = scoreboard.applymap(
            lambda x: x == 10).sum(axis=1)
        scoreboard.index.name = 'Student_ID'
        scoreboard.sort_values(by=['Total', 'Student_ID'],
                               inplace=True,
                               ascending=[False, True])
        scoreboard.drop(columns='Total', inplace=True)
        scoreboard.index.name = None
        scoreboard = scoreboard.applymap(lambda x: icon.get(x, 'help_outline'))
        return scoreboard.to_html(border=0, max_cols=None, max_rows=None, escape=False)

    return {'render': render, 'generate': generate}


@app.route('/')
def index():
    return render_template('index.html', group_id=oj.config['Config']['group'])


if __name__ == '__main__':
    from waitress import serve
    oj = OnlineJudge()
    if not isfile('cache.h5'):
        print("Building cache...")
        table_display()['generate']()
        print("Cache built!")
    else:
        print("Cache found!")
    serve(app, host="0.0.0.0", port=8080)
