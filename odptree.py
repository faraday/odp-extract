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
Count links of ODP categories, traverse category tree and output:

* clustering information in Carpineto et al format (e.g. AMBIENT, ODP 239).
* pickled category tree (topicTree.pkl).

USAGE: odptree.py <odp_content_file>

@author: Cagatay Calli <cagatay@ceng.metu.edu.tr>
'''

import sys
import re
import pickle
import math


# <Topic r:id="World/Türkçe">
# ....
# </Topic>

# <ExternalPage about="http://www.awn.com">
# ...
# <topic>Top/Arts/Animation</topic>
# </ExternalPage>

reTopic = re.compile('<Topic(?: xmlns=".*?")? r:id=".*?">',re.DOTALL)
reTopic2 = re.compile('<Topic(?: xmlns=".*?")? r:id="(.*?)">',re.DOTALL)
reExternalPage = re.compile('<ExternalPage about="(?P<url>.*?)">.*?<d:Title>(?P<title>.*?)</d:Title>.*?<d:Description>(?P<snippet>.*?)</d:Description>.*?<topic>.*?</topic>.*?</ExternalPage>',re.MULTILINE|re.DOTALL)

RSIZE = 10000000	# read chunk size = 10 MB

class Node:
	def __init__(self,name,linkCount=0,links=[]):
		self.name = name
		self.children = []
		self.linkCount = linkCount
		self.links = links
		return
	def addChild(self,cnode):
		self.children.append(cnode)
		return
	def getChildren(self):
		return self.children
	def getChild(self,name):
		for n in self.children:
			if n.name == name:
				return n
		return None

class Tree:
	def __init__(self):
		# root node is nameless
		self.root = Node('')
		return
	def add(self,parts,linkCount,links):
		tmpnode = self.root
		absname = ''
		for p in parts:
			tc = tmpnode.getChild(p)
			if tc:
				tmpnode = tc
			else:
				nd = Node(p,linkCount,links)
				if absname:
					nd.absname = absname + '/' + p
				else:
					nd.absname = p
				tmpnode.addChild(nd)

			if absname:
				absname += '/' + p
			else:
				absname = p
		return	


tree = Tree()

def recordTopic(page):
   mtopic = reTopic2.search(page)
   strTopic = mtopic.group(1)

   if not strTopic:
	return

   links = [mr.groupdict() for mr in reExternalPage.finditer(page)]
   linkCount = len(links)

   st = strTopic.find('Türkçe') + len('Türkçe/')
   strTopic = strTopic[st:]

   if strTopic.startswith('Kids'):
	parts = ['Çocuk_ve_Genç']
	parts += strTopic.split('/')
	tree.add(parts,linkCount,links)
   else:
	parts = strTopic.split('/')
	tree.add(parts,linkCount,links)
   return	# true

args = sys.argv[1:]
# odptree.py <odp_content_file> <RSIZE>

if len(args) < 1:
    sys.exit()

if len(args) == 2:
    RSIZE = int(args[1])

f = open(args[0],'r')
prevText = ''

firstRead = f.read(10000)
documentStart = firstRead.find('<Topic')

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

	pst = msti.start()

    prevText = text[pst:]

f.close()


def visit(knode):
	cnodes = knode.getChildren()
	lcount = 0
	if not cnodes:
		return knode.linkCount
	else:
		# sum up link counts of children
		for cn in cnodes:
			lcount += visit(cn)
		knode.linkCount += lcount
			
	return knode.linkCount


# subtopic node collector
class NodeCollector:
	def __init__(self):
		self.nodes = []	# node at level = 2
		return
	def collect(self,knode,level=0):
		cnodes = knode.getChildren()
		if not cnodes or knode.linkCount < 100 or len(cnodes) < 6 or level > 2:
			return

		if level == 2:
			self.nodes.append((knode,len(cnodes)))
			return

		else:
			for cn in cnodes:
				self.collect(cn,level+1)
		return
	def trim(self,knode,level=0):
		cnodes = knode.getChildren()
		dlinks = []
		if not cnodes:
			return knode.links
		else:
			for cn in cnodes:
				dlinks += self.trim(cn,level+1)
		if level > 0:
			knode.links += dlinks
		return knode.links


# visit all nodes and fix link counts of parents
visit(tree.root)

ncol = NodeCollector()
ncol.collect(tree.root)
ncol.trim(tree.root)	# copy all sub-level link information to upper levels

topicDict = {}	# topicID - topic

fTopics = open('topics.txt','w')
fTopics.write('ID\tdescription\n')

fSubTopics = open('subTopics.txt','w')
fSubTopics.write('ID\tdescription\n')

topicID = 1	# topic ID part
stID = 1	# subtopic ID part

fResults = open('results.txt','w')
fResults.write('ID\turl\ttitle\tsnippet\n')

fStRel = open('STRel.txt','w')
fStRel.write('subTopicID\tdocID\n')

for n in ncol.nodes:
	#print n[0].absname,'\t',n[1],'\t',n[0].linkCount
	sumLinks = 0
	validChildren = []
	for st in n[0].getChildren():
		if st.linkCount < 4: continue
		sumLinks += st.linkCount
		validChildren.append(st)

	if len(validChildren) < 6:
		continue

	strTopic = n[0].absname.replace("/"," > ")
	fTopics.write(str(topicID) + '\t' + strTopic + '\n')
	print ' == ' + strTopic + ' == '

	totalResults = 0
	stCounts = []
	for vc in validChildren:
		rlcount = float(vc.linkCount) / sumLinks * 100
		rlcount = max(math.floor(rlcount),4)
		rlcount = int(rlcount)
		stCounts.append((vc,rlcount))
		totalResults += rlcount

	sortedChildren = sorted(stCounts, key=lambda x: x[1],reverse=True)

	stID = 1
	docID = 1
	for (vc,resCount) in sortedChildren:
		if stID > 10:
			break
		stFullID = str(topicID) + '.' + str(stID)
		strSubTopic = vc.absname.replace("/"," > ")
		print strSubTopic,'\t',resCount
		fSubTopics.write(stFullID + '\t' + strSubTopic + '\n')
		stLinks = vc.links[:resCount]

		for li in stLinks:
			docFullID = str(topicID) + '.' + str(docID)
			fResults.write(docFullID + '\t' + li['url'] + '\t' + li['title'] + '\t' + li['snippet'] + '\n')
			fStRel.write(stFullID + '\t' + docFullID + '\n')
			docID += 1

		stID += 1
		

	topicID += 1
	print totalResults,'\n\n'


fResults.close()
fStRel.close()

pk = open('topicTree.pkl','w')
pickle.dump(tree,pk)
pk.close()
