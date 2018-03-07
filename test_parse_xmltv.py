# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import os
import time

channels = None
if os.path.exists('./xmltv.xml'):
    print "Fichier xmltv trouvé"
    tree = ET.parse('./xmltv.xml')
    root = tree.getroot()
    channels = root.findall('channel')

print "ROOT :" + root.tag

current_time_string = time.strftime('%Y%m%d%H%M%S')
current_time_utc = int(time.strftime('%Y%m%d%H%M%S'))
current_time_utc_offset = int(time.strftime('%z'))
current_time = current_time_utc + current_time_utc_offset

print "Current time " + str(current_time_utc)
print "Current utc offset string " + time.strftime('%z')
print "Current utc offset " + str(int(time.strftime('%z')))
print "Current utc offset " + str(int('-0100'))

for programme in root.findall('programme'):
    programme_start_s = programme.get('start')
    programme_start = int(programme_start_s.split()[0]) + int(programme_start_s.split()[1])
    programme_stop_s = programme.get('stop')
    programme_stop = int(programme_stop_s.split()[0]) + int(programme_stop_s.split()[1])
    if current_time >= programme_start and current_time <= programme_stop:
    	print "Programme time start " + programme.find('title').text