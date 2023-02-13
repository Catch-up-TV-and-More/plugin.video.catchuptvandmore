# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

# called my5.py in dev tree, python3 kodi 19/20


from __future__ import unicode_literals

import re
import json
import base64
import xbmc
import urlquick
import urllib
import time
import ctypes
import math

# MY5-001: import xbmvvfs, os
import os
import xbmcvfs

#from kodi_six import xbmcgui
from codequick import Listitem, Resolver, Route
#import urlquick

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode



from resources.lib.kodi_utils import get_kodi_version, get_selected_item_art, get_selected_item_label, get_selected_item_info, INPUTSTREAM_PROP
from resources.lib.menu_utils import item_post_treatment

from resources.lib import resolver_proxy, web_utils
from resources.lib.resolver_proxy import get_stream_with_quality


# Local HTTP server to mangle live fetched mpd
LOCAL_URL = 'http://127.0.0.1:5057/5LIVE'

CORONA_URL = 'https://corona.channel5.com/shows/'
BASIS_URL = CORONA_URL + '%s/seasons'

URL_SEASONS = BASIS_URL + '.json'
URL_EPISODES = BASIS_URL + '/%s/episodes.json'
FEEDS_API = 'https://feeds-api.channel5.com/collections/%s/concise.json'

URL_VIEW_ALL = CORONA_URL + 'search.json'
URL_WATCHABLE = 'https://corona.channel5.com/watchables/search.json'
URL_SHOWS = 'https://corona.channel5.com/shows/search.json'
IMG_URL = 'https://api-images.channel5.com/otis/images/episode/%s/320x180.jpg'
SHOW_IMG_URL = 'https://api-images.channel5.com/otis/images/show/%s/320x180.jpg'


ONEOFF = 'https://corona.channel5.com/shows/%s/episodes/next.json'


GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}

LICC_URL = 'https://cassie.channel5.com/api/v2/media/my5desktopng/%s.json?timestamp=%s'
LIVE_LICC_URL = 'https://cassie.channel5.com/api/v2/live_media/my5desktopng/%s.json?timestamp=%s'
KEYURL = "https://player.akamaized.net/html5player/core/html5-c5-player.js"
CERT_URL = 'https://c5apps.channel5.com/wv/c5-wv-app-cert-20170524.bin'

#MY5-001: Customise My5 artwork - create constants
HOME              = xbmcvfs.translatePath('special://home/')
ADDONS            = os.path.join(HOME,     'addons')
RESOURCE_IMAGES   = os.path.join(ADDONS,   'resource.images.catchuptvandmore')
RESOURCES         = os.path.join(RESOURCE_IMAGES,   'resources')
CHANNELS          = os.path.join(RESOURCES,         'channels')
UK_CHANNELS       = os.path.join(CHANNELS,          'uk')
fanartpath        = os.path.join(UK_CHANNELS,       'my5_fanart.jpg')
iconpath          = os.path.join(UK_CHANNELS,       'my5.png')

feeds_api_params = {
    'vod_available': 'my5desktop',
    'friendly': '1'
}

view_api_params = {
    'platform': 'my5desktop',
    'friendly': '1'
}

lic_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Referer': 'https://www.channel5.com/',
        'Content-Type': '',
    }




# Some Sttaic Arrays
# Not sure where S4B comes from, statically defined for now
S4B = [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22]

# Not sure where G4B comes from, statically defined for now
G4B = [1374988112,2118214995,437757123,975658646,1001089995,530400753,-1392879445,1273168787,540080725,-1384747530,-1999866223,-184398811,1340463100,-987051049,641025152,-1251826801,-558802359,632953703,1172967064,1576976609,-1020300030,-2125664238,-1924753501,1809054150,59727847,361929877,-1083344149,-1789765158,-725712083,1484005843,1239443753,-1899378620,1975683434,-191989384,-1722270101,666464733,-1092530250,-259478249,-920605594,2110667444,1675577880,-451268222,-1756286112,1649639237,-1318815776,-1150570876,-25059300,-116905068,1883793496,-1891238631,-1797362553,1383856311,-1418472669,1917518562,-484470953,1716890410,-1293211641,800440835,-2033878118,-751368027,807962610,599762354,33778362,-317291940,-1966138325,-1485196142,-217582864,1315562145,1708848333,101039829,-785096161,-995688822,875451293,-1561111136,92987698,-1527321739,193195065,1080094634,1584504582,-1116860335,1042385657,-1763899843,-583137874,1306967366,-1856729675,1908694277,67556463,1615861247,429456164,-692196969,-1992277044,1742315127,-1326955843,126454664,-417768648,2043211483,-1585706425,2084704233,-125559095,0,159417987,841739592,504459436,1817866830,-49348613,260388950,1034867998,908933415,168810852,1750902305,-1688513327,607530554,202008497,-1822955761,-1259432238,463180190,-2134850225,1641816226,1517767529,470948374,-493635062,-1063245083,1008918595,303765277,235474187,-225720403,766945465,337553864,1475418501,-1351284916,-291906117,-1551933187,-150919521,1551037884,1147550661,1543208500,-1958532746,-886847780,-1225917336,-1192955549,-684598070,1113818384,328671808,-2067394272,-2058738563,-759480840,-1359400431,-953573011,496906059,-592301837,226906860,2009195472,733156972,-1452230247,294930682,1206477858,-1459843900,-1594867942,1451044056,573804783,-2025238841,-650587711,-1932877058,-1730933962,-1493859889,-1518674392,-625504730,1068351396,742039012,1350078989,1784663195,1417561698,-158526526,-1864845080,775550814,-2101104651,-1621262146,1775276924,1876241833,-819653965,-928212677,270040487,-392404114,-616842373,-853116919,1851332852,-325404927,-2091935064,-426414491,-1426069890,566021896,-283776794,-1159226407,1248802510,-358676012,699432150,832877231,708780849,-962227152,899835584,1951317047,-58537306,-527380304,866637845,-251357110,1106041591,2144161806,395441711,1984812685,1139781709,-861254316,-459930401,-1630423581,1282050075,-1054072904,1181045119,-1654724092,25965917,-91786125,-83148498,-1285087910,-1831087534,-384805325,1842759443,-1697160820,933301370,1509430414,-351060855,-827774994,-1218328267,-518199827,2051518780,-1663901863,1441952575,404016761,1942435775,1408749034,1610459739,-549621996,2017778566,-894438527,-1184316354,941896748,-1029488545,371049330,-1126030068,675039627,-15887039,967311729,135050206,-659233636,1683407248,2076935265,-718096784,1215061108,-793225406]

