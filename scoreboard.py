'''
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

'''
from asyncio import gather, get_event_loop

from pandas import DataFrame, set_option

from online_judge import Online_Judge

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

    def __init__(self, token, problems, problem_name):
        self.problems = problems
        self.problem_name = problem_name
        self.online_judge = Online_Judge(token)
        self.scoreboard = DataFrame()

    def update(self):
        '''Update scoreboard using web crawler.
        Since api return a json message, we can use it to update scoreboard.

        '''
        tasks = []

        async def crawl(problem_id):
            return await loop.run_in_executor(None, self.online_judge.get_submission, problem_id)

        for problem_id in self.problems:
            task = loop.create_task(crawl(problem_id))
            tasks.append(task)

        temp = dict(
            zip(self.problems, loop.run_until_complete(gather(*tasks))))

        self.scoreboard = DataFrame.from_dict(temp)
        self.scoreboard.index.name = 'Student_ID'
        self.scoreboard['Total'] = self.scoreboard.applymap(
            lambda x: x == x and x['verdict'] == 10).sum(axis=1)
        self.scoreboard.sort_values(
            by=['Total', 'Student_ID'], inplace=True, ascending=[False, True])

    def visualize(self):
        '''
        Make scoreboard table.

        Returns:
            (str) A html page to be rendered.
        '''
        def make_verdict_string(x):
            verdict = {4: 'CE', 5: 'RE', 6: 'MLE',
                       7: 'TLE', 8: 'OLE', 9: 'WA', 10: 'AC'}
            if x == x:
                return '<span class="{}" title="Attempted: {}">{}</span>'.format("right" if x['verdict'] == 10 else "wrong", x['penalty'], verdict[x['verdict']])
            else:
                return '<span class="none" title="Not Attempt">N/A</span>'

        css = """<style type="text/css">
                html,body{
                    margin:0;
                    padding:0;
                    height:100%;
                    width:100%;
                }
                .row_heading {width:70px}
                .wrong {background-color:red}
                .right {background-color:green}
                .none {background-color:gray}
                span{
                    text-align:center;
                    display:block;
                    width:60px;
                }
                th, td{
                    text-align:center;
                    width:60px;
                }
                a{
                    text-decoration:none;
                    color:black;
                }
                </style>
            """

        scoreboard = self.scoreboard.drop(columns=['Total']).applymap(
            make_verdict_string)
        scoreboard.index.name = None
        scoreboard.rename(lambda x: '<a href="https://oj.nctu.me/problems/{1}/" target="_blank" <span title="{0}">{1}</span></a>'.format(self.problem_name[str(x)], x),
                          axis='columns', inplace=True)
        return css + scoreboard.to_html(border=0, max_cols=None, max_rows=None, escape=False)
