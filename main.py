from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import json
from BeautifulSoup import BeautifulSoup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/beer.db'
db = SQLAlchemy(app)

class Beer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200))
	brewery = db.Column(db.String(200))
	BA_URL = db.Column(db.String(200))
	BA_rating = db.Column(db.Integer)
	ABV = db.Column(db.String(20))
	style = db.Column(db.String(200))
	image_url = db.Column(db.String(200))
	location = db.Column(db.String(200))

	def __init__(self, beerName, brewery,url,rating,abv,style,image,location):
		self.name = beerName
		self.brewery = brewery
		self.BA_URL = url
		self.BA_rating = rating
		self.ABV = abv
		self.style = style
		self.image_url = image
		self.location = location

def isInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

@app.route("/autocomplete",methods=['GET'])
def autocomplete():
	beer_name = request.args['beer_name']
	matchingBeers = Beer.query.filter(Beer.name.like("%"+beer_name+"%")).all()
	print matchingBeers
	print map(lambda x:{'name':x.name,'url':x.BA_URL},matchingBeers)
	return json.dumps(map(lambda x:{'name':x.name,'url':x.BA_URL},matchingBeers))

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
	beer_url = request.args['beer_url']
	beer_id = beer_url.split("/")[-1]
	matched_beer = Beer.query.filter_by(BA_URL=beer_url).first() 
	if matched_beer is not None:
		print matched_beer
		return jsonify({'image':matched_beer.image_url,
						'rating':matched_beer.BA_rating,
						'style':matched_beer.style,
						'abv':matched_beer.ABV,
						'name':matched_beer.name,
						'location':matched_beer.location,
						'brewery':matched_beer.brewery,
						'url':matched_beer.BA_URL})

	# Get beer image
	image_url = "im/beers/"+beer_id+".jpg"
	beer_request = requests.get(beer_url)
	beer_soup = BeautifulSoup(beer_request.text)
	beer_name = beer_soup.find("div","titleBar").find("h1").text.split("-")[0]
	# print beer_soup

	# Get rating and other information
	rating = beer_soup.find("span","BAscore_big").text
	styleAbvParent = beer_soup.find(text='Style | ABV').findParent('td').text
	style = styleAbvParent.split("ABV")[1].split("|")[0]
	abv = styleAbvParent.split("ABV")[1].split("|")[1].split("ABV")[0].replace("&nbsp;","").strip()
	brewery = styleAbvParent.split("Brewed by:")[1].split("&nbsp;")[0].strip()
	location = styleAbvParent.split("&nbsp;")[1].split("Style")[0]

  # Get RateBeer rating
	rb_search_url = "http://google.com/search?q=ratebeer+"+beer_name.replace(" ","+")
	print rb_search_url
	print beer_soup.find("h1").span.text.replace(" ","+")
	rb_req = requests.get(rb_search_url)
	rb_soup = BeautifulSoup(rb_req.text)
	rb_rating = rb_soup.find('h3').text.split("-")[1].split("atRateBeer")[0].strip()
	
	rb_brewery_search_url = "http://google.com/search?q=ratebeer+"+brewery.replace(" ","+")
	rb_req = requests.get(rb_brewery_search_url)
	rb_soup = BeautifulSoup(rb_req.text)
	rb_location = rb_soup.find('h3').text[rb_soup.find("h3").text.find(",")+1:].split("-RateBeer")[0].strip()
	if len(rb_location) < 100 and rb_location.find("RateBeer") == -1 and rb_location.find("...") == -1:
		location = rb_location

	overall = rating
	if not isInt(rating) and isInt(rb_rating):
		overall = rb_rating
	if isInt(rating) and isInt(rb_rating):
		overall = str((int(rating) + int(rb_rating))/2)

	# Save to Database
	newBeer = Beer(beer_name,brewery,beer_url,rating,abv,style,image_url,location)
	db.session.add(newBeer)
	db.session.commit()
	#print newBeer

	# Create a dict
	beer_info = {'image': image_url, 'rating': overall, 'style': style, 'abv': abv, 'name':beer_name, 'brewery':brewery, 'location':location, 'url':beer_url}

	print beer_info

	# Return JSON
	return_json = jsonify(beer_info)

	return return_json
	#return "<img src='"+image_url+"'/>\nrating: "+rating


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
