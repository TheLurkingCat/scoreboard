'''
LICENSE: MIT license

This module is made to interact with FOJ api.

'''
import json
import re
from collections import Counter, defaultdict
from configparser import ConfigParser

from requests import get


class OnlineJudge:
    '''Some wrapped functions to interact with FOJ api.

    Attributes:
        api: (str) Url of FOJ's api.
        cookies: (dict) You need token to access FOJ.
        user: (dict) An user_id to student_id mapping dictionary.
    '''
    config = ConfigParser()
    config.read('app.config')
    api = 'https://api.oj.nctu.me/{}'
    cookies = {'token': config['Authorize']['token']}

    def __init__(self):
        self.user = self.get_user()

    def get_data(self, url, params=None):
        group_id = self.config['Config']['group']
        if params is None:
            data = json.loads(
                get(url.format(group_id), cookies=self.cookies).text)
        else:
            params['group_id'] = group_id
            data = json.loads(
                get(url, cookies=self.cookies, params=params).text)
        # TODO check response.
        return data['msg']

    def get_user(self):
        '''Create an user_id to student_id mapping dictionary using api.

        Returns:
            (dict) An user_id to student_id mapping dictionary.
        '''
        data = self.get_data(self.api.format('groups/{}/users/'))
        blacklist = self.config['Config']['blacklist'].split()
        whitelist = re.compile(self.config['Config']['whitelist'])
        return {user['id']: user['name']
                for user in data
                if whitelist.match(user['name']) and
                user['name'] not in blacklist}

    def get_problems(self):
        data = self.get_data(self.api.format('groups/{}/problems/'))
        excluded_problems = self.config['Config']['excluded_problems'].split()
        title_mask = re.compile(self.config['Config']['extract_title_re'])
        ret = {}
        for problem in data['data']:
            title = title_mask.match(problem['title'])
            if problem['id'] not in excluded_problems and title is not None:
                ret[problem['id']] = title.group(1)
        return ret

    def get_submission(self, problem_id):
        '''Fetch submission data using FOJ api.

        Args:
            problem_id: (int) Id of the problem you want to fetch.

        Returns:
            (defaultdict): The submission state of the problem_id.
        '''
        params = {'group_id': None,
                  'problem_id': problem_id,
                  'count': '1048576'}
        url = self.api.format('submissions/')
        data = self.get_data(url, params)['submissions']
        return data
        data.reverse()
        table = defaultdict(Counter)
        for submission in data:
            try:
                if 3 < submission['verdict_id'] < 11:
                    if table[self.user[submission['user_id']]]['verdict'] != 10:
                        table[self.user[submission['user_id']]]['penalty'] += 1
                    table[self.user[submission['user_id']]]['verdict'] = max(
                        table[self.user[submission['user_id']]]['verdict'], submission['verdict_id'])
            except KeyError:
                pass

        return table


if __name__ == '__main__':
    oj = OnlineJudge()
    print(oj.get_submission(1018))
