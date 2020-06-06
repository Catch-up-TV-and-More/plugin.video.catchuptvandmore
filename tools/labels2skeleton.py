#!/usr/bin/env python3

import sys

labels_f = open('../plugin.video.catchuptvandmore/resources/lib/labels.py', 'r')

labels = {}
start = False
last_key = None
for line in labels_f.readlines():
    if start:
        if '\'' in line and ':' in line:
            # key case
            last_key = line.split('\'')[1]
        elif '\'' in line and ',' in line:
            value = line.split('\'')[1]
            print(last_key + ' --> ' + value)
            labels[last_key] = value
    if 'LABELS = {' in line:
        start = True
    if start and '}' in line:
        start = False


filepath = sys.argv[1]
print()
print('File to migrate: ' + filepath)

skeleton = open(filepath, 'r')

new_file_content = []

for line in skeleton.readlines():
    if ': {' in line:
        last_key = line.split('\'')[1]
        print('Modify item_id: ' + last_key)
        if last_key not in labels:
            sys.exit(1)
    if 'label' in line:
        line = line.replace('TOTO', labels[last_key])
    new_file_content.append(line)

skeleton.close()

skeleton = open(filepath, 'w')

for line in new_file_content:
    skeleton.write(line)

skeleton.close()