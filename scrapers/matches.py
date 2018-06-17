import requests;
from bs4 import BeautifulSoup;
import json;
from datetime import datetime;
import pytz;
from dateutil import parser;
import re;

r = requests.get('https://www.fifa.com/worldcup/matches/');
doc = BeautifulSoup(r.text, 'html.parser');

now = datetime.now(pytz.utc);
groups = [];

for group in doc.select('.fi-matchlist .fi-mu-list'):
    name = group.select('.fi-mu-list__head__date')[0].text.strip();
    name = re.sub('\s+', ' ', name);
    matches = [];

    for match in group.select('.fi-mu'):
        date = parser.parse(match.select('.fi-mu__info__datetime')[0]['data-utcdate']);

        matches.append({
            'date': date.isoformat(),
            'stadium': match.select('.fi__info__stadium')[0].text.strip(),
            'city': match.select('.fi__info__venue')[0].text.strip(),

            'team1': match.select('.fi-t .fi-t__nText')[0].text.strip(),
            'team2': match.select('.fi-t .fi-t__nText')[1].text.strip(),

            'score': match.select('.fi-s__scoreText')[0].text.strip() if date < now else None,
        });

    groups.append({
        'name': name,
        'matches': matches,
    });

with open('./data/matches.json', 'w+') as file:
    file.write(json.dumps(groups));
