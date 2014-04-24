from urllib2 import urlopen
from bs4 import BeautifulSoup, Comment
from collections import Counter
import re


def mangeurDURL(url):
	# Fetch
	html = urlopen(url).read()
	soup = BeautifulSoup(html)

	# Remove <script>
	[x.extract() for x in soup.findAll('script')]

	# Remove comments
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]

	# Get all text
	data = soup.findAll(text=True)

	# Transform to string
	string = unicode.join(u'\n', map(unicode, data))
	string = string.replace('\n', ' ')

	# Count words
	counts = Counter()
	counts.update(word.strip('.,?!"\'').lower() for word in string.split())

	# Update BDD woth counts



	
	urls = soup.findAll("a")
	regex = re.compile(r'^http')
	filtered = [i['href'] for i in urls if regex.search(i['href'])]


	return filtered


url = 'http://www.d8.tv/d8-series/pid6654-d8-longmire.html'
urls = mangeurDURL(url)

for url in urls:
	print(url)