from flask import Flask, jsonify, request
import requests
import json
from BeautifulSoup import BeautifulSoup
app = Flask(__name__)

def isInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

@app.route("/find_beer",methods=['GET'])
def find_beer():
	search_url = "http://beeradvocate.com/search?qt=beer&q="+request.args['beer_name'].replace(" ","+")
	r = requests.get(search_url)
	soup = BeautifulSoup(r.text)
	links = soup.find(id="baContent").find("ul")
	# print beer_url
	urls = []
	for li in links:
		# print "li ", li
		link = li.find("a")
		beer_name = link.find("b").text
		beer_url = "http://beeradvocate.com"+link.get('href')
		urls.append({"url":beer_url,"name":beer_name})
	print urls
	return json.dumps(urls)

@app.route("/get_beer",methods=['GET'])
def get_beer():
	# search_url = "http://beeradvocate.com/search?qt=beer&q="+request.args['beer_name'].replace(" ","+")
	# r = requests.get(search_url)
	# soup = BeautifulSoup(r.text)
	# # print soup.find(id="baContent").find("ul")
	# links = soup.find(id="baContent").find("ul")
	# # print "Hello"
	# # print links
	# beer_url = "http://beeradvocate.com"+links.find("li").find("a").get('href')
	beer_url = request.args['beer_url']
	#beer_url = "http://beeradvocate.com"+link
	beer_id = beer_url.split("/")[-1]
	# print beer_id

	# Get beer image
	image_url = "http://beeradvocate.com/im/beers/"+beer_id+".jpg"
	beer_request = requests.get(beer_url)
	beer_soup = BeautifulSoup(beer_request.text)
	# print beer_soup

	# Get rating
	rating = beer_soup.find("span","BAscore_big").text
	styleAbvParent = beer_soup.find(text='Style | ABV').findParent('td').text
	style = styleAbvParent.split("ABV")[1].split("|")[0]
	abv = styleAbvParent.split("ABV")[1].split("|")[1].split("ABV")[0].replace("&nbsp;","").strip()

  # Get RateBeer rating
	rb_search_url = "http://google.com/search?q=ratebeer+"+beer_soup.find("h1").text.replace(" ","+")
	rb_req = requests.get(rb_search_url)
	rb_soup = BeautifulSoup(rb_req.text)
	rb_rating = rb_soup.find('h3').text.split("-")[1].split("atRateBeer")[0].strip()

	overall = rating
	if not isInt(rating) and isInt(rb_rating):
		overall = rb_rating
	if isInt(rating) and isInt(rb_rating):
		overall = str((int(rating) + int(rb_rating))/2)

	# Create a dict
	beer_info = {'image': image_url, 'rating': overall, 'style': style, 'abv': abv}

	print beer_info

	# Return JSON
	return_json = jsonify(beer_info)

	return return_json
	#return "<img src='"+image_url+"'/>\nrating: "+rating


if __name__ == "__main__":
    app.run()