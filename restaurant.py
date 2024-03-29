# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

# restaurant.py - has Restaurant class with CMURestaurant and YelpRestaurant as subclasses
# The restaurant classes contain all the information about a restaurant by webscraping the information

# CITATION - using tkinter as the graphics framework
# From https://github.com/python/cpython/tree/3.8/Lib/tkinter
from tkinter import *

# CITATION - using PIL's image class to display images on the canvas
# From https://pillow.readthedocs.io/en/3.1.x/index.html
from PIL import Image

# CITATION - using requests to load webpages
# From https://pypi.org/project/requests/
import requests

# CITATION - using BeautifulSoup to parse webpages
# From https://pypi.org/project/beautifulsoup4/
from bs4 import BeautifulSoup

# CITATION - using Nominatim to convert addresses into latitude and longitude
# From https://pypi.org/project/geopy/
from geopy.geocoders import Nominatim

# Importing Python's BytesIO class
from io import BytesIO

# Restaurant class - has helper functions that both
# CMURestaurant and YelpRestaurant need
class Restaurant(object):
    @staticmethod
    def loadParser(url):
        # Makes an HTTP GET request for the HTML code 
        # and creates a Beautiful Soup parse
        try:
            website = requests.get(url)
            source = website.text
            return BeautifulSoup(source,'html.parser')
        except:
            return None

    # Representing the objects as strings
    def __repr__(self):
        return f"{self.name}"
    
    def __hash__(self):
        return hash(self.name)

    # Equating restaurants based on name
    def __eq__(self, other):
        return isinstance(other, Restaurant) and self.name == other.name

    # Removing most whitespace from a list/string L
    def process(self, L):
        return [x for x in L if x!='\n' and x!="\t" and x!='\r']
    
    # Removes characters that python can't store in files
    # such as apostrophes and e with accents
    def fixUnicode(self, name):
        newName = ""
        for char in name:
            if ord(char) == 201:
                newName = newName + "E"
            elif ord(char) == 8217:
                newName = newName + "'"
            else:
                newName = newName + char
        return newName

    # Calculates the coordinates of where the restarant card
    # should be draw on the canvas
    def calculateCoordinates(self, number):
        # Finding the row/col
        row = 0
        col = number
        while col >= self.app.cols:
            row += 1
            col -= self.app.cols
        
        # Calculating the bounds of the cell
        self.x0 = (self.app.margin + self.app.cellWidth) * col + self.app.margin
        self.y0 = (self.app.margin + self.app.cellHeight) * row + self.app.margin * 3\
            - self.app.scrollY + self.app.topHeight
        self.x1 = self.x0 + self.app.cellWidth
        self.y1 = self.y0 + self.app.cellHeight

    # Draws a rectangle for the restaurant
    def draw(self, canvas, number):
        self.calculateCoordinates(number)
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1)

        # Displaying the name as two lines if it's too long
        if len(self.name) > 24:
            words = self.name.split(" ")
            mid = len(words) // 2
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2-7, text=" ".join(words[:mid]), font="Times 10")
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2+7, text=" ".join(words[mid:]), font="Times 10")
        else:
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2, text=self.name, font="Times 10")


# Takes a card from CMU's menu and extracts the information from it
# Based on the html structure of the cards
class CMURestaurant(Restaurant):
    # Creating the properties of the restaurant from the Beautiful Soup object card
    def __init__(self, card, app):
        self.card = card
        self.app = app
        name = self.card.find("h3", class_="name detailsLink").text.strip().upper()
        self.name = self.fixUnicode(name)
        hoursLoc = self.process(list(self.card.find("div", class_="hoursLocations").children))
        self.location = self.process(list(hoursLoc[0].children))[1].text.strip() + ", CMU's Campus"
        self.hours = " ".join(hoursLoc[1].text.split())[15:]
        self.description = self.card.find("div", class_="description").text.strip()
        self.mapLink = self.process(list(hoursLoc[0].children))[1]["href"]
        self.latitude = float(self.mapLink[self.mapLink.find("place/") +\
            len("place/"):self.mapLink.find(",")])
        self.longitude = float(self.mapLink[self.mapLink.find(",") +\
            len(","):self.mapLink.find("/", self.mapLink.find(","))])
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        newPageUrl = "https://apps.studentaffairs.cmu.edu/" + self.process(list(self.card.find("div", class_="links").children))[0]["href"]
        parser = Restaurant.loadParser(newPageUrl)
        if parser is None:
            self.specials = None
        else:
            specials = parser.find_all("div", class_="specialItems")
            self.specials = "".join(self.process(", ".join(item.div.ul.li.text.strip() for item in specials)))
        # CITATION: Using the image from each restaurant's website as the background for the cards
        imageUrl = "https://apps.studentaffairs.cmu.edu" + parser.find("div", class_="conceptImage").img["src"]
        imageContent = requests.get(imageUrl).content
        self.image = Image.open(BytesIO(imageContent))

# YelpRestaurant - Takes a card from yelp's website and
# parses it to get the name, location, and description of a restaurant
class YelpRestaurant(Restaurant):
    # Finding the properties of the restaurant
    def __init__(self, card, app):
        self.card = card
        self.app = app
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        name = self.card.find("h4", class_="lemon--h4__373c0__1yd__ heading" +\
            "--h4__373c0__27bDo alternate__373c0__2Mge5").find("a").text.upper()
        self.name = self.fixUnicode(name)
        self.location = self.card.find("address").find("span").text + ", Pittsburgh, PA"
        tags = self.card.find_all("span", class_="lemon--span__373c0__3997G text" +\
            "__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align" +\
            "--left__373c0__2XGa-")
        self.description = []
        for info in tags:
            self.description.append(info.a.text)
        self.description = ", ".join(self.description)
        geolocator = Nominatim(user_agent="CMU Foodie")
        try:
            loc = geolocator.geocode(self.location, timeout=10)
        except:
            loc = None
        # Some locations are not possible to get latitude and longitude from
        # Skip these ones
        if loc is None:
            self.useful = False
        else:
            self.latitude = loc.latitude
            self.longitude = loc.longitude
            self.useful = True
        self.specials = ""
        # CITATION - Using image from Yelp as background
        imageUrl = self.card.find("div", class_="lemon--div__373c0__1mboc on-click-container border-color--default__373c0__3-ifU").a.img["src"]        
        imageContent = requests.get(imageUrl).content
        self.image = Image.open(BytesIO(imageContent))

# Testing to get the menu and specials
if __name__ == "__main__":
    # Get the webpage with the info of all of the CMU Restaurants
    url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
    parser = Restaurant.loadParser(url)
    if parser is None:# If bad request or something failed, load from cached file
        with open("cmuCache.html", "r") as f:
            parser = BeautifulSoup(f, "html.parser")
    else:# Write to cached file results
        with open("cmuCache.html", "w") as f:
            # CITATION: Saving CMU dining information in case
            # the website can't be loaded in the future
            f.write(parser.prettify())
    cards = parser.find_all("div", class_="card")
    rests = []
    for card in cards:
        rests.append(CMURestaurant(card, "app"))