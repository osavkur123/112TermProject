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
import restaurant
import userData


# class that controls the user inteface
class UserInterface(ModalApp):
    def appStarted(self):
        self.mainScreen = HomeScreen()
        self.setActiveMode(self.mainScreen)

class RestaurantScreen(Mode):
    def __init__(self, mainApp, restaurant):
        super().__init__()
        self.restaurant = restaurant
        self.mainApp = mainApp
    
    def appStarted(self):
        self.getDimensions()

    def getDimensions(self):
        self.exitButton = (self.width * 7 / 8, self.mainApp.margin, self.width - self.mainApp.margin, self.app.height/20 + self.mainApp.margin)

    def mousePressed(self, event):
        if self.exitButton[0] <= event.x <= self.exitButton[2] and\
            self.exitButton[1] <= event.y <= self.exitButton[3]:
            self.app.setActiveMode(self.app.mainScreen)
    
    def sizeChanged(self):
        self.getDimensions()

    def redrawAll(self, canvas):
        canvas.create_rectangle(*self.exitButton)
        canvas.create_text((self.exitButton[0]+self.exitButton[2])/2, (self.exitButton[1]+self.exitButton[3])/2, text="EXIT")
        canvas.create_text(self.width/2, self.app.height/4, text=self.restaurant.name)
        canvas.create_text(self.width/2, self.app.height/2, text=self.restaurant.description)
        if self.mainApp.user is not None:
            canvas.create_text(self.width/2, self.app.height/10, text="Welcome " + self.mainApp.user.username)

# class that displays the main screen
# TODO: Implement searching feature
class HomeScreen(Mode):
    def appStarted(self):
        # Get the webpage with the info of all of the restaurant
        url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
        website = requests.get(url)
        source = website.text
        # Parse the website and create objects for each restaurant
        parser = BeautifulSoup(source,'html.parser')
        self.restaurants = [restaurant.Restaurant(card, self) for card in parser.find_all("div", class_="card")]
        self.scrollY = 0
        self.backgroundColor = "white"
        self.getDimensions()
        self.user = None
        self.query = None
    
    # Find the dimensions for the search bar and each of the restaurant cells
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
        self.maxScrollY = self.rows * (self.cellHeight + self.margin) + self.margin * 3 + self.topHeight - self.app.height
        if self.scrollY < 0:
            self.scrollY = 0
        elif self.scrollY > self.maxScrollY:
            self.scrollY = self.maxScrollY

    def keyPressed(self, event):
        if event.key == "Up":
            self.scrollY = max(0, self.scrollY - 10)
        elif event.key == "Down":
            self.scrollY = min(self.maxScrollY, self.scrollY + 10)
    
    def timerFired(self):
        if (self.cellWidth + self.margin) * self.cols + self.margin != self.width or\
            (self.cellHeight + self.margin) * self.rows + self.margin + self.topHeight != self.height + self.maxScrollY:
            self.getDimensions()

    
    def mousePressed(self, event):
        if 0 <= event.x - self.margin <= self.searchBarWidth and\
            0 <= event.y - self.margin <= self.topHeight:
            self.query = self.getUserInput("What do you want to eat?")
            if self.query is not None:
                pass
        elif 0 <= event.y - self.margin <= self.topHeight and\
            self.margin * 2 + self.searchBarWidth <= event.x <= self.width - self.margin:
            if self.user is None:
                login = self.getUserInput("What is your username?")
                self.user = userData.login(login)
            else:
                self.user = self.user.logout()
        else:
            for restaurant in self.restaurants:
                if restaurant.x0 <= event.x <= restaurant.x1 and\
                    restaurant.y0 <= event.y <= restaurant.y1:
                    self.app.setActiveMode(RestaurantScreen(self, restaurant))
                    break

    def sizeChanged(self):
        self.getDimensions()
    
    def drawSearchAndLogin(self, canvas):
        # Clear what's under the header
        canvas.create_rectangle(0, 0, self.width, self.topHeight + self.margin * 2, fill="black")

        # Draw Search bar
        canvas.create_rectangle(self.margin, self.margin,\
            self.margin + self.searchBarWidth,\
            self.margin + self.topHeight, fill=self.backgroundColor)
        if self.query is None or self.query == "":
            canvas.create_text(self.margin + self.searchBarWidth / 2,\
                self.margin + self.topHeight / 2, text="Search")
        else:
            canvas.create_text(self.margin + self.searchBarWidth / 2,\
                self.margin + self.topHeight / 2, text=self.query)
        
        # Draw the login button
        canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
            self.margin, self.width - self.margin,\
            self.margin + self.topHeight, fill=self.backgroundColor)
        if self.user is None:
            status = "Login"
        else:
            status = "Logout " + self.user.username
        canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
            self.margin + self.topHeight / 2, text=status)

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.app.height, fill=self.backgroundColor)

        # Draw each restaurant card
        for i in range(len(self.restaurants)):
            restaurant = self.restaurants[i]
            restaurant.draw(canvas, i)
        
        # Draw the header
        self.drawSearchAndLogin(canvas)

if __name__ == "__main__":
    UserInterface(width=600, height=600)