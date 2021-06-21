''' Download image files with python 
(uses the urllib python library)

* What it supports:
[+] this script will download all the images from the provided url to a local path
[+] http auth 
[+] multiple extensions

* What it does not support
[-] Does not support Dynamic <img> tags generated by JavaScript (only the original html code will be evaluated)

* Example usage: 
python3 pyImageScraper.py https://www.w3schools.com/html/html_images.asp images
python3 pyImageScraper.py https://www.w3schools.com/html/html_images.asp images --extensions jpg
python3 pyImageScraper.py https://en.wikipedia.org/wiki/Painting images --extensions 'jpg|png'
python3 pyImageScraper.py https://en.wikipedia.org/wiki/Painting images --extensions 'jpg|png' --username <user> --password <password> 

@d7x_real
'''

import os, sys	
import argparse
import urllib.request # follows redirects by default
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import base64
import ssl

def downloadResource(link, savePath='images'):
	path_info = urlparse(link)
	filename_r = os.path.basename(path_info.path)
	filename = savePath + '/' + filename_r
	
	# read image
	result = urllib.request.urlopen(link)
	data = result.read()
	
	# write binary data to file
	try:
		f = open(filename, 'wb')
		f.write(data)
	except IOError:
		CRED = '\033[0;31m'
		CEND = '\033[0m'
		print(CRED)
		print("*"*140)
		print("Unable to write to %s. Please check that the directory exists or you have write permissions." %filename)
		print("*"*140)
		print(CEND)
	finally:
		f.close()
	return True
	
def main():

	parser = argparse.ArgumentParser(description='DevOps task.')

	# positional: url, path
	parser.add_argument('url', help='Provivde the url to make the request to')
	parser.add_argument('path', help='Output directory path')
	
	# optional: username, password
	parser.add_argument('--extensions', help='Image extensions to download (default png)\nExample: png|jpg')
	parser.add_argument('--username', help='Provivde the url to make the request to')
	parser.add_argument('--password', help='Output directory path')

	args = parser.parse_args()

	# base64 
	auth_encoded = None	
	if args.username is None and args.password:
		print("You can't provide a password without a username")
		return
	if args.username:
		username = args.username
		password = args.password
		
		auth = ('%s:%s' % (username, password))
		auth_encoded = base64.b64encode(auth.encode('ascii')).decode("ascii")
		# ::debug :: 
		# print(auth_encoded)
	
	url = args.url
	path = args.path
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
	if auth_encoded:
		headers['Authorization'] = 'Basic %s' % auth_encoded
	
	# disable ssl verification
	# ssl._create_default_https_context = ssl._create_unverified_context

	req = urllib.request.Request(url, headers=headers)
	# req.set_proxy('127.0.0.1:8080', 'http')
	
	print("Requesting %s..." %args.url)
	with urllib.request.urlopen(req) as response:
		html = response.read()

	# print(html)
	htmlsoup = BeautifulSoup(html, 'html.parser')

	# :: debug  ::
	# print(htmlsoup.prettify())

	# extensions = ''
	# if (argParse.extensions):
	
	allowed_extensions = 'png'
	if (args.extensions):
		allowed_extensions = args.extensions
		
	images = htmlsoup.find_all('img', {'src' : re.compile(r'('+allowed_extensions+')$', re.IGNORECASE)})
	
	
	# :: debug ::
	# print(images)
	
	count_total = 0
	
	for i in images:
		if i['src'].startswith('//'): # exception for UNC paths (https://en.wikipedia.org/wiki/Painting)
			link = i['src'].replace('//', '{uri.scheme}://'.format(uri=urlparse(url) ))
		else:
			if not (i['src'].startswith('http')):
				link = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url)) + '/' + i['src']
		print(link)
		print("Downloading %s... " %link, end='')
		result = downloadResource(link, path)
		if result:
			print("Done")
			count_total+=1
		else:
			print("Error!")
	
	print("*"*40)	
	print("Downloaded: %s images" % count_total)
	print("Extensions: %s" % allowed_extensions)
	print("*"*40)

if __name__ == "__main__":
    main()

