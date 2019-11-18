# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

from cmu_112_graphics import *
from tkinter import *
import requests
from bs4 import BeautifulSoup
import geopy
import textract
import math

# Takes a card from CMU's menu and extracts the information from it
# Based on the html structure of the cards
class Restaurant(object):
    # Creating the properties of the restaurant
    def __init__(self, card, app):
        self.card = card
        self.app = app
        self.name = self.card.find("h3", class_="name detailsLink").text.strip()
        hoursLoc = self.process(list(self.card.find("div", class_="hoursLocations").children))
        self.location = self.process(list(hoursLoc[0].children))[1].text.strip()
        self.hours = " ".join(hoursLoc[1].text.split())[15:]
        self.description = self.card.find("div", class_="description").text.strip()
        self.mapLink = self.process(list(hoursLoc[0].children))[1]["href"]
        self.latitude = float(self.mapLink[self.mapLink.find("place/") + len("place/"):self.mapLink.find(",")])
        self.longitude = float(self.mapLink[self.mapLink.find(",") + len(","):self.mapLink.find("/", self.mapLink.find(","))])
        # TODO: Get menu and sepecials

    # Representing the objects as strings
    def __repr__(self):
        return f"\n{self.name}\t{self.description}"

    # Removing most whitespace from a list/string L
    def process(self, L):
        return [x for x in L if x!='\n' and x!="\t" and x!='\r']
    
    def draw(self, canvas, number):
        row = 0
        col = number
        while col >= self.app.cols:
            row += 1
            col -= self.app.cols
        x0 = (self.app.margin + self.app.cellWidth) * col + self.app.margin
        y0 = (self.app.margin + self.app.cellHeight) * row + self.app.margin * 3\
            - self.app.scrollY + self.app.topHeight
        x1 = x0 + self.app.cellWidth
        y1 = y0 + self.app.cellHeight
        canvas.create_rectangle(x0, y0, x1, y1)
        if len(self.name) > 24:
            words = self.name.split(" ")
            mid = len(words) // 2
            canvas.create_text((x0+x1)/2, (y0+y1)/2-7, text=" ".join(words[:mid]))
            canvas.create_text((x0+x1)/2, (y0+y1)/2+7, text=" ".join(words[mid:]))
        else:
            canvas.create_text((x0+x1)/2, (y0+y1)/2, text=self.name)

# class that controls the user inteface
# TODO: Implement searching feature
# TODO: Implement login and user feature
class UserInterface(App):
    def appStarted(self):
        # Get the webpage with the info of all of the restaurant
        url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
        website = requests.get(url)
        source = website.text
        # Parse the website and create objects for each restaruraunt
        parser = BeautifulSoup(source,'html.parser')
        self.restaurants = [Restaurant(card, self) for card in parser.find_all("div", class_="card")]
        self.scrollY = 0
        self.backgroundColor = "white"
        self.getDimensions()
    
    def getDimensions(self):
        self.margin = 10
        self.topHeight = 50
        self.searchBarWidth = (self.width - self.margin * 3) * 3 / 4
        self.loginWidth = (self.width - self.margin * 3) / 4
        self.maxColWidth = 200
        self.cols = max(1, self.width // self.maxColWidth)
        self.rows = math.ceil(len(self.restaurants) / self.cols)
        self.cellWidth = (self.width - self.margin * (self.cols + 1)) // self.cols
        self.cellHeight = self.cellWidth
        self.maxScrollY = self.rows * (self.cellHeight + self.margin) + self.margin * 3 + self.topHeight - self.height
        if self.scrollY < 0:
            self.scrollY = 0
        elif self.scrollY > self.maxScrollY:
            self.scrollY = self.maxScrollY

    def keyPressed(self, event):
        if event.key == "Up":
            self.scrollY = max(0, self.scrollY - 10)
        elif event.key == "Down":
            self.scrollY = min(self.maxScrollY, self.scrollY + 10)
    
    def mousePressed(self, event):
        if 0 <= event.x - self.margin <= self.searchBarWidth and\
            0 <= event.y - self.margin <= self.topHeight:
            self.query = self.getUserInput("What do you want to eat?")
            if self.query is not None:
                pass
        elif 0 <= event.y - self.margin <= self.topHeight and\
            self.margin * 2 + self.searchBarWidth <= event.x <= self.width - self.margin:
            self.login = self.getUserInput("What is your username?")
            if self.login is not None:
                pass      

    def sizeChanged(self):
        self.getDimensions()
    
    def drawSearchAndLogin(self, canvas):
        # Clear what's under the header
        canvas.create_rectangle(0, 0, self.width, self.topHeight + self.margin * 2, fill="black")

        # Draw Search bar
        canvas.create_rectangle(self.margin, self.margin,\
            self.margin + self.searchBarWidth,\
            self.margin + self.topHeight, fill=self.backgroundColor)
        canvas.create_text(self.margin + self.searchBarWidth / 2,\
            self.margin + self.topHeight / 2, text="Search")
        
        # Draw the login button
        canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
            self.margin, self.width - self.margin,\
            self.margin + self.topHeight, fill=self.backgroundColor)
        canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
            self.margin + self.topHeight / 2, text="Login")

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill=self.backgroundColor)

        # Draw each restaurant card
        for i in range(len(self.restaurants)):
            restaurant = self.restaurants[i]
            restaurant.draw(canvas, i)
        
        # Draw the header
        self.drawSearchAndLogin(canvas)

def main():
    UserInterface(width=600, height=600)

if __name__ == "__main__":
    main()