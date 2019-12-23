'''
LICENSE: MIT license

This module is made to interact with FOJ api.

'''
import json
import re
from collections import Counter, defaultdict
from configparser import ConfigParser

import pandas as pd
from numpy import isnan, nan
from requests import get


class OnlineJudge:
    '''Some wrapped functions to interact with FOJ api.

    Attributes:
        api: (str) Url of FOJ's api.
        cookies: (dict) You need token to access FOJ.
        user: (dict) An user_id to student_id mapping dictionary.
    '''
    api = 'https://api.oj.nctu.me/{}'

    def __init__(self, config):
        self.config = config
        self.cookies = {'token': config['Authorize']['token']}
        if self.validate():
            self.user = self.get_user()
        else:
            raise ValueError('Invalid authorization')

    def validate(self):
        group_id = self.config['Config']['group']
        url = self.api.format('groups/{}/users/'.format(group_id))
        response = get(url.format(group_id), cookies=self.cookies)
        data = json.loads(response.text)['msg']
        if data == 'Permission Denied.':
            print(data)
            return False
        print('Authorized')
        if isinstance(self.config, ConfigParser):
            self.config.set('Authorize', 'token',
                            response.cookies['token'][1:-1])
            with open('app.config', 'w') as cfg:
                self.config.write(cfg)
        return True

    def get_data(self, url, params=None):
        group_id = self.config['Config']['group']
        if params is None:
            data = json.loads(
                get(url.format(group_id), cookies=self.cookies).text)
        else:
            params['group_id'] = group_id
            data = json.loads(
                get(url, cookies=self.cookies, params=params).text)
        return data['msg']

    def get_last_submission(self, count):
        params = {'group_id': None,
                  'count': count}
        url = self.api.format('submissions/')
        data = self.get_data(url, params)['submissions']
        return data

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
            (DataFrame): Users who passed the problem.
        '''
        params = {'group_id': None,
                  'problem_id': problem_id,
                  'count': '1048576'}
        url = self.api.format('submissions/')
        data = self.get_data(url, params)['submissions']
        table = pd.DataFrame(columns=[problem_id], dtype='float16')
        for submission in data:
            if submission['verdict_id'] > 4:
                name = self.user.get(submission['user_id'], None)
                if name is not None:
                    if isnan(table[problem_id].get(name, nan)):
                        table.at[name, problem_id] = submission['verdict_id']
                    else:
                        table.at[name, problem_id] = max(
                            table.at[name, problem_id], submission['verdict_id'])

        return table
