import requests
import Constants


def get_events():
    response = requests.get(Constants.GANDR_URL)
    return [
        e['type_string'] + ': ' + e['name'] + (', ' + e['diff_string'] if e['diff_string'] else '')
        for e in sorted(response.json(), key=lambda e: e['type'])
    ]
