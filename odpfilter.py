#!/usr/bin/python
# -*- coding: utf8 -*-

'''
Copyright (C) 2010  Cagatay Calli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


'''
Filter ODP data to leave only Turkish data.
Output filtered RDF (xml).

SAMPLE USAGE: odpfilter.py content.rdf.u8 > turkish-content.rdf.u8

@author: Cagatay Calli <cagatay@ceng.metu.edu.tr>
'''

import sys
import re


# <Topic r:id="World/Türkçe">
# ....
# </Topic>

# <ExternalPage about="http://www.awn.com">
# ...
# <topic>Top/Arts/Animation</topic>
# </ExternalPage>

reTopic = re.compile('<Topic(?: xmlns=".*?")? r:id=".*?">',re.DOTALL)
reTopic2 = re.compile('<Topic(?: xmlns=".*?")? r:id="(.*?)">',re.DOTALL)

RSIZE = 10000000	# read chunk size = 10 MB

def recordTopic(page):
   print page
   return	# true

args = sys.argv[1:]
# odpfilter.py <odp_content_file> <RSIZE>

if len(args) < 1:
    sys.exit()

if len(args) == 2:
    RSIZE = int(args[1])

f = open(args[0],'r')
prevText = ''

firstRead = f.read(10000)
documentStart = firstRead.find('<Topic')
print firstRead[:documentStart]	# preamble (RDF)

prevText = firstRead[documentStart:10000]

while True:

    newText = f.read(RSIZE)
    if not newText:
        break
    
    text = prevText + newText

    pst = -1
    pend = -1
    for msti in reTopic.finditer(text):
	if pst != -1:
		pend = msti.start()
		recordTopic(text[pst:pend])
		pst = -1

	# apply filtering here..
	if msti.group().find('Türkçe') == -1:
		continue
	else:	
		pst = msti.start()

    prevText = text[pst:]

f.close()

print '</RDF>'

