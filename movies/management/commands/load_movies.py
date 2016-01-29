import os
import json
import requests
import getpass

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    """
        * Command to load all data in json to database
        * Spaces in genres and director names in json file is not considered
        * Hence duplicates may exist
        * Arguments:
            File to be loaded. imdb.json with exact path
            url of the path: ex: http://localhost:8000
        * In heroku you should run
            $ heroku run python manage.py load_movies /app/imdb.json http://moviesforall.herokuapp.com
    """
    args = '<config_file> <url>'

    def handle(self, *args, **kwargs):
        if args:
            file_path = args[0]
            url = args[1]
            username = raw_input('Enter admin username: ')
            password = getpass.getpass(prompt='Enter admin password: ')
            r = requests.post(url=url + '/user/login_token/',
                              data={'username': username, 'password': password})
            token = r.json()['token']
            headers = {'Authorization': 'Token ' + str(token), 'content-type': 'application/json'}
            if os.path.exists(file_path):
                with open(file_path, 'rb') as data_file:
                    json_data = json.load(data_file)
                    for data in json_data:
                        data['popularity'] = data['99popularity']
                        del data['99popularity']
                        r = requests.post(url=url + '/movies/', data=json.dumps(data), headers=headers)
                        print r
            else:
                return 'File not found'
        else:
            return 'No arguments provided'