# Not sure where D4B comes from, statically defined for now
D4B = [-1487908364,1699970625,-1530717673,1586903591,1808481195,1173430173,1487645946,59984867,-95084496,1844882806,1989249228,1277555970,-671330331,-875051734,1149249077,-1550863006,1514790577,459744698,244860394,-1058972162,1963115311,-267222708,-1750889146,-104436781,1608975247,-1667951214,2062270317,1507497298,-2094148418,567498868,1764313568,-935031095,-1989511742,2037970062,1047239000,1910319033,1337376481,-1390940024,-1402549984,984907214,1243112415,830661914,861968209,2135253587,2011214180,-1367032981,-1608712575,731183368,1750626376,-48656571,1820824798,-122203525,-752637069,48394827,-1890065633,-1423284651,671593195,-1039978571,2073724613,145085239,-2014171096,-1515052097,1790575107,-2107839210,472615631,-1265457287,-219090169,-492745111,-187865638,-1093335547,1646252340,-24460122,1402811438,1436590835,-516815478,-344611594,-331805821,-274055072,-1626972559,273792366,-1963377119,104699613,95345982,-1119466010,-1917480620,1560637892,-730921978,369057872,-81520232,-375925059,1137477952,-1636341799,1119727848,-1954019447,1530455833,-287606328,172466556,266959938,516552836,0,-2038232704,-314035669,1890328081,1917742170,-262898,945164165,-719438418,958871085,-647755249,-1507760036,1423022939,775562294,1739656202,-418409641,-1764576018,-1851909221,-984645440,547512796,1265195639,437656594,-1173691757,719700128,-532464606,387781147,218828297,-944901493,-1464259146,-1446505442,428169201,122466165,-574886247,1627235199,648017665,-172204942,1002783846,2117360635,695634755,-958608605,-60246291,-245122844,-590686415,-2062531997,574624663,287343814,612205898,1039717051,840019705,-1586641111,793451934,821288114,1391201670,-472877119,376187827,-1181111952,1224348052,1679968233,-1933268740,1058709744,752375421,-1863376333,1321699145,-775825096,-1560376118,188127444,-2117097739,-567761542,-1910056265,-1079754835,-1645990854,-1844621192,-862229921,1180849278,331544205,-1192718120,-144822727,-1342864701,-2134991011,-1820562992,766078933,313773861,-1724135252,2108100632,1668212892,-1149510853,2013908262,418672217,-1224610662,-1700232369,1852171925,-427906305,-821550660,-387518699,-1680229657,919489135,164948639,2094410160,-1297141340,590424639,-1808742747,1723872674,-1137216434,-895026046,-793714544,-669699161,-1739919100,-621329940,1343127501,-164685935,-695372211,-1337113617,1297403050,81781910,-1243373871,-2011476886,532201772,1367295589,-368796322,895287692,1953757831,1093597963,492483431,-766340389,1446242576,1192455638,1636604631,209336225,344873464,1015671571,669961897,-919226527,-437395172,-1321436601,-547775278,1933530610,-830924780,935293895,-840281097,-1436852227,1863638845,-611944380,-209597777,-1002522264,875313188,1080017571,-1015933411,621591778,1233856572,-1790836979,24197544,-1277294580,-459482956,-1047501738,-2073986101,-1234119374,1551124588,1463996600]
# Not sure where d4B comes from, statically defined for now
d4B = [-190361519,1097159550,396673818,660510266,-1418998981,-1656360673,-94852180,-486304949,821712160,1986918061,-864644728,38544885,-438830001,718002117,893681702,1654886325,-1319482914,-1172609243,-368142267,-20913827,796197571,1290801793,1184342925,-738605461,-1889540349,-1835231979,1836772287,1381620373,-1098699308,1948373848,-529979063,-909622130,-1031181707,-1904641804,1480485785,-1183720153,-514869570,-2001922064,548169417,-835013507,-548792221,439452389,1362321559,1400849762,1685577905,1806599355,-2120213250,137073913,1214797936,1174215055,-563312748,2079897426,1943217067,1258480242,529487843,1437280870,-349698126,-1245576401,-981755258,923313619,679998000,-1079659997,57326082,377642221,-820237430,2041877159,133361907,1776460110,-621490843,96392454,878845905,-1493267772,777231668,-212492126,-1964953083,-152341084,-2081670901,1626319424,1906247262,1846563261,562755902,-586793578,1040559837,-423803315,1418573201,-1000536719,114585348,1343618912,-1728371687,-1108764714,1078185097,-643926169,-398279248,-1987344377,425408743,-923870343,2081048481,1108339068,-2078357000,0,-2138668279,736970802,292596766,1517440620,251657213,-2059905521,-1361764803,758720310,265905162,1554391400,1532285339,908999204,174567692,1474760595,-292105548,-1684955621,-1060810880,-601841055,2001430874,303699484,-1816524062,-1607801408,585122620,454499602,151849742,-1949848078,-1230456531,514443284,-249985705,1963412655,-1713521682,2137062819,19308535,1928707164,1715193156,-75615141,1126790795,600235211,-302225226,-453942344,836553431,1669664834,-1759363053,-971956092,1243905413,-1153566510,-114159186,698445255,-1641067747,-1305414692,-2041385971,-1042034569,-1290376149,1891211689,-1807156719,-379313593,-57883480,-264299872,2100090966,865136418,1229899655,953270745,-895287668,-737462632,-176042074,2061379749,-1215420710,-1379949505,983426092,2022837584,1607244650,2118541908,-1928084746,-658970480,972512814,-1011878526,1568718495,-795640727,-718427793,621982671,-1399243832,410887952,-1671205144,1002142683,645401037,1494807662,-1699282452,1335535747,-1787927066,-1671510,-1127282655,367585007,-409216582,1865862730,-1626745622,-1333995991,-1531793615,1059270954,-1517014842,-1570324427,1320957812,-2100648196,-1865371424,-1479011021,77089521,-321194175,-850391425,-1846137065,1305906550,-273658557,-1437772596,-1778065436,-776608866,1787304780,740276417,1699839814,1592394909,-1942659839,-2022411270,188821243,1729977011,-606973294,274084841,-699985043,-681472870,-1593017801,-132870567,322734571,-1457000754,1640576439,484830689,1202797690,-757114468,-227328171,349075736,-952647821,-137500077,-39167137,1030690015,1155237496,-1342996022,1757691577,607398968,-1556062270,499347990,-500888388,1011452712,227885567,-1476300487,213114376,-1260086056,1455525988,-880516741,850817237,1817998408,-1202240816]
# Not sure where l4B comes from, statically defined for now
l4B = [1347548327,1400783205,-1021700188,-1774573730,-885281941,-249586363,-1414727080,-1823743229,1428173050,-156404115,-1853305738,636813900,-61872681,-674944309,-2144979644,-1883938141,1239331162,1730525723,-1740248562,-513933632,46346101,310463728,-1551022441,-966011911,-419197089,-1793748324,-339776134,-627748263,768917123,-749177823,692707433,1150208456,1786102409,2029293177,1805211710,-584599183,-1229004465,401639597,1724457132,-1266823622,409198410,-2098914767,1620529459,1164071807,-525245321,-2068091986,486441376,-1795618773,1483753576,428819965,-2020286868,-1219331080,598438867,-495826174,1474502543,711349675,129166120,53458370,-1702443653,-1512884472,-231724921,-1306280027,-1174273174,1559041666,730517276,-1834518092,-252508174,-1588696606,-848962828,-721025602,533804130,-1966823682,-1657524653,-1599933611,839224033,1973745387,957055980,-1438621457,106852767,1371368976,-113368694,1033297158,-1361232379,1179510461,-1248766835,91341917,1862534868,-10465259,605657339,-1747534359,-863420349,2003294622,-1112479678,-2012771957,954669403,-612775698,1201765386,-377732593,-906460130,0,-2096529274,1211247597,-1407315600,1315723890,-67301633,1443857720,507358933,657861945,1678381017,560487590,-778347692,975451694,-1324610969,261314535,-759894378,-1642357871,1333838021,-1570644960,1767536459,370938394,182621114,-440360918,1128014560,487725847,185469197,-1376613433,-1188186456,-938205527,-2057834215,1286567175,-1141990947,-39616672,-1611202266,-1134791947,-985373125,878443390,1988838185,-590666810,1756818940,1673061617,-891866660,272786309,1075025698,545572369,2105887268,-120407235,296679730,1841768865,1260232239,-203640272,-334657966,-797457949,1814803222,-1716948807,-99511224,575138148,-995558260,446754879,-665420500,-282971248,-947435186,-1042728751,-24327518,915985419,-811141759,681933534,651868046,-1539330625,-466863459,223377554,-1687527476,1649704518,-1024029421,-393160520,1580087799,-175979601,-1096852096,2087309459,-1452288723,-1278270190,1003007129,-1492117379,1860738147,2077965243,164439672,-194094824,32283319,-1467789414,1709610350,2125135846,136428751,-420538904,-642062437,-833982666,-722821367,-701910916,-1355701070,824852259,818324884,-1070226842,930369212,-1493400886,-1327460144,355706840,1257309336,-146674470,243256656,790073846,-1921626666,1296297904,1422699085,-538667516,-476130891,457992840,-1195299809,2135319889,77422314,1560382517,1945798516,788204353,1521706781,1385356242,870912086,325965383,-1936009375,2050466060,-1906706412,-1981082820,-288446169,901210569,-304014107,1014646705,1503449823,1062597235,2031621326,-1082931401,-363595827,1533017514,350174575,-2038938405,-2117423117,1052338372,741876788,1606591296,1914052035,213705253,-1960297399,1107234197,1899603969,-569897805,-1663519516,-1872472383,1635502980,1893020342,1950903388,1120974935]
P94 = [82,9,106,213,48,54,165,56,191,64,163,158,129,243,215,251,124,227,57,130,155,47,255,135,52,142,67,68,196,222,233,203,84,123,148,50,166,194,35,61,238,76,149,11,66,250,195,78,8,46,161,102,40,217,36,178,118,91,162,73,109,139,209,37,114,248,246,100,134,104,152,22,212,164,92,204,93,101,182,146,108,112,72,80,253,237,185,218,94,21,70,87,167,141,157,132,144,216,171,0,140,188,211,10,247,228,88,5,184,179,69,6,208,44,30,143,202,63,15,2,193,175,189,3,1,19,138,107,58,145,17,65,79,103,220,234,151,242,207,206,240,180,230,115,150,172,116,34,231,173,53,133,226,249,55,232,28,117,223,110,71,241,26,113,29,41,197,137,111,183,98,14,170,24,190,27,252,86,62,75,198,210,121,32,154,219,192,254,120,205,90,244,31,221,168,51,136,7,199,49,177,18,16,89,39,128,236,95,96,81,127,169,25,181,74,13,45,229,122,159,147,201,156,239,160,224,59,77,174,42,245,176,200,235,187,60,131,83,153,97,23,43,4,126,186,119,214,38,225,105,20,99,85,33,12,125]



