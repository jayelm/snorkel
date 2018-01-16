#!/usr/bin/env python

import requests
import csv
from io import StringIO

world_cities = requests.get('https://raw.githubusercontent.com/datasets/world-cities/master/data/world-cities.csv').text

f = StringIO(world_cities)
reader = csv.reader(f, delimiter=',')

all_rows = set()

for row in reader:
    all_rows.add(row[0])
    all_rows.add(row[1])
    all_rows.add(row[2])

all_rows = sorted(list(all_rows))
all_rows = [x for x in all_rows if x]
with open('locs.txt', 'w') as fout:
    print('\n'.join(all_rows), file=fout)
