# Name: Omkar Savkur
# AndrewID: osavkur
# tech demo

import requests
from bs4 import BeautifulSoup
import geopy
import textract

# Takes a card from CMU's menu and extracts the information from it
# Based on the html structure of the cards
class Restaurant(object):
    # Creating the properties of the restaurant
    def __init__(self, card):
        self.card = card
        self.name = self.card.find("h3", class_="name detailsLink").text.strip().title()
        hoursLoc = self.process(list(self.card.find("div", class_="hoursLocations").children))
        self.location = self.process(list(hoursLoc[0].children))[1].text.strip()
        self.hours = " ".join(hoursLoc[1].text.split())[15:]
        self.description = self.card.find("div", class_="description").text.strip()
        self.mapLink = self.process(list(hoursLoc[0].children))[1]["href"]
        self.latitude = float(self.mapLink[self.mapLink.find("place/") + len("place/"):self.mapLink.find(",")])
        self.longitude = float(self.mapLink[self.mapLink.find(",") + len(","):self.mapLink.find("/", self.mapLink.find(","))])

    # Representing the objects as strings
    def __repr__(self):
        return f"\n{self.name}\t{self.description}"

    # Removing most whitespace from a list/string L
    def process(self, L):
        return [x for x in L if x!='\n' and x!="\t" and x!='\r']

def main():
    # Get the webpage with the info of all of the restaurant
    url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
    website = requests.get(url)
    source = website.text
    # Parse the website and create objects for each restaruraunt
    parser = BeautifulSoup(source,'html.parser')
    restaurants = [Restaurant(card) for card in parser.find_all("div", class_="card")]
    print(restaurants)

    # Converting Address into a latitude and longitude
    geolocator = geopy.geocoders.Nominatim(user_agent="trial")
    location = geolocator.geocode("5000 Forbes Avenue PA")
    print(location.latitude, location.longitude)

    # Get a website menu and extracting the text from the pdf
    menu = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/conceptAssets/menus/F19BackBarGrillMenu_22x28.pdf"
    open("menu.pdf", "wb").write(requests.get(menu, allow_redirects=True).content)
    menuText = textract.process("menu.pdf").decode("UTF-8")
    print(menuText)


if __name__ == "__main__":
    main()