def arrayCopy(original):
    out = [None] * len(original);
    for x in range(0, len(original)):
       out[x] = original[x]
    return(out)

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val


# make a number like a javbascript inter only 32 bits long
def u_to_l(u):
    return u - (1<<32) if u >= (1<<31) else u


# make array23 from cassie
def cassiearray(H7):
   L7 = []
   for z0 in range(len(H7)):
     try:
       tempx= L7[z0 >> 2]
     except IndexError:
       tempx = L7.append(0)
     L7[z0 >> 2] |= (255 & ord(H7[z0])) << (24 - z0 % 4 * 8)
   return(L7)

def cassieoarraymod(A23):
   q5N = 1240
   e5N = 728
   A32 = []
   x = len(A23)
   xbmc.log("XXXX %s" % x, level=xbmc.LOGERROR)
   for x in A23:
     A32.append(x)
   if (len(A23) > 22):
     for x in range(22,30):
       A32.append(0)
     A32[(e5N & 0xffffffff) >> 5] |= 128 << 24 - e5N % 32
     A32.append(1240)
   else:
     A32[21] |= 128
     for x in range(22,31):
        A32.append(0)
     A32.append(1208)
   return(A32)


def init(j5A):
    Q6t = 16
    X6t = []
    f6t = []
    for g6t in range(Q6t):
       try:
           tempx= j5A[g6t]
       except IndexError:
           tempx = 0

       tempy = u_to_l(tempx) ^ 1549556828
       tempz = u_to_l(tempx) ^ 909522486
       X6t.append(u_to_l(tempy))
       f6t.append(u_to_l(tempz))
    return(X6t, f6t)

