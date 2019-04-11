'''
LICENSE: MIT license

This module is made to interact with FOJ api.

'''
from collections import defaultdict
from json import loads
from re import match

from requests import get


class Online_Judge:
    '''Some wrapped functions to interact with FOJ api.

    Attributes:
        api: (str) Url of FOJ's api.
        cookies: (dict) You need token to access FOJ.
        user: (dict) An user_id to student_id mapping dictionary.
    '''

    def __init__(self, token):
        self.api = 'https://api.oj.nctu.me/'
        self.cookies = {'token': token}
        self.user = self.get_user()

    def get_user(self):
        '''Create an user_id to student_id mapping dictionary using api.

        Returns:
            (dict) An user_id to student_id mapping dictionary.
        '''
        url = self.api + 'groups/11/users/'
        data = get(url, cookies=self.cookies).text
        return {user['id']: user['name'] for user in loads(data)['msg'] if match(r'0(\d){6}', user['name'])}

    def get_submission(self, problem_id):
        '''Fetch submission data using FOJ api.

        Args:
            problem_id: (int) Id of the problem you want to fetch.

        Returns:
            (defaultdict): The submission state of the problem_id.
        '''
        submission_code = 'submissions/?group_id=11&problem_id={}&count=1048576'
        url = self.api + submission_code.format(problem_id)
        data = loads(get(url, cookies=self.cookies).text)['msg']['submissions']
        table = defaultdict(int)

        for submission in data:
            try:
                table[self.user[submission['user_id']]] = max(
                    submission['verdict_id'], table[self.user[submission['user_id']]])
            except KeyError:
                pass

        return table
