import requests;
from bs4 import BeautifulSoup;
import json;
from datetime import datetime;
import re;

def cleanStr(str):
    str = str.strip();
    str = re.sub('\s+', ' ', str);
    return str;

weeks = [24, 26, 27];
# final list of agenda items
items = [];

for week in weeks:
    r = requests.get('https://www.bundestag.de/apps/plenar/plenar/conferenceweekDetail.form?year=2018&limit=50&week=' + str(week));
    doc = BeautifulSoup(r.text, 'html.parser');

    for day in doc.select('.bt-table-data'):
        matches = re.search(r"(\d+)\.\s([A-Za-z]+)\s(\d{4})\s\((\d+)\.\s[A-Za-z]+\)", day.select('caption')[0].text);
        months = {
            'Juni': 6,
            'Juli': 7,
        };
        date = datetime(int(matches[3]), months[matches[2]], int(matches[1]));
        number = matches[4];

        tops = [];
        sessionNumber = int(matches[4]);

        for top in day.select('tbody tr'):
            time = top.select('td:nth-of-type(1) p')[0].text.split(':');
            start = date.replace(hour = int(time[0]), minute = int(time[1]));

            desc = top.select('td:nth-of-type(3) .bt-documents-description')[0];

            if len(desc.select('.bt-top-collapser-wrap')):
                if(len(desc.select('button'))):
                    link = desc.select('button')[0]['data-url'];
                else:
                    link = None;

                topic = cleanStr(desc.select('.bt-top-collapser')[0].text);
                desc = cleanStr(desc.select('.bt-top-collapse p')[0].text);
            else:
                topic = cleanStr(desc.text);
                desc = None;
                link = None;

            items.append({
                'start': start.isoformat(),
                'end': None,
                'sessionNumber': sessionNumber,
                'topic': topic,
                'description': desc,
                'link': link,
            });

        for i in range(len(tops) - 1):
            if(i < len(tops)):
                tops[i]['end'] = tops[i+1]['start'];
        # Set end agenda item end datetime for convenience
        for i in range(len(items) - 1):
            if(i < len(items) and items[i]['sessionNumber'] == items[i+1]['sessionNumber']):
                items[i]['end'] = items[i+1]['start'];
            else:
                items[i]['end'] = items[i]['start'];

        sessions.append({
            'date': date.isoformat(),
            'number': int(number),
            'tops': tops,
        });

with open('./data/debates.json', 'w+') as file:
    file.write(json.dumps(sessions));
