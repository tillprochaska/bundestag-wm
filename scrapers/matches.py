import requests;
from bs4 import BeautifulSoup;
import json;
from datetime import datetime, timezone, timedelta;
import pytz;
import re;
import logging;
logging.basicConfig(level=logging.INFO);

URL = 'https://www.fifa.com/worldcup/matches/';
DEST = './data/matches.json';

KNOCKOUT_TYPES = ['round of 16', 'quarter-finals', 'semi-finals', 'play-off for third place', 'final'];
TIMEZONE_OFFSET = {
    'Moscow': 3,
    'Ekaterinburg': 5,
    'St. Petersburg': 3,
    'Sochi': 3,
    'Kazan': 3,
    'Saransk': 3,
    'Kaliningrad': 2,
    'Samara': 4,
    'Rostov-On-Don': 3,
    'Nizhny Novgorod': 3,
    'Volgograd': 3,
};

def cleanStr(str):
    str = str.strip();
    str = re.sub('\s+', ' ', str);
    return str;

logging.info('Requesting match list…');
r = requests.get(URL);
doc = BeautifulSoup(r.text, 'html.parser');

now = datetime.now(pytz.utc);
matches = [];

for group in doc.select('.fi-matchlist .fi-mu-list'):
    # check if match is a group or knockout match
    matchType = cleanStr(group.select('.fi-mu-list__head__date')[0].text).lower();
    if matchType not in KNOCKOUT_TYPES:
        matchType = 'group'

    for match in group.select('.fi-mu'):
        city = cleanStr(match.select('.fi__info__venue')[0].text);

        # dates are in the following format: 01 Jul 2018 - 18:00 Local time
        dateFormat = '%d %b %Y - %H:%M Local time';
        date = datetime.strptime(cleanStr(match.select('.fi-mu__info__datetime')[0].text), dateFormat);
        zone = timezone(timedelta(hours = TIMEZONE_OFFSET[city]));
        date = date.replace(tzinfo = zone);

        matches.append({
            'type': matchType,
            'start': date.isoformat(),
            'end': (date + timedelta(minutes = 105)).isoformat(),
            'stadium': cleanStr(match.select('.fi__info__stadium')[0].text),
            'city': city,

            'team1': cleanStr(match.select('.fi-t .fi-t__nText')[0].text),
            'team2': cleanStr(match.select('.fi-t .fi-t__nText')[1].text),

            'score': cleanStr(match.select('.fi-s__scoreText')[0].text) if date < now else None,
        });

logging.info('Saved info on %d matches into %s.', len(matches), DEST);

with open(DEST, 'w+') as file:
    file.write(json.dumps(matches));
