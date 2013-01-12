from flask import Flask, jsonify, request
import requests
from BeautifulSoup import BeautifulSoup
app = Flask(__name__)

@app.route("/",methods=['GET'])
def get_beer():
	search_url = "http://beeradvocate.com/search?qt=beer&q="+request.args['beer_name'].replace(" ","+")
	r = requests.get(search_url)
	soup = BeautifulSoup(r.text)
	print soup.find(id="baContent").find("ul")
	links = soup.find(id="baContent").find("ul")
	print "Hello"
	print links
	beer_url = "http://beeradvocate.com"+links.find("li").find("a").get('href')
	print beer_url
	for li in links:
		print "li ", li
		link = li.find("a")
		if link.find("b").text.upper() == request.args['beer_name'].upper():
			beer_url = "http://beeradvocate.com"+link.get('href')
	print beer_url
	#beer_url = "http://beeradvocate.com"+link
	beer_id = beer_url.split("/")[-1]
	print beer_id
	image_url = "http://beeradvocate.com/im/beers/"+beer_id+".jpg"
	beer_request = requests.get(beer_url)
	beer_soup = BeautifulSoup(beer_request.text)
	print beer_soup
	rating = beer_soup.find("span","BAscore_big").text
	return "<img src='"+image_url+"'/>\nrating: "+rating


if __name__ == "__main__":
    app.run()