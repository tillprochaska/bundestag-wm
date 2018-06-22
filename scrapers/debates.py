import requests;
from bs4 import BeautifulSoup;
import json;
from datetime import datetime;
import re;
import collections;
import logging;
logging.basicConfig(level=logging.INFO);

URL = 'https://www.bundestag.de/apps/plenar/plenar/conferenceweekDetail.form?year=2018&limit=50&week=';
SESSION_WEEKS = [24, 26, 27];
DEST = './data/debates.json';
STOP_WORDS = [
    'der', 'die', 'das',
    'bericht', 'drucksache', 'drucksachen',
    'beratung', 'stellungnahme', 'vorschlag', 'änderung', 'antrag', 'namentliche',
    'fration', 'ausschuss',
];

def cleanContent(element):
    # replace <br> tags with line breaks
    for br in element.find_all('br'):
        br.replace_with('\n');

    text = element.text;
    text = text.strip();
    text = re.sub('\n\n+', '\n', text);
    text = re.sub('[\r\t ]+', ' ', text);
    return text;

# final list of agenda items
items = [];
# list all words in order to find most commong words
words = [];

for week in SESSION_WEEKS:

    logging.info('Requesting session info for calendar week %d…', week);
    r = requests.get(URL + str(week));
    doc = BeautifulSoup(r.text, 'html.parser');

    for day in doc.select('.bt-table-data'):
        # parse date and session number from table header
        matches = re.search(r'(\d+)\.\s([A-Za-z]+)\s(\d{4})\s\((\d+)\.\s[A-Za-z]+\)', day.select('caption')[0].text);
        months = {
            'Juni': 6,
            'Juli': 7,
        };
        date = datetime(int(matches[3]), months[matches[2]], int(matches[1]));
        sessionNumber = int(matches[4]);

        for top in day.select('tbody tr'):
            organizationalTypes = ['Sitzungseröffnung', 'Sitzungsunterbrechung', 'Sitzungsende'];
            time = top.select('td:nth-of-type(1) p')[0].text.split(':');
            start = date.replace(hour = int(time[0]), minute = int(time[1]));
            vote = False;
            article = None;

            # check if agenda item has detailed description
            desc = top.select('td:nth-of-type(3) .bt-documents-description')[0];
            if len(desc.select('.bt-top-collapser-wrap')):

                # check if description contains link to further information
                if(len(desc.select('button'))):
                    link = desc.select('button')[0]['data-url'];
                    print('Requesting further info for agenda item…');
                    r = requests.get('https://www.bundestag.de' + link);
                    doc = BeautifulSoup(r.text, 'html.parser');

                    content = doc.select('.bt-artikel .bt-videoplayer + .bt-standard-content p')
                    if(len(content)):
                        article = cleanContent(doc.select('.bt-artikel .bt-bild-standard + .bt-standard-content div p, .bt-artikel .bt-videoplayer + .bt-standard-content p')[0]);
                else:
                    link = None;
                    
                topic = cleanContent(desc.select('.bt-top-collapser')[0]);
                desc = cleanContent(desc.select('.bt-top-collapse p')[0]);

                # check if agenda item includes parliament voting
                vote = re.subn(r'Namentliche Abstimmunge?n?', '', desc, flags=re.IGNORECASE);
                if(vote[1] != 0):
                    desc = vote[0];
                    vote = True;
                else:
                    vote = False;

                if(desc == topic):
                    desc = None;

            else:
                topic = cleanContent(desc);
                desc = None;
                link = None;

            # split title into list of words
            topicWords = re.findall(r'\b[A-Z\u00c4\u00d6\u00dc].*?\b', topic);
            words.extend([ x.lower() for x in topicWords ]);
            # if(desc):
            #     descWords = re.findall(r'\b[A-Z\u00c4\u00d6\u00dc].*?\b', desc);
            #     words.extend([ x.lower() for x in descWords ]);

            items.append({
                'type': 'organizational' if topic in organizationalTypes else 'main',
                'vote': vote,
                'start': start.isoformat(),
                'end': None,
                'sessionNumber': sessionNumber,
                'topic': topic,
                'description': article if article else desc,
                'link': link,
            });

        # Set end agenda item end datetime for convenience
        for i in range(len(items) - 1):
            if(i < len(items) and items[i]['sessionNumber'] == items[i+1]['sessionNumber']):
                items[i]['end'] = items[i+1]['start'];
            else:
                items[i]['end'] = items[i]['start'];

logging.info('Saved info on %d weeks of parliamentary sessions and %d agenda items into %s.', len(SESSION_WEEKS), len(items), DEST);

words = collections.Counter(filter(lambda x: x not in STOP_WORDS, words));

with open(DEST, 'w+') as file:
    file.write(json.dumps(items));
