"""
Get confirmed (i.e. yes vote) place-of-death relations from Google.
"""

import json
import requests
from urllib import parse
import tqdm


with open('.api_key', 'r') as f:
    API_KEY = f.read().strip()


def get_name(mid):
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'ids': mid,
        'limit': 1,
        'key': API_KEY
    }
    url = service_url + '?' + parse.urlencode(params)
    r = requests.get(url).json()
    if len(r['itemListElement']) != 1:
        return None
    try:
        return r['itemListElement'][0]['result']['name']
    except Exception:
        return None


if __name__ == "__main__":
    total = 0
    hits = 0
    with open('pod.tsv', 'w') as fout, \
            open('pod.json', 'w') as jsonout, \
            open('pod_gold.tsv', 'w') as goldf, \
            open('20131104-place_of_death.json', 'r') as fin:
        lines_i = list(enumerate(fin.readlines()))
        for i, line in tqdm.tqdm(lines_i):
            total += 1
            dat = json.loads(line)

            judgments = [x['judgment'] == 'yes'
                         for x in dat['judgments']]

            overall = (sum(judgments) / len(judgments)) > 0.5
            if not overall:
                continue

            sub_mid = dat['sub']
            obj_mid = dat['obj']
            # Get api call
            sub_name = get_name(sub_mid)
            obj_name = get_name(obj_mid)
            if sub_name is None or obj_name is None:
                print("Skipping")
                continue
            hits += 1
            if len(dat['evidences']) != 1:
                raise Exception(dat)
            dat = {
                'text': dat['evidences'][0]['snippet'],
                'sub': sub_name,
                'obj': obj_name,
                'n_raters': len(judgments),
                'rater_percent': 1 - (sum(judgments) / len(judgments)),
                'overall': -1,
            }
            fout.write('{}\t{}\n'.format('d' + str(i), dat['text']))
            jsonout.write('{}\n'.format(json.dumps(dat)))
            goldf.write('{}\t{}\t{}\t{}\n'.format('d' + str(i), dat['sub'],
                                                  dat['obj'], dat['overall']))
    print(total, hits)
