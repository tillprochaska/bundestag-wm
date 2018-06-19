import requests;
from bs4 import BeautifulSoup;
import json;
from datetime import datetime;
import re;
import logging;
logging.basicConfig(level=logging.INFO);

URL = 'https://www.bundestag.de/apps/plenar/plenar/conferenceweekDetail.form?year=2018&limit=50&week=';
SESSION_WEEKS = [24, 26, 27];
DEST = './data/debates.json';

def cleanStr(str):
    str = str.strip();
    str = re.sub('\s+', ' ', str);
    return str;

# final list of agenda items
items = [];

for week in SESSION_WEEKS:

    logging.info('Requesting session info for calendar week %d…', week);
    r = requests.get(URL + str(week));
    doc = BeautifulSoup(r.text, 'html.parser');

    for day in doc.select('.bt-table-data'):
        # parse date and session number from table header
        matches = re.search(r"(\d+)\.\s([A-Za-z]+)\s(\d{4})\s\((\d+)\.\s[A-Za-z]+\)", day.select('caption')[0].text);
        months = {
            'Juni': 6,
            'Juli': 7,
        };
        date = datetime(int(matches[3]), months[matches[2]], int(matches[1]));
        sessionNumber = int(matches[4]);

        for top in day.select('tbody tr'):
            time = top.select('td:nth-of-type(1) p')[0].text.split(':');
            start = date.replace(hour = int(time[0]), minute = int(time[1]));

            # check if agenda item has detailed description
            desc = top.select('td:nth-of-type(3) .bt-documents-description')[0];
            if len(desc.select('.bt-top-collapser-wrap')):
                # check if description contains link
                # to further information
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

        # Set end agenda item end datetime for convenience
        for i in range(len(items) - 1):
            if(i < len(items) and items[i]['sessionNumber'] == items[i+1]['sessionNumber']):
                items[i]['end'] = items[i+1]['start'];
            else:
                items[i]['end'] = items[i]['start'];

logging.info('Saved info on %d weeks of parliamentary sessions and %d agenda items into %s.', len(SESSION_WEEKS), len(items), DEST);

with open(DEST, 'w+') as file:
    file.write(json.dumps(items));
