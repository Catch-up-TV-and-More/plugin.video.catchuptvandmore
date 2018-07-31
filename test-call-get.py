# -*- coding: utf-8 -*-

import requests
import json


#Test .65 for find a card
# headers_value = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8', 'Connection': 'keep-alive', 'Host': 'pc.middleware.6play.fr', 'Origin': 'https://www.rtlplay.be', 'Referer': 'https://www.rtlplay.be/tvi', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36', 'x-client-release': 'm6group_web-4.39.3', 'x-customer-name': 'rtlbe'}
#headers_value = {'x-customer-name': 'rtlbe'}
#url = 'http://tbd.com/shows'

#Test .93 for find a card
#headers_value = {'charset': 'UTF-8', 'Content-type': 'application/json', 'Accept': 'application/json' ,'Connection': 'keep-alive' ,'AuthToken': '661baa4c-0688-4f14-986a-879ef77a7aa8' , 'X-Client-DN': 'DNP'}
#url = 'http://10.122.152.93:42000/api/1.7/subjects/000001/cards/FR2MC000012d84eff3698c4fcdbd082bb8b9a432fb'

url = 'http://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:video:paramountchannel.it:live&configtype=edge'
headers_value = {'referer': 'http://www.paramountchannel.it/tv/diretta', 'Content-Type': 'application/json' }

r = requests.get(url, headers = headers_value)
print 'Reponse : ' + r.text
print 'Status : ' + str(r.status_code)

url2 = 'http://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:video:paramountchannel.es:live&configtype=edge'
headers_value2 = {'referer': 'http://www.paramountchannel.es/programacion/en-directo', 'Content-Type': 'application/json' }

r2 = requests.get(url2, headers = headers_value2)
print 'Reponse 2 : ' + r2.text
print 'Status 2 : ' + str(r2.status_code)


url3 = 'http://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:video:paramountnetwork.com:live&configtype=edge'
headers_value3 = {'referer': 'http://www.paramountnetwork.com/live-tv', 'Content-Type': 'application/json' }

r3 = requests.get(url3, headers = headers_value3)
print 'Reponse 3 : ' + r3.text
print 'Status 3 : ' + str(r3.status_code)