# create auth token at last
def strinigify(U8E):
    Z8E = 0
    P8E = 32
    i8E = []
    S8E = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


    while (Z8E < P8E):
       try:
           tempx = U8E[Z8E + 2 >> 2]
       except IndexError:
           tempx = 0
       L8E = 0
       while (L8E < 4 and Z8E + .75 * L8E < P8E):
            A8E  = (U8E[Z8E >> 2] >> 24 - Z8E % 4 * 8 & 255) << 16 | (U8E[Z8E + 1 >> 2] >> 24 - (Z8E + 1) % 4 * 8 & 255) << 8 | tempx >> 24 - (Z8E + 2) % 4 * 8 & 255
            i8E.append( S8E[A8E >> 6 * (3 - L8E) & 63] )
            L8E += 1
       Z8E += 3
    # padd to 44 with = but these get stripped later so dont bother now
    #i8E.append("=")

    return(i8E)

# susbstitute some characters in auth string before requesting license
def change(auth):
    result = ''.join(str(x) for x in auth)
    result = result.replace("+", "-")
    result = result.replace("/", "_")
    result = re.sub(r'=={0,}$', '', result)
    return(result)



# build array from lic key
def parse(M5A):
    # always is the same so no need to generate each time
    parsemap = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 62, None, None, None, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, None, None, None, 64, None, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, None, None, None, None, None, None, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    j5A = [0] * 4
    z5A = 0
    f5A = 0

    F5A = M5A.index('=') 
    for f5A in range(F5A):
      if ((f5A % 4) != 0):
        B5A = parsemap[ord(M5A[f5A - 1])] << f5A % 4 * 2
        G5A = parsemap[ord(M5A[f5A])] >> 6 - f5A % 4 * 2
        Z5A = B5A | G5A
        temp_x = 24 - z5A % 4 * 8
        j5A[z5A >> 2] |= ctypes.c_int(Z5A << temp_x).value
        z5A += 1

    return(j5A)

# all we need is array of ascii value of each character in the long story 
def url_parse(queryStr):
   i = 0
   data = []
   unicodestring=urllib.parse.unquote(queryStr)
   for unicodechar in unicodestring: 
       data.append(ord(unicodechar))
       i += 1
   return data


def randomMath(y6k):
    y6kInt = int(y6k)
    b = int(4294967296 * (y6k - (0 | y6kInt) ))
    c = twos_comp(b, 32)
    return(c)


def srState(H6k):
    u6k = int(math.sqrt(H6k))
    Q6k = 2
    state = True
    while (Q6k <= u6k):
         if ((H6k % Q6k) == 0):
             state = False
             Q6k = u6k + 2
         Q6k += 1
    return(state)


def magic64():
    B6k = [0] * 64
    S6k = [0] * 64
    V6k = 2
    X6k = 0
    while (X6k < 64):
        if ( srState(V6k) ):
           B6k[X6k] = randomMath( pow(V6k, 0.5) )
           # approximating 1/3 looks okay
           S6k[X6k] = randomMath( pow(V6k, 0.3333333333333333))
           X6k += 1
        V6k += 1

    return(S6k)

def array32a1(a1,c8):
   out = []
   for x in a1:
       out.append(x)
   for x in c8 :
       out.append(x)
   out.append(-2147483648)
   for x in range(6):
       out.append(0)
   out.append(768)
   return(out)

def doProcessBlock(D5r,o0r,S6k,Y5k):
   I6k = [] 
   a6k = D5r[0]
   k6k = D5r[1]
   M6k = D5r[2]
   z5k = D5r[3]
   c6k = D5r[4]
   R5k = D5r[5]
   f5k = D5r[6]
   q5k = D5r[7]

   for L6k in range (64):
      if (L6k < 16):
          I6k.append( o0r[L6k + Y5k] )
      else:
          s6k = I6k[L6k - 15]
          h5k = (ctypes.c_int(s6k << 25).value | (s6k & 0xffffffff) >> 7) ^ (ctypes.c_int(s6k << 14).value | (s6k & 0xffffffff) >> 18) ^ (s6k & 0xffffffff) >> 3
          t5k = I6k[L6k - 2]
          K5k = (ctypes.c_int(t5k << 15).value | (t5k & 0xffffffff) >> 17) ^ (ctypes.c_int(t5k << 13).value | (t5k & 0xffffffff) >> 19) ^ (t5k & 0xffffffff) >> 10
          I6k.append( h5k + I6k[L6k - 7] + K5k + I6k[L6k - 16])

      g5k = a6k & k6k ^ a6k & M6k ^ k6k & M6k
      P5k = (ctypes.c_int(a6k << 30).value | (a6k & 0xffffffff) >> 2) ^ (ctypes.c_int(a6k << 19).value | (a6k & 0xffffffff) >> 13) ^ (ctypes.c_int(a6k << 10).value | (a6k & 0xffffffff) >> 22)
      m5k = q5k + ((ctypes.c_int(c6k << 26).value | (c6k & 0xffffffff) >> 6) ^ (ctypes.c_int(c6k << 21).value | (c6k & 0xffffffff) >> 11) ^ (ctypes.c_int(c6k << 7).value | (c6k & 0xffffffff) >> 25)) + (c6k & R5k ^ ~c6k & f5k) + S6k[L6k] + I6k[L6k];



      q5k = f5k
      f5k = R5k
      R5k = c6k
      c6k = ctypes.c_int( (z5k + m5k) ).value
      z5k = M6k
      M6k = k6k
      k6k = a6k
      a6k = ctypes.c_int(m5k + (P5k + g5k)).value

   # finally make new magic array of 8
   D5r[0] = ctypes.c_int(D5r[0] + a6k).value
   D5r[1] = ctypes.c_int(D5r[1] + k6k).value
   D5r[2] = ctypes.c_int(D5r[2] + M6k).value
   D5r[3] = ctypes.c_int(D5r[3] + z5k).value
   D5r[4] = ctypes.c_int(D5r[4] + c6k).value
   D5r[5] = ctypes.c_int(D5r[5] + R5k).value
   D5r[6] = ctypes.c_int(D5r[6] + f5k).value
   D5r[7] = ctypes.c_int(D5r[7] + q5k).value

   return(D5r)



