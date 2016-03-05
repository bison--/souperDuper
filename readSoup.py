#!/usr/bin/env python

__author__ = 'bison'

import urllib2
import BeautifulSoup
import os
import sys
import datetime
import json

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

class souperDuper(object):
	def __init__(self, args):
		self.account = args[1]
		self.destPath = os.path.join("images", self.account)
		self.counter = 0
		self.knownUrlsFile = os.path.join("images", self.account + ".knownUrls.txt")
		self.knownUrls = {}

		self.lastPage = ""
		self.doResume = False
		self.imageTypes = []

		for arg in args[2:]:
			if arg.startswith("imageTypes="):
				tmp = arg.replace("imageTypes=", "")
				self.imageTypes = tmp.split(",")
				for i in range(len(self.imageTypes)):
					self.imageTypes[i] = "." + self.imageTypes[i]
			elif arg == "resume":
				self.doResume = True
			else:
				print "UNKNOWN PARAMETER:", arg
				exit(404)

		if not os.path.exists(self.destPath):
			os.makedirs(self.destPath)
		else:
			# Magic voodoo I did not write, but it works!
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

		html = self.grabPage()

		foundNext = True
		while foundNext:
			self.saveKnownUrls()

			nextSegment = self.getNextEndless(html)
			if not nextSegment:
				foundNext = False
			else:
				self.debug("got: " + str(len(self.knownUrls)) + " next: " + nextSegment)
				html = self.grabPage(nextSegment)

		self.saveKnownUrls()

	def grabPage(self, urlExt=""):
		grabUrl = 'http://' + self.account + '.soup.io'
		prettyHtml = ""
		#SOUP.Endless.next_url
		if urlExt != "":
			grabUrl += "/" + urlExt

		try:
			pageOpener = urllib2.build_opener()
			pageOpener.addheaders = [('User-agent', USER_AGENT)]
			response = pageOpener.open(grabUrl)
			html = response.read()

			soup = BeautifulSoup.BeautifulSoup(html)

			#print(soup.prettify())
			#exit()
			#for link in soup.findAll('a'):
			#	print(link.get('href'))

			for img in soup.findAll('img'):
				imgUrl = str(img.get('src'))
				if "asset" in imgUrl and not "square" in imgUrl:
					if not imgUrl in self.knownUrls and self._isValidFile(imgUrl):
						self.counter += 1
						self.knownUrls[imgUrl] = self.counter

						self.debug(str(self.counter) + ' > ' + imgUrl)

						destFile = os.path.join(self.destPath, self.getSaveFileName(imgUrl))
						fh = open(destFile, "wb")
						imageOpener = urllib2.build_opener()
						imageOpener.addheaders = [('User-agent', USER_AGENT)]
						fh.write(imageOpener.open(imgUrl).read())
						#fh.write(urllib2.urlopen(imgUrl).read())
						fh.close()
			prettyHtml = soup.prettify()
		except Exception as ex:
			self.debug("ERROR: " + grabUrl + "\n" + str(ex))

		return prettyHtml

	def _isValidFile(self, url):
		if not self.imageTypes:
			return True

		#fileExt = imgUrl.split('.')
		#fileExt = fileExt[len(fileExt)-1]
		fileName, fileExt = os.path.splitext(url)
		#print fileName,"#", fileExt, fileExt in self.imageTypes
		if fileExt.lower() in self.imageTypes:
			return True

		return False

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
		sd = souperDuper(sys.argv)
		sd.grabAll()
	else:
		print """first parameter must be the user you want to dupe

# options #
imageTypes: the file extensions separated with ,

# samples #
readSoup.py bison
readSoup.py bison imageTypes=png,gif
"""
