import requests
import datetime
import json

def get_player_ids(skaters):
    teams = json.load(open('team-to-abv-mappings.json', 'r'))

    current_players = skaters.values()


    for team in teams:
        response = requests.get(f'https://api-web.nhle.com/v1/roster/{team}/current').json()
        for forward in response.get('forwards'):
            name = f'{forward.get('firstName').get('default')} {forward.get('lastName').get('default')}'
            if name in current_players:
                continue
            skaters.update({name: forward.get('id')})
        for d_man in response.get('defensemen'):
            name = f'{d_man.get('firstName').get('default')} {d_man.get('lastName').get('default')}'
            if name in current_players:
                continue
            skaters.update({name: d_man.get('id')})

    json.dump(skaters, open('skaters-id-map.json', 'w')) 

    def get_games():
        pass