def getdata(ui,watching):
   # We need 2 things from the js file, the long string of gibberish and the short
   # string to OR with,
   # I assume short string is always 6 digits long to regexp search on
   # The lomg string is really long so i look for at least 3000 characters

   resp = urlquick.get(KEYURL)
   content = resp.content.decode("utf-8", "ignore")

   # short string
   m = re.compile(r';}}}\)\(\'(......)\'\)};').search(content)
   ss = m.group(1)
   # long string
   m = re.compile(r'\(\){return "(.{3000,})";\}').search(content)
   s = str(m.group(1))


   z = url_parse(s)
   l = len(z)

   y = 0
   sout = ""

   for x in range(l):
       if (y > 5):
         y = 0
       p1 = z[x]
       p2 = ord(ss[y])
       k = p1 ^ p2
       # Only worried about printable characters for what we need
       if ( (k > 31) and (k < 127) ):
        sout = sout + chr(k)
       #else:
       # sout = sout + str(k)
       y = y + 1

   #extract the key from sout
   m = re.compile(r'SSL_MA..(.{24})..(.{24})').search(sout)
   k1 = m.group(1)
   k2 = m.group(2)


   # we need an 8 byte array that makes magic
   m = re.compile(r'2689\)\]=\[(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\]').search(content)

   # lets make an array
   magicArray = []
   for x in range(1,9):
       magicArray.append( twos_comp(int( m.group(x) ),32) )
   fourarray = parse(k1)
   a1,a2 = init(fourarray)

   S6k = magic64()

   timeStamp = str( int(time.time()) ) 

   
   if (watching == "vod"): 
      CALL_URL = LICC_URL % (ui, timeStamp)
   else:
      CALL_URL = LIVE_LICC_URL % (ui, timeStamp)

   array23 = cassiearray(CALL_URL)
   array32 = cassieoarraymod(array23)


   # iterate around doProcessBlock
   magicArrayF = arrayCopy(magicArray)
   onemagic8 = doProcessBlock(magicArrayF,a2,S6k,0)

   twomagic8array = arrayCopy(array32)
   twomagic8 = doProcessBlock(onemagic8,twomagic8array,S6k,0)

   threemagic8 = doProcessBlock(twomagic8,twomagic8array,S6k,16)

   magicArrayF = arrayCopy(magicArray)
   fourmagic8array = array32a1(a1,threemagic8)
   fourmagic8 = doProcessBlock(magicArrayF,fourmagic8array,S6k,0)

   fivemagic8 = doProcessBlock(fourmagic8,fourmagic8array,S6k,16)



   authKey = strinigify(fivemagic8)
   str1 = change(authKey)

   LICFULL_URL = CALL_URL + "&auth=" + str1
   return (LICFULL_URL, k2)

def ivdata(URL):
    resp = urlquick.get(URL, headers=GENERIC_HEADERS)
    root = json.loads(resp.text)
    iv = root['iv']
    data = root['data']
    return(iv, data)



# For Iv and Data processing

def aesToArray(key):
    keyArray = parse(key)
    return keyArray

def mangle(st):
    #result = iv + "===="
    result = st
    result = result.replace("-", "+")
    result = result.replace("_", "/")
    return (result)

def b6(iv):
    Z4Z = 22
    p4Z = 2

    Y4Z = [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 62, None, 62, None, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, None, None, None, None, None, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, None, None, None, None, 63, None, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51 ]
    T4Z = 0
    t4Z = [0] * 16
    j4Z = 0
    while (T4Z < 18):
        e4Z = ctypes.c_int(Y4Z[ord(iv[T4Z])] << 18).value | ctypes.c_int(Y4Z[ord(iv[T4Z+1])] << 12).value | ctypes.c_int(Y4Z[ord(iv[T4Z+2])] << 6).value | Y4Z[ord(iv[T4Z+3])]
        e4Z32 = (e4Z & 0xffffffff)
        t4Z[j4Z] = e4Z32 >> 16 & 255
        j4Z += 1
        t4Z[j4Z] = e4Z32 >> 8 & 255
        j4Z += 1
        t4Z[j4Z] = 255 & e4Z
        j4Z += 1
        T4Z += 4


    try:
        T4Z1 = Y4Z[ord(iv[T4Z+1])]
    except:
        T4Z1 = 0

    try:
        T4Z2 = Y4Z[ord(iv[T4Z+2])]
    except:
        T4Z2 = 0

    if (p4Z == 2):
        e4Z = ctypes.c_int(Y4Z[ord(iv[T4Z])] << 2).value | (T4Z1 >> 4)
        t4Z[j4Z] = 255 & e4Z

    if (p4Z == 1):
        e4Z = ctypes.c_int(Y4Z[ord(iv[T4Z])] << 10).value | ctypes.c_int(T4Z1 << 4).value | T4Z2 >> 2
        t4Z.append(ctypes.c_int(e4Z >> 8).value & 255)
        t4Z.append(255 & e4z)


def ivArray(N3n):
    d3n = [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 62, None, None, None, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, None, None, None, 64, None, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, None, None, None, None, None, None, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51 ]
    f3n = 0
    K3n = [0] * 4 
    T3n = N3n.index("=")
    for L3n in range(T3n):
        if ( (L3n % 4) != 0):
           D3n = ctypes.c_int(d3n[ord(N3n[L3n-1])] << L3n % 4 * 2).value
           o3n = (d3n[ord(N3n[L3n])] & 0xffffffff) >>  6 - L3n % 4 * 2
           P3n = D3n | o3n
           K3n[f3n >> 2] |= ctypes.c_int(P3n << 24 - f3n % 4 * 8).value
           f3n += 1
    return(K3n)

