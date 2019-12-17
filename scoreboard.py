'''
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

'''
from asyncio import gather, get_event_loop
from functools import reduce

from flask import render_template
from pandas import merge, set_option

from online_judge import OnlineJudge

loop = get_event_loop()
set_option('display.max_colwidth', -1)


class Scoreboard:
    '''Handles a dataframe to build up a scoreboard.

    Attributes:
        problems: (list) A list of problem id which we are tracking.
        scoreboard: (Dataframe) A pandas.Dataframe that saves user attempts.
                    by student id.
        online_judge: (Online_Judge) An FOJ api wrapper.
    '''

    def __init__(self):
        self.oj = OnlineJudge()
        self.scoreboard = None

    def update(self):
        '''Update scoreboard using web crawler.
        Since api return a json message, we can use it to update scoreboard.

        '''
        tasks = []
        problems = self.oj.get_problems().keys()

        async def crawl(problem_id):
            return await loop.run_in_executor(None, self.oj.get_submission, problem_id)

        for problem_id in problems:
            task = loop.create_task(crawl(problem_id))
            tasks.append(task)

        df_list = loop.run_until_complete(gather(*tasks))
        self.scoreboard = reduce(lambda x, y: merge(x, y, left_index=True,
                                                    right_index=True, how='outer'), df_list)
        self.scoreboard.fillna(False, inplace=True)
        # TODO: change code below
        self.scoreboard.index.name = 'Student_ID'
        self.scoreboard['Total'] = self.scoreboard.sum(axis=1)
        self.scoreboard.sort_values(by=['Total', 'Student_ID'],
                                    inplace=True,
                                    ascending=[False, True])
        self.scoreboard.drop(columns='Total', inplace=True)
        self.scoreboard.index.name = None

        return self.scoreboard.applymap(lambda x: 'done' if x else 'clear').to_html(border=0, max_cols=None, max_rows=None, escape=False)

    def visualize(self):
        '''
        Make scoreboard table.

        Returns:
            (str) A html page to be rendered.
        '''


if __name__ == '__main__':
    css = """
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
      rel="stylesheet">
      <script>
        $(function () {
            $('td').each(function(i, v){
                if (v.textContent === "done"){
                    v.bgColor = "#D4EDC9"
                }else{
                    v.bgColor = "#FFE3E3"
                }
            })
            $('thead > tr > th').each(function(i, v){
                v.onclick = function(){window.open("https://oj.nctu.me/problems/" + v.textContent + "/", "_blank")}
            })
        })
      </script>

<style>
    html,
    body {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
    }

    th,
    td {
        text-align: center;
        width: 60px;
    }

    td{
        font-family: 'Material Icons'
    }
</style>
"""
    sb = Scoreboard()
    with open('D:/1.html', 'w') as f:
        f.write(css + sb.update())
