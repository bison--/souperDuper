#!/usr/bin/env python

__author__ = 'bison'

import urllib2
import BeautifulSoup
import os
import sys
import time
import datetime
import json

class souperDuper(object):
	def __init__(self, user):
		self.account = user
		self.destPath = os.path.join("images", self.account)
		self.counter = 0
		self.knownUrlsFile = os.path.join("images", user + ".knownUrls.txt")
		self.knownUrls = {}

		if not os.path.exists(self.destPath):
			os.makedirs(self.destPath)
		else:
			self.counter = len([name for name in os.listdir(self.destPath) if os.path.isfile(name)])

	def loadKnownUrls(self, fullPath=""):
		if fullPath == "":
			fullPath = self.knownUrlsFile

		if os.path.isfile(fullPath):
			fh = open(fullPath, 'r')
			tmpJson = fh.read()
			if tmpJson != "":
				self.knownUrls = json.loads(tmpJson)
			fh.close()

	def saveKnownUrls(self, fullPath=""):
		if fullPath == "":
			fullPath = self.knownUrlsFile

		fh = open(fullPath, 'w')
		fh.write(json.dumps(self.knownUrls))
		fh.close()

	def grabAll(self):
		self.loadKnownUrls()

		html = self.grab()

		foundNext = True
		while foundNext:
			self.saveKnownUrls()

			nextSegment = self.getNextEndless(html)
			if not nextSegment:
				foundNext = False
			else:
				self.debug("next: " + nextSegment)
				html = self.grab(nextSegment)

		self.saveKnownUrls()

	def grab(self, urlExt=""):
		grabUrl = 'http://' + self.account + '.soup.io'

		#SOUP.Endless.next_url
		if urlExt != "":
			grabUrl += "/" + urlExt

		response = urllib2.urlopen(grabUrl)
		html = response.read()

		soup = BeautifulSoup.BeautifulSoup(html)

		#print(soup.prettify())
		#exit()
		#for link in soup.findAll('a'):
		#	print(link.get('href'))

		for img in soup.findAll('img'):
			imgUrl = str(img.get('src'))
			if "asset" in  imgUrl and not "square" in imgUrl:
				if not imgUrl in self.knownUrls:
					self.counter  += 1
					self.knownUrls[imgUrl] = self.counter

					self.debug(str(self.counter) + ' > ' + imgUrl)

					#fileExt = imgUrl.split('.')
					#fileExt = fileExt[len(fileExt)-1]

					destFile =  os.path.join(self.destPath, self.getSaveFileName(imgUrl))#str(self.counter) + '.' + fileExt)
					fh = open(destFile, "wb")
					fh.write(urllib2.urlopen(imgUrl).read())
					fh.close()

		return soup.prettify()

	def getSaveFileName(self, url=""):
		#tmp = url.replace('http://', '')
		tmp = url.split('/')
		return str(self.counter) + '#' + tmp[len(tmp)-2] + "#" + tmp[len(tmp)-1]

	def getNextEndless(self, html):
		#http://user.soup.io/since/294388231
		pret = html.split("SOUP.Endless.next_url = '")
		if len(pret) == 2:
			part = pret[1].split('?')[0]
			return part
		return ""

	def debug(self, txt):
		print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S|"+txt)


if __name__ == "__main__":
	if len(sys.argv) > 1:
		sd = souperDuper(sys.argv[1])
		sd.grabAll()
	else:
		print "first parameter must be the user you want to dupe"