def ivParse(N3n):
    l9u = len(N3n)
    z9u = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    d3n = [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 62, None, None, None, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, None, None, None, 64, None, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, None, None, None, None, None, None, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51 ]
    D9u = "="
    try:
        d9u = G9u.index("=")
    except: 
        d9u = "-1"
    f3n = 0
    K3n = [0] * 480
    for L3n in range(l9u):
        if ( (L3n % 4) != 0):
           I9u = ctypes.c_int(d3n[ord(N3n[L3n-1])] << L3n % 4 * 2).value
           o3n = (d3n[ord(N3n[L3n])] & 0xffffffff) >>  6 - L3n % 4 * 2
           P3n = I9u | o3n
           temp_x = 24 - f3n % 4 * 8
           K3n[f3n >> 2] |= ctypes.c_int(P3n << temp_x).value
           # K3n[f3n >> 2] |= ctypes.c_int(P3n << 24 - f3n % 4 * 8).value
           f3n += 1
    return(K3n)

def ivreset(aes4) :
    M6B = aes4
    w6B = aes4
    r4B = [ 0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54 ]
    e6B = 4
    X6B = 44
    k6B = [0] * 44
    g6B = 0
    C6B = -67372037

 



    # javascript here was really cryptic so my python version is very drawn out
    for g6B in range (X6B):
        if (g6B < e6B):
            k6B[g6B] = w6B[g6B]
        else:
            C6B = k6B[g6B - 1]
            if (g6B % e6B):
                if ( (e6B > 6) & (g6B % e6B == 4) ):
                        # e6B is sigBytes, i always see this as 4 so this code is untested
                        temp1 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 24] << 24).value
                        temp2 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 16 & 255] << 16).value
                        temp3 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 8 & 255] << 8).value
                        temp4 = S4B[255 & C6B]
                        C6B = temp1 | temp2 | temp3 | temp4
                        C6B = temp1 | temp2 | temp3 | temp4
                        C6B ^= ctypes.c_int(r4B[g6B // e6B | 0] << 24).value
                        k6B[g6B] = k6B[g6B - e6B] ^ C6B    
                else:
                        k6B[g6B] = k6B[g6B - e6B] ^ C6B
            else:
                C6B = ctypes.c_int(C6B << 8).value  | (C6B & 0xffffffff) >> 24
                temp1 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 24] << 24).value
                temp2 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 16 & 255] << 16).value
                temp3 = ctypes.c_int(S4B[(C6B & 0xffffffff) >> 8 & 255] << 8).value
                temp4 = S4B[255 & C6B]
                C6B = temp1 | temp2 | temp3 | temp4
                C6B ^= ctypes.c_int(r4B[g6B // e6B | 0] << 24).value
                k6B[g6B] = k6B[g6B - e6B] ^ C6B    

    T6B = []
    for Y6B in range(X6B):
        g6B = X6B - Y6B
        if (Y6B % 4):
            C6B = k6B[g6B]
        else:
            C6B = k6B[g6B - 4]
        if  ( (Y6B < 4) or  (g6B <= 4)):
            T6B.append(C6B)
        else:    
            # javascript is cryptic again, so its broken up into smaller chunks
            temp1 = G4B[S4B[(C6B & 0xffffffff) >> 24]] 
            temp2 = l4B[S4B[(C6B & 0xffffffff) >> 16 & 255]] 
            temp3 = D4B[S4B[(C6B & 0xffffffff) >> 8 & 255]] 
            temp4 = d4B[S4B[255 & C6B]]
            temp = temp1 ^ temp2 ^ temp3 ^ temp4
            T6B.append(temp)
       
    return(T6B)

def stringify480(I0,M0):
    s0 = [0]
    N0 = 0
    while ( ((N0 & 0xffffffff) >> 2) < len(I0)):
         o0 = ( I0[(N0 & 0xffffffff) >> 2] & 0xffffffff) >> 24 - N0 % 4 * 8 & 255
         if ( (o0 < 128) and (o0 > 31) ):
          s0.append( chr(o0) )
         N0 += 1

    result = ''.join(str(x) for x in s0)
    trimstr = result[:result.index(']}')+2]

    return(s0,trimstr)

def dataParse(i8):
    dL476 = arrayCopy(i8)
    dF4 = []
    for x in range(4):
       dF4.append(i8[0])
       dL476.pop(0)
    return(dF4, dL476)

def doCryptBlock(G94, d94, w94):
    e94 = G4B
    j94 = l4B
    r94 = D4B
    k94 = d4B
    S94 = 10
    A94 = G94[w94] ^ d94[0]
    O94 = G94[w94 + 1] ^ d94[1]
    u94 = G94[w94 + 2] ^ d94[2]
    i94 = G94[w94 + 3] ^ d94[3]
    v94 = 4
    V94 = 1
    for V94 in range (1,10):
        a = e94[(A94 & 0xffffffff) >> 24]
        b = j94[(O94 & 0xffffffff) >> 16 & 255]
        c = r94[(u94 & 0xffffffff) >> 8 & 255]
        d = k94[255 & i94]
        B94 = e94[(A94 & 0xffffffff) >> 24] ^ j94[(O94 & 0xffffffff) >> 16 & 255] ^ r94[(u94 & 0xffffffff) >> 8 & 255] ^ k94[255 & i94] ^ d94[v94]
        v94 += 1
        x94 = e94[(O94 & 0xffffffff) >> 24] ^ j94[(u94 & 0xffffffff) >> 16 & 255] ^ r94[(i94 & 0xffffffff) >> 8 & 255] ^ k94[255 & A94] ^ d94[v94]
        v94 += 1
        Q94 = e94[(u94 & 0xffffffff) >> 24] ^ j94[(i94 & 0xffffffff) >> 16 & 255] ^ r94[(A94 & 0xffffffff) >> 8 & 255] ^ k94[255 & O94] ^ d94[v94]
        v94 += 1
        F94 = e94[(i94 & 0xffffffff) >> 24] ^ j94[(A94 & 0xffffffff) >> 16 & 255] ^ r94[(O94 & 0xffffffff) >> 8 & 255] ^ k94[255 & u94] ^ d94[v94]
        v94 += 1
        A94 = B94
        O94 = x94
        u94 = Q94
        i94 = F94
    B94 = ( ctypes.c_int(P94[(A94 & 0xffffffff) >> 24] << 24).value | ctypes.c_int(P94[(O94 & 0xffffffff) >> 16 & 255] << 16).value | ctypes.c_int(P94[(u94 & 0xffffffff) >> 8 & 255] << 8).value | P94[255 & i94]) ^ d94[v94]
    p1 = P94[(A94 & 0xffffffff)  >> 24]
    v94 += 1
    x94 = ( ctypes.c_int(P94[(O94 & 0xffffffff) >> 24] << 24).value | ctypes.c_int(P94[(u94 & 0xffffffff) >> 16 & 255] << 16).value | ctypes.c_int(P94[(i94 & 0xffffffff) >> 8 & 255] << 8).value | P94[255 & A94]) ^ d94[v94]
    v94 += 1
    Q94 = ( ctypes.c_int(P94[(u94 & 0xffffffff) >> 24] << 24).value | ctypes.c_int(P94[(i94 & 0xffffffff) >> 16 & 255] << 16).value | ctypes.c_int(P94[(A94 & 0xffffffff) >> 8 & 255] << 8).value | P94[255 & O94]) ^ d94[v94]
    v94 += 1
    F94 = ( ctypes.c_int(P94[(i94 & 0xffffffff) >> 24] << 24).value | ctypes.c_int(P94[(A94 & 0xffffffff) >> 16 & 255] << 16).value | ctypes.c_int(P94[(O94 & 0xffffffff) >> 8 & 255] << 8).value | P94[255 & u94]) ^ d94[v94]
    v94 += 1
    G94[w94] = B94
    G94[w94 + 1] = x94
    G94[w94 + 2] = Q94
    G94[w94 + 3] = F94
    return(G94)



def dataProcess(a480, k6, iv4):
    counter1 = 0
    J0 = 0
    tA4 = []

    # 2D array to hold the pevious block
    previous = [[0]*0]*0
    # start it off with iv4
    iprevious = []
    iprevious = arrayCopy(iv4)
    previous.append(iprevious)

    tempB = arrayCopy(a480)
 
    J94 = 0
    F6 = 0
    while (J94 < 479):
        p4 = []
        for x in range(4):
              p4.append(a480[x + J94])
        previous.append(p4)
        c94 = tempB[J94 + 1]
        tempB[J94 + 1] = tempB[J94 + 3]
        tempB[J94 + 3] = c94
        tempB = doCryptBlock(tempB, k6, J94) 
        c94 = tempB[J94 + 1]
        tempB[J94 + 1] = tempB[J94 + 3]
        tempB[J94 + 3] = c94

        # get "previous" value to or with
        ork6 = []
        for c in range(4):
            ork6.append(previous[counter1][c])
        for r6 in range(4):
            tempB[F6 + r6] ^= ork6[r6]
        J94 += 4
        F6 += 4
        counter1 += 1
        pg6 = []
    for c in range(4):
        pg6.append(a480[476 + c])
    offs = 255 & tempB[479]    
    return(tempB, pg6, offs)

# this is probably really inefficient code, json habdling still confussess me
def getUseful(s):
    # back to json parsing to also do live urls .....
    keyserver = 'NA'
    streamUrl ='NA'
    subtitile = 'NA'
    fixed = s[1:]
    data = json.loads(fixed)
    jsonData = data['assets']
    for x in jsonData:
      if (x['drm'] == "widevine" ):
        keyserver = (x['keyserver'])
        u = (x['renditions'])
        for i in u:
          streamUrl = i['url']

    return  (streamUrl, keyserver, subtitile)

         

def part2(iv, aesKey, rdata):
    aesFour = aesToArray(aesKey)
    ivMangle = mangle(iv)
    b6(iv)
    ivFourArray = ivArray(ivMangle)
    dataMangle = mangle(rdata)
    data480 = ivParse(dataMangle)
    aes44 = ivreset(aesFour)
    (dataFirst4, dataLast476) = dataParse(data480)
    (newdata480, lastprevious, offset) = dataProcess(data480, aes44, ivFourArray)
    parseLength = 1920 - offset
    aarray, astring = stringify480(newdata480, parseLength)
    (stream, drmurl, sub) = getUseful(astring)
    return (stream, drmurl, sub)



@Route.register
def list_categories(plugin, **kwargs):
    resp = urlquick.get(FEEDS_API % 'PLC_My5SubGenreBrowsePageSubNav', headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    for i in range(int(root['total_items'])):
     try:
        item = Listitem()
        item_id = 1
        item.label = root['filters']['contents'][i]['title']
        browse_name = root['filters']['contents'][i]['id']
        offset = "0"
        item.set_callback(list_subcategories, item_id=item_id, browse_name=browse_name, offset=offset)
        item_post_treatment(item)
        # MY5-001: display My5 artwork instead of CUTV artwork
        item.art["thumb"] = iconpath
        item.art["fanart"] = fanartpath
        yield item
     except:
        pass


@Route.register
def list_subcategories(plugin, item_id, browse_name, offset, **kwargs):
    if (browse_name == "PLC_My5AllShows"):
       watchable_params = '?limit=25&offset=%s&platform=my5desktop&friendly=1' % str(offset)
       s = URL_SHOWS + watchable_params
       resp = urlquick.get(s, headers=GENERIC_HEADERS, params=feeds_api_params)
       root = json.loads(resp.text)
       item_number = int(root['size'])
       for emission in root['shows']:
        try:
         standalone = emission['standalone']
         standalone = "yes"
        except:
         standalone = "no"

        if (standalone == "yes"):
         item = Listitem()
         item.label = emission['title']
         item.info['plot'] = emission['s_desc']
         fname = emission['f_name']
         picture_id = emission['id']
         item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
         item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="", show_id="show_id", standalone="yes")
         item_post_treatment(item)
         yield item

        else:
         try:
          item = Listitem()
          title = emission['title']
          item.label = title
          item.info['plot'] = emission['s_desc']
          fname = emission['f_name']
          picture_id = emission['id']
          item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
          item.set_callback(list_seasons, item_id=item_id, fname=fname, pid=picture_id, title=title)
          item_post_treatment(item)
          yield item
         except:
          pass

       if 'next_page_url' in root:
          offset = str(int(offset) + int(root['limit']))
          yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


    else:
       resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
       root = json.loads(resp.text)
       item_number = int(root['total_items'])

       if root['filters']['type'] == 'Collection':
         offset = 0
         for i in range(item_number):
          try:
            item = Listitem()
            item.label = root['filters']['contents'][i]['title']
            browse_name = root['filters']['contents'][i]['id']
            item.set_callback(list_collections, item_id=item_id, browse_name=browse_name, offset=offset)
            item_post_treatment(item)
            # MY5-001: display My5 artwork instead of CUTV artwork
            item.art["thumb"] = iconpath
            item.art["fanart"] = fanartpath
            yield item
          except:
            pass
       elif root['filters']['type'] == 'Show':
        ids = root['filters']['ids']
        watchable_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
        for i in range(item_number):
          try:
            watchable_params = watchable_params + '&ids[]=%s' % ids[i]
          except:
            pass


        resp = urlquick.get(URL_SHOWS + watchable_params, headers=GENERIC_HEADERS)
        root = json.loads(resp.text)
        for watchable in root['shows']:
          try:
            item = Listitem()
            item.label = watchable['title']
            item.info['plot'] = watchable['s_desc']
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['id']
            show_id = watchable['id']
            fname = watchable['f_name']
            item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="season_f_name", show_id=show_id, standalone="yes")
            item_post_treatment(item)
            yield item
          except:
            pass


       elif root['filters']['type'] == 'Watchable':
        ids = root['filters']['ids']
        watchable_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
        for i in range(item_number):
          try:
            watchable_params = watchable_params + '&ids[]=%s' % ids[i]
          except:
            pass
        resp = urlquick.get(URL_WATCHABLE + watchable_params, headers=GENERIC_HEADERS)
        root = json.loads(resp.text)

        for watchable in root['watchables']:
          try:
            item = Listitem()
            item.label = watchable['sh_title']
            item.info['plot'] = watchable['s_desc']
            t = int(int(watchable['len']) // 1000)
            item.info['duration'] = t
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['sh_id']
            #fname = watchable['f_name']
            #season_f_name = watchable['sea_f_name']
            show_id = watchable['id']
            item.set_callback(get_video_url, item_id=item_id, fname="fname", season_f_name="season_f_name", show_id=show_id, standalone="no")
            item_post_treatment(item)
            yield item
          except:
            pass



@Route.register
def list_watchables(plugin, itemid, browse_name, offset, item_number, ids):
    return False


@Route.register
def list_collections(plugin, item_id, browse_name, offset, **kwargs):
    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    subgenre = root['filters']['vod_subgenres']
    view_all_params = {
        'platform': 'my5desktop',
        'friendly': '1',
        'limit': '25',
        'offset': offset,
        'vod_subgenres[]': subgenre
    }
    resp = urlquick.get(URL_VIEW_ALL, headers=GENERIC_HEADERS, params=view_all_params)
    root = json.loads(resp.text)

    for emission in root['shows']:
      try:
        standalone = emission['standalone']
        standalone = "yes"
      except:
        standalone = "no"

      if (standalone == "yes"):
        item = Listitem()
        item.label = emission['title']
        item.info['plot'] = emission['s_desc']
        fname = emission['f_name']
        picture_id = emission['id']
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
        item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="", show_id="show_id", standalone="yes")
        item_post_treatment(item)
        yield item

      else:
       try:
        item = Listitem()
        title = emission['title']
        item.label = title
        item.info['plot'] = emission['s_desc']
        fname = emission['f_name']
        picture_id = emission['id']
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
        item.set_callback(list_seasons, item_id=item_id, fname=fname, pid=picture_id, title=title)
        item_post_treatment(item)
        yield item
       except:
        pass




    if 'next_page_url' in root:
        offset = str(int(offset) + int(view_all_params['limit']))
        yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


@Route.register
def list_seasons(plugin, item_id, fname, pid, title, **kwargs):


    resp = urlquick.get(URL_SEASONS % fname, headers=GENERIC_HEADERS, params=view_api_params)
    if resp.ok:
        root = json.loads(resp.text)

        for season in root['seasons']:
          try:
            item = Listitem()
            season_number = season['seasonNumber']
            item.label = title + '\nSeason ' + season_number
            picture_id = pid
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
            item.set_callback(list_episodes, item_id=item_id, fname=fname, season_number=season_number)
            item_post_treatment(item)
            yield item
          except:
            pass


@Route.register
def list_episodes(plugin, item_id, fname, season_number, **kwargs):
    resp = urlquick.get(URL_EPISODES % (fname, season_number), headers=GENERIC_HEADERS, params=view_api_params)
    root = json.loads(resp.text)

    for episode in root['episodes']:
      try:
        item = Listitem()
        picture_id = episode['id']
        item.art['thumb'] = item.art['landscape'] = IMG_URL % picture_id
        item.label = episode['title']
        item.info['plot'] = episode['s_desc']
        t = int(int(episode['len']) // 1000)
        item.info['duration'] = t
        season_f_name = episode['sea_f_name']
        fname = episode['f_name']
        show_id = episode['id']
        item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name=season_f_name, show_id=show_id, standalone="no")
        item_post_treatment(item)
        yield item
      except:
        pass


@Resolver.register
def get_video_url(plugin, item_id, fname, season_f_name, show_id, standalone, **kwargs):

    # for a onceoff/stanalone we still dont have showid so we get it now
    if (standalone == "yes"):
      resp = urlquick.get(ONEOFF % fname, headers=GENERIC_HEADERS, params=view_api_params)
      if resp.ok:
        root = json.loads(resp.text)
        try:
          show_id = root['id']
        except:
          pass


    LICFULL_URL, aesKey  = getdata(show_id, "vod")
    (iv,data)=ivdata(LICFULL_URL)
    (stream,drmurl,suburl) = part2(iv,aesKey,data)
    xbmc.log("Stream : %s" % stream, level=xbmc.LOGERROR)
    xbmc.log("Licensce :  %s" % drmurl, level=xbmc.LOGERROR)

    # get server certiticate data and b64 it
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')

    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)


    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property[ 'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[ 'inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item
    
@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    LICFULL_URL, aesKey  = getdata(item_id,"live")
    (iv,data)=ivdata(LICFULL_URL)
    (stream,drmurl,suburl) = part2(iv,aesKey,data)
    xbmc.log("Stream : %s" % stream, level=xbmc.LOGERROR)
    xbmc.log("Licensce :  %s" % drmurl, level=xbmc.LOGERROR)

    # Send request to local web server

    # get server certiticate data and b64 it
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')

    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)

    #stream = 'http://127.0.0.1:5057/5LIVE?id=' + dstream

    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property[ 'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[ 'inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item


