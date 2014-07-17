from readSoup import souperDuper
import os

folder = os.getcwd() + '/images'
folder = os.listdir(folder)

for filename in folder:
	username = filename.split('.')[0]
	print username
	os.system('python readSoup.py ' + username)
	os.system('clear')
