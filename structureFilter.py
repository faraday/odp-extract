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
Filter ODP structure.rdf to leave only relevant data.
Remove "altlang","symbolic","related","editor","Alias" tags

Output filtered RDF (xml).

SAMPLE USAGE: structureFilter.py structure.rdf.u8 > filtered-structure.rdf.u8

@author: Cagatay Calli <cagatay@ceng.metu.edu.tr>
'''

import sys
import re

re_strings = ['<editor','<symbolic','<altlang','<related','<newsgroup']
piped_re = re.compile( "|".join( re_strings ) , re.DOTALL)

reAlias = re.compile('<Alias')
reEndAlias = re.compile('</Alias>')

# <Topic r:id="World/Türkçe">
# ....
# </Topic>

# <ExternalPage about="http://www.awn.com">
# ...
# <topic>Top/Arts/Animation</topic>
# </ExternalPage>

args = sys.argv[1:]
# structureFilter.py <odp_structure_file>

if len(args) < 1:
    sys.exit()

f = open(args[0],'r')

mlRecord = False

for line in f.readlines():
	if piped_re.search(line):
		continue
	if reAlias.search(line):
		mlRecord = True
		continue
	if mlRecord and reEndAlias.search(line):
		mlRecord = False
		continue

	if not mlRecord:
		print line,

f.close()

