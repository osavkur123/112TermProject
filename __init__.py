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
        self.newUserScreen = UserCreationScreen()
        self.setActiveMode(self.mainScreen)

class RestaurantScreen(Mode):
    def __init__(self, mainApp, restaurant):
        super().__init__()
        self.restaurant = restaurant
        self.mainApp = mainApp
        self.rating = ""
        self.comment = ""
    
    def appStarted(self):
        self.getDimensions()

    def getDimensions(self):
        self.exitButton = (self.width * 7 / 8, self.mainApp.margin,\
            self.width - self.mainApp.margin,\
            self.app.height/20 + self.mainApp.margin)
        self.ratingButton = (self.mainApp.margin, self.height * 5 / 6,\
            (self.width - self.mainApp.margin) / 2,\
            self.height - self.mainApp.margin)
        self.commentButton = ((self.width + self.mainApp.margin) / 2,\
            self.height * 5 / 6, self.width - self.mainApp.margin,\
            self.height - self.mainApp.margin)

    def mousePressed(self, event):
        if self.exitButton[0] <= event.x <= self.exitButton[2] and\
            self.exitButton[1] <= event.y <= self.exitButton[3]:
            self.app.setActiveMode(self.app.mainScreen)
        
        if self.mainApp.user is not None:
            if self.ratingButton[0] <= event.x <= self.ratingButton[2] and\
                self.ratingButton[1] <= event.y <= self.ratingButton[3]:
                self.rating = self.getUserInput(f"HOW DO YOU RATE {self.restaurant.name}?")

            elif self.commentButton[0] <= event.x <= self.commentButton[2] and\
                self.commentButton[1] <= event.y <= self.commentButton[3]:
                self.comment = self.getUserInput(f"WHAT DO YOU THINK ABOUT {self.restaurant.name}?")
            
            if self.rating != "" and self.rating.isdigit() and self.comment != "":
                self.mainApp.user.reviews[self.restaurant.name] = {"rating": self.rating, "comment": self.comment}
                self.mainApp.user.updateFile()
    
    def sizeChanged(self):
        self.getDimensions()

    def redrawAll(self, canvas):
        canvas.create_rectangle(*self.exitButton)
        canvas.create_text((self.exitButton[0]+self.exitButton[2])/2, (self.exitButton[1]+self.exitButton[3])/2, text="EXIT")
        canvas.create_text(self.width/2, self.app.height/4, text=self.restaurant.name)
        canvas.create_text(self.width/2, self.app.height/2, text=self.restaurant.description)
        if self.mainApp.user is not None:
            canvas.create_text(self.width/2, self.app.height/10, text="Welcome " + self.mainApp.user.username)
            canvas.create_rectangle(*self.ratingButton)
            if self.rating == "":
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2, (self.ratingButton[1]+self.ratingButton[3])/2, text="RATE")
            elif not self.rating.isdigit():
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2, (self.ratingButton[1]+self.ratingButton[3])/2, text="PLEASE ENTER A NUMBER")
            else:
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2, (self.ratingButton[1]+self.ratingButton[3])/2, text=f"RATING: {self.rating}")
            canvas.create_rectangle(*self.commentButton)
            if self.comment == "":
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2, (self.commentButton[1]+self.commentButton[3])/2, text="COMMENT")
            else:
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2, (self.commentButton[1]+self.commentButton[3])/2, text=f"COMMENT: {self.comment}")

# Animation that handles the user creating a profile
class UserCreationScreen(Mode):
    def appStarted(self):
        self.getDimensions()
        self.username = ""
        self.pass1 = ""
        self.pass2 = ""
    
    def getDimensions(self):
        self.margin = 10
        self.cellHeight = 50
        self.usernameBox = (self.margin, self.height / 6,\
            self.width - self.margin, self.height / 6 + self.cellHeight)
        self.pass1Box = (self.margin, self.height / 3,\
            self.width - self.margin, self.height / 3 + self.cellHeight)
        self.pass2Box = (self.margin, self.height / 2,\
            self.width - self.margin, self.height / 2 + self.cellHeight)
        self.cancelBox = (self.margin, self.height * 2 / 3,\
            (self.width - self.margin) / 2, self.height * 2 / 3 + self.cellHeight)
        self.submitBox = ((self.width + self.margin) / 2, self.height * 2 / 3,\
            self.width - self.margin, self.height * 2 / 3 + self.cellHeight)

    @staticmethod
    def clickWithinBox(event, box):
        return box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]

    def mousePressed(self, event):
        if UserCreationScreen.clickWithinBox(event, self.usernameBox):
            self.username = self.getUserInput("Enter username")
        elif UserCreationScreen.clickWithinBox(event, self.pass1Box):
            self.pass1 = self.getUserInput("Enter password")
        elif UserCreationScreen.clickWithinBox(event, self.pass2Box):
            self.pass2 = self.getUserInput("Confirm password")
        elif UserCreationScreen.clickWithinBox(event, self.cancelBox):
            self.app.setActiveMode(self.app.mainScreen)
        elif UserCreationScreen.clickWithinBox(event, self.submitBox):
            usernames = []
            with open("users.xml", "r") as database:
                data = BeautifulSoup(database, "xml")
                usernames = [user["username"] for user in data.find_all("user")]
            if self.username not in usernames and self.pass1 == self.pass2 and self.pass1 != "":
                newUser = userData.User(self.username, self.pass1, dict())
                newUser.updateFile()
                self.app.setActiveMode(self.app.mainScreen)

    def sizeChanged(self):
        self.getDimensions()

    @staticmethod
    def drawTextWithinBox(text, box, canvas):
        canvas.create_text((box[0]+box[2])/2, (box[1]+box[3])/2, text=text)

    def redrawAll(self, canvas):
        canvas.create_rectangle(*self.usernameBox)
        UserCreationScreen.drawTextWithinBox("Enter Username", self.usernameBox, canvas)
        canvas.create_rectangle(*self.pass1Box)
        UserCreationScreen.drawTextWithinBox("Enter Password", self.pass1Box, canvas)
        canvas.create_rectangle(*self.pass2Box)
        UserCreationScreen.drawTextWithinBox("Confirm Password", self.pass2Box, canvas)
        canvas.create_rectangle(*self.cancelBox)
        UserCreationScreen.drawTextWithinBox("Cancel", self.cancelBox, canvas)
        canvas.create_rectangle(*self.submitBox)
        UserCreationScreen.drawTextWithinBox("Submit", self.submitBox, canvas)

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
                if self.margin <= event.y <= self.margin + self.topHeight / 2 - self.margin/4: 
                    # testUser user password is "hello"
                    # other user password is "potatoes"
                    username = self.getUserInput("What is your username?")
                    password = self.getUserInput("What is your password?")
                    self.user = userData.login(username, password)
                elif self.margin + self.topHeight / 2 + self.margin / 4 <= event.y <= self.margin + self.topHeight:
                    self.app.setActiveMode(self.app.newUserScreen)
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
        
        # Draw the login and registration button
        if self.user is None:       
            canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
                self.margin, self.width - self.margin,\
                self.margin + self.topHeight / 2 - self.margin/4, fill=self.backgroundColor)
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight / 4 - self.margin / 8, text="Login")
            canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
                self.margin + self.topHeight / 2 + self.margin/4, self.width - self.margin,\
                self.margin + self.topHeight, fill=self.backgroundColor)
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight * 3 / 4 + self.margin / 8, text="Sign Up")
        else:
            canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
                self.margin, self.width - self.margin,\
                self.margin + self.topHeight, fill=self.backgroundColor)
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight / 2, text="Logout " + self.user.username)

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