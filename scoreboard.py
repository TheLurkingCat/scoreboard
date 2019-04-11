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

    def __init__(self, token, problems):
        self.problems = problems
        self.online_judge = Online_Judge(token)
        self.scoreboard = DataFrame()

    def update(self):
        '''Update scoreboard using web crawler.
        Since api return a json mas, we can use it to update scoreboard.

        '''
        temp = {}

        verdict = {4: 'CE', 5: 'RE', 6: 'MLE',
                   7: 'TLE', 8: 'OLE', 9: 'WA', 10: 'AC'}

        for problem_id in self.problems:
            temp[problem_id] = self.online_judge.get_submission(problem_id)

        self.scoreboard = DataFrame.from_dict(temp).applymap(
            lambda x: verdict[x] if x == x else 'N/A')

        self.scoreboard.index.name = 'Student_ID'
        self.scoreboard['Total'] = (self.scoreboard == 'AC').sum(axis=1)
        self.scoreboard.sort_values(
            by=['Total', 'Student_ID'], inplace=True, ascending=[False, True])

    def visualize(self):
        '''
        Make scoreboard table.

        Returns:
            (str) A html page to be rendered.
        '''

        def hightlight(scoreboard):
            color_list = []
            for submission in scoreboard:
                if submission == 'AC':
                    color_list.append('background-color: green')
                elif submission == 'N/A':
                    color_list.append('background-color: gray')
                else:
                    color_list.append('background-color: red')
            return color_list

        scoreboard = self.scoreboard.drop(columns=['Total'])
        scoreboard.index.name = ''

        scoreboard = scoreboard.style.set_properties(
            **{'width': '50px', 'text-align': 'center'})

        return scoreboard.apply(hightlight).render()
