'''
LICENSE: MIT license

This module can help us know about who can ask when
we have troubles in some buggy codes while solving problems.

'''
from pandas import DataFrame

from online_judge import Online_Judge


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
        temp = dict()
        for problem_id in self.problems:
            temp[problem_id] = self.online_judge.get_submission(problem_id)

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
                return '<span title="Attempted: {}">{}</span>'.format(x['penalty'], verdict[x['verdict']])
            else:
                return '<span title="Not Attempt">N/A</span>'

        def hightlight(submission):
            if submission.endswith('AC</span>'):
                return 'background-color: green'
            elif submission.endswith('N/A</span>'):
                return 'background-color: gray'
            else:
                return 'background-color: red'

        scoreboard = self.scoreboard.drop(columns=['Total']).applymap(
            make_verdict_string)
        scoreboard.index.name = None
        scoreboard.rename(lambda x: '<span title="{}">{}</span>'.format(self.problem_name[str(x)], x),
                          axis='columns', inplace=True)
        scoreboard = scoreboard.style.set_properties(
            **{'width': '60px', 'text-align': 'center'})

        return scoreboard.applymap(hightlight).render()
