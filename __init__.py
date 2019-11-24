# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

# The main file, __init__.py
# Runs the user interface and handles the recommendation algorithm
# Calls fuctions from userData.py to log users in and out
# Uses classes from restaurant.py to store all the information scraped from the internet

# CITATION - using CMU's 15-112 graphics library to help with drawing to the canvas
# From course notes: http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *

# CITATION - using tkinter as the graphics framework
# Url: https://github.com/python/cpython/tree/3.8/Lib/tkinter
from tkinter import *

# CITATION - using BeautifulSoup to parse webpages
# From https://pypi.org/project/beautifulsoup4/
from bs4 import BeautifulSoup

# Using python's builtin math library
import math

# importing from other file in same directory
import restaurant
import userData

# class that controls the user inteface
# switches between animations
class UserInterface(ModalApp):
    def appStarted(self):
        self.mainScreen = HomeScreen()
        self.newUserScreen = UserCreationScreen()
        self.setActiveMode(self.mainScreen)

# Animation that displays the restaurant information
# and allows users to rate restaurants
class RestaurantScreen(Mode):
    def __init__(self, mainApp, restaurant):
        super().__init__()
        self.restaurant = restaurant
        self.mainApp = mainApp
        self.rating = ""
        self.comment = ""
    
    # Get the dimensions at the beginning of the animation
    def appStarted(self):
        self.getDimensions()

    # Calculates the sizes of each button
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

    # Handles mouse clicks
    def mousePressed(self, event):
        # Exit button takes user back to the main screen
        if self.exitButton[0] <= event.x <= self.exitButton[2] and\
            self.exitButton[1] <= event.y <= self.exitButton[3]:
            self.app.setActiveMode(self.app.mainScreen)
        
        # If the user is logged in, handle review system
        if self.mainApp.user is not None:
            # Get rating of restaurant
            if self.ratingButton[0] <= event.x <= self.ratingButton[2] and\
                self.ratingButton[1] <= event.y <= self.ratingButton[3]:
                self.rating = self.getUserInput(\
                    f"HOW DO YOU RATE {self.restaurant.name}?")

            # Get comment
            elif self.commentButton[0] <= event.x <= self.commentButton[2] and\
                self.commentButton[1] <= event.y <= self.commentButton[3]:
                self.comment = self.getUserInput(\
                    f"WHAT DO YOU THINK ABOUT {self.restaurant.name}?")
            
            # Update the file if both are filled out
            if self.rating != "" and self.rating is not None and\
                self.rating.isdigit() and self.comment != "" and self.comment is not None:
                self.mainApp.user.reviews[self.restaurant.name] = {
                    "rating": int(self.rating), "comment": self.comment}
                self.mainApp.user.updateFile()
    
    # Change the location of the buttons based on the size of the canvas
    def sizeChanged(self):
        self.getDimensions()

    # Draw the buttons and the restaurant name and description
    def redrawAll(self, canvas):
        canvas.create_rectangle(*self.exitButton)
        canvas.create_text((self.exitButton[0]+self.exitButton[2])/2,\
            (self.exitButton[1]+self.exitButton[3])/2, text="EXIT")
        canvas.create_text(self.width/2, self.app.height/4,\
            text=self.restaurant.name)
        canvas.create_text(self.width/2, self.app.height/2,\
            text=self.restaurant.description)
        if self.mainApp.user is not None:
            canvas.create_text(self.width/2, self.app.height/10,\
                text="Welcome " + self.mainApp.user.username)
            canvas.create_rectangle(*self.ratingButton)
            if self.rating == "":
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text="RATE")
            elif not self.rating.isdigit():
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text="PLEASE ENTER A NUMBER")
            else:
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text=f"RATING: {self.rating}")
            canvas.create_rectangle(*self.commentButton)
            if self.comment == "":
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2,\
                    (self.commentButton[1]+self.commentButton[3])/2, text="COMMENT")
            else:
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2,\
                    (self.commentButton[1]+self.commentButton[3])/2, text=f"COMMENT: {self.comment}")

# Animation that handles the user creating a profile
class UserCreationScreen(Mode):
    def appStarted(self):
        self.getDimensions()
        self.username = ""
        self.pass1 = ""
        self.pass2 = ""
    
    # Determine positions of boxes on the canvas
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

    # determine if a click is within a box
    @staticmethod
    def clickWithinBox(event, box):
        return box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]

    # Handles getting the user input and creating a new user
    def mousePressed(self, event):
        if UserCreationScreen.clickWithinBox(event, self.usernameBox):
            self.username = self.getUserInput("Enter username")
        elif UserCreationScreen.clickWithinBox(event, self.pass1Box):
            self.pass1 = self.getUserInput("Enter password")
        elif UserCreationScreen.clickWithinBox(event, self.pass2Box):
            self.pass2 = self.getUserInput("Confirm password")
        # Exit back to main screen
        elif UserCreationScreen.clickWithinBox(event, self.cancelBox):
            self.app.setActiveMode(self.app.mainScreen)
        # Create a new user if passwords match and username is unique
        elif UserCreationScreen.clickWithinBox(event, self.submitBox):
            if self.pass1 == self.pass2 and self.pass1 != "":
                usernames = []
                with open("users.xml", "r") as database:
                    data = BeautifulSoup(database, "xml")
                    usernames = [user["username"] for user in data.find_all("user")]
                if self.username not in usernames:
                    newUser = userData.User(self.username, userData.passwordHash(self.pass1), dict())
                    newUser.updateFile()
                    self.app.setActiveMode(self.app.mainScreen)

    # Get the positions of boxes
    def sizeChanged(self):
        self.getDimensions()

    # Draw the text within a box
    @staticmethod
    def drawTextWithinBox(text, box, canvas):
        canvas.create_text((box[0]+box[2])/2, (box[1]+box[3])/2, text=text)

    # Display the boxes and text for the user
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
        self.getRestaurantInfo()
        self.scrollY = 0
        self.backgroundColor = "white"
        self.user = None
        self.otherUsers = []
        self.query = None
        self.recommendations = []
        self.getDimensions()
    
    def getRestaurantInfo(self):
        # Get the webpage with the info of all of the CMU Restaurants
        url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
        parser = restaurant.Restaurant.loadParser(url)
        if parser is None:# If bad request or something failed, load from cached file
            with open("cmuCache.html", "r") as f:
                parser = BeautifulSoup(f, "html.parser")
        else:# Write to cached file results
            with open("cmuCache.html", "w") as f:
                f.write(parser.prettify())
        cards = parser.find_all("div", class_="card")
        self.restaurants = [restaurant.CMURestaurant(card, self) for card in cards]
        # Get the webpage with other restaurants
        url = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=5000%"+\
            "20Forbes%20Ave%2C%20Pittsburgh%2C%20PA&l=g%3A-79.94270148285887%2"+\
            "C40.45110570038694%2C-79.95452895199287%2C40.44305530316755"
        parser = restaurant.Restaurant.loadParser(url)
        # Creating all the Yelp Restaurant objects
        if parser is None or len(parser.find_all("li",\
            class_="lemon--li__373c0__1r9wz border-color--default__373c0__3-ifU")) == 0:
             with open("yelpCache.html", "rb") as f:
                parser = restaurant.BeautifulSoup(f.read(), "html.parser")
        cards = parser.find_all("li",\
            class_="lemon--li__373c0__1r9wz border-color--default__373c0__3-ifU")
        for card in cards:
            if card.find("h4") is not None:
                rest = restaurant.YelpRestaurant(card, self)
                if rest.useful and rest not in self.restaurants:
                    self.restaurants.append(rest)
        self.restaurants.sort(key = lambda rest: rest.name)

    # Find the dimensions for the search bar and each of the restaurant cells
    def getDimensions(self):
        self.margin = 10
        self.topHeight = 50
        self.searchBarWidth = (self.width - self.margin * 3) * 3 / 4
        self.loginWidth = (self.width - self.margin * 3) / 4
        self.maxColWidth = 200
        self.cols = max(1, self.width // self.maxColWidth)
        if len(self.recommendations) == 0:
            self.rows = math.ceil(len(self.restaurants) / self.cols)
        else:
            self.rows = math.ceil(len(self.recommendations) / self.cols)
        self.cellWidth = (self.width - self.margin * (self.cols + 1)) // self.cols
        self.cellHeight = self.cellWidth
        self.maxScrollY = self.rows * (self.cellHeight + self.margin) +\
            self.margin * 3 + self.topHeight - self.app.height
        if self.scrollY < 0:
            self.scrollY = 0
        elif self.scrollY > self.maxScrollY:
            self.scrollY = self.maxScrollY

    # Change scrollY based on key presses
    def keyPressed(self, event):
        if event.key == "Up":
            self.scrollY = max(0, self.scrollY - 10)
        elif event.key == "Down":
            self.scrollY = min(self.maxScrollY, self.scrollY + 10)
    
    # Check and readjust for imperfections in drawing
    def timerFired(self):
        if (self.cellWidth + self.margin) * self.cols + self.margin != self.width or\
            (self.cellHeight + self.margin) * self.rows + self.margin +\
            self.topHeight != self.height + self.maxScrollY:
            self.getDimensions()

    # Handles searching, login, registration, logout, and recommendation
    def mousePressed(self, event):
        if 0 <= event.x - self.margin <= self.searchBarWidth and\
            0 <= event.y - self.margin <= self.topHeight:
            if self.query is None or self.query == "":
                self.query = self.getUserInput("What do you want to eat?")
                self.searchRestaurants()
            else:
                self.query = None
                self.restaurants.sort(key=lambda rest:rest.name)
        elif 0 <= event.y - self.margin <= self.topHeight and\
            self.margin * 2 + self.searchBarWidth <= event.x <= self.width - self.margin:
            if self.user is None:
                if self.margin <= event.y <= self.margin + self.topHeight / 2 - self.margin/4: 
                    # testUser user password is "hello"
                    # other user password is "potatoes"
                    # newUser user password is "pass"
                    username = self.getUserInput("What is your username?")
                    password = userData.passwordHash(self.getUserInput("What is your password?"))
                    self.user = userData.login(username, password)
                elif self.margin + self.topHeight / 2 + self.margin / 4 <=\
                    event.y <= self.margin + self.topHeight:
                    self.app.setActiveMode(self.app.newUserScreen)
            else:
                if self.margin <= event.y <= self.margin + self.topHeight / 2 - self.margin/4: 
                    self.user = self.user.logout()
                    self.otherUsers = []
                    self.recommendations = []
                elif self.margin + self.topHeight / 2 + self.margin / 4 <= event.y <=\
                    self.margin + self.topHeight:
                    if len(self.recommendations) == 0:
                        # call the recommendation function
                        self.getRecommendations()
                    else:
                        self.recommendations = []
                        self.getDimensions()
        else:
            self.findClickedRestaurant(event)

    # Finds which restaurant has been clicked and
    # opens that restaurant's info/review page
    def findClickedRestaurant(self, event):
        if len(self.recommendations) == 0:
            for rest in self.restaurants:
                if rest.x0 <= event.x <= rest.x1 and\
                    rest.y0 <= event.y <= rest.y1:
                    self.app.setActiveMode(RestaurantScreen(self, rest))
                    break
        else:
            for rest in self.recommendations:
                if rest.x0 <= event.x <= rest.x1 and\
                    rest.y0 <= event.y <= rest.y1:
                    self.app.setActiveMode(RestaurantScreen(self, rest))
                    break
    
    # Recommendation funcition - using K-Nearest Neighbors algorithm
    # Source for Algorigthm:
    # https://medium.com/capital-one-tech/k-nearest-neighbors-knn-algorithm-for-machine-learning-e883219c8f26
    def getRecommendations(self):
        k = 3
        self.otherUsers = self.user.getOtherUsers()
        distances = {}
        for otherUser in self.otherUsers:
            distances[otherUser] = self.getDistance(otherUser)
        neighbors = HomeScreen.getNearestNeighbors(distances, k)
        recommendations = set()
        for user in neighbors:
            for restaurant in self.restaurants:
                if restaurant.name in user.reviews and\
                    user.reviews[restaurant.name]["rating"] > 9:
                    recommendations.add(restaurant)
        self.recommendations = list(recommendations)
        self.recommendations.sort(key=lambda rest: rest.name)
        self.getDimensions()

    # Calculates the "distance" between the current user and the other user
    # Distance is based on the similarities of the ratings between users
    # If the users both have the same rating, they get a 1 for that restaurant
    # If only one user rated a restaurant, then the other users' score is a 5 by default
    # If neither user rated a restaurant, then the default is 7
    def getDistance(self, otherUser):
        distanceSquared = 0
        for restaurant in self.restaurants:
            if restaurant.name in self.user.reviews and restaurant.name in otherUser.reviews:
                distanceSquared += (otherUser.reviews[restaurant.name]["rating"] - self.user.reviews[restaurant.name]["rating"]) ** 2
            elif restaurant.name in self.user.reviews:
                distanceSquared += (5 - self.user.reviews[restaurant.name]["rating"]) ** 2
            elif restaurant.name in otherUser.reviews:
                distanceSquared += (otherUser.reviews[restaurant.name]["rating"] - 5) ** 2
            else:
                distanceSquared += 7 ** 2
        return math.sqrt(distanceSquared)

    # Takes the dictionary distances mapping other users 
    # to their distance from the current user and returns a list of the
    # k (or the entire list) users with the smallest distance
    @staticmethod
    def getNearestNeighbors(distances, k):
        users = list(distances.keys())
        k = min(k, len(users))
        result = sorted(users, key = lambda user: distances[user])
        return result[:k]

    # Search function that orders the restaurants based on their
    # relevance to the query
    def searchRestaurants(self):
        scores = dict()
        url = "https://www.thesaurus.com/browse/" + self.query.replace(" ", "%20")
        parser = restaurant.Restaurant.loadParser(url)
        synonyms = [self.query.upper()]
        if parser is not None:
            ul = parser.find("ul", class_="css-1lc0dpe et6tpn80")
            if ul is not None:
                for word in ul.children:
                    synonyms.append(word.span.a.text)
        for rest in self.restaurants:
            for word in synonyms:
                    scores[rest] = scores.get(rest, 0) + rest.name.upper().count(word) + rest.description.upper().count(word)
        self.restaurants.sort(key=lambda rest:scores[rest])
        self.restaurants.reverse()

    # Change the dimensions if the size of the canvas has changed
    def sizeChanged(self):
        self.getDimensions()
    
    # Draws the header bar with search
    def drawSearch(self, canvas):
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
                self.margin + self.topHeight / 2, text="All Restaurants")

    # Draw the login buttons
    def drawLogin(self, canvas):
        # Draw the boxes for the login/logout and register/recommendations
        canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
            self.margin, self.width - self.margin,\
            self.margin + self.topHeight / 2 - self.margin/4, fill=self.backgroundColor)
        canvas.create_rectangle(self.width - self.margin - self.loginWidth,\
            self.margin + self.topHeight / 2 + self.margin/4, self.width - self.margin,\
            self.margin + self.topHeight, fill=self.backgroundColor)        

        if self.user is None:
            # Display the text for the login and sign up buttons
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight / 4 - self.margin / 8, text="Login")
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                text="Sign Up")
        else:
            # Display the text for the logout and recommendation buttons
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight / 4 - self.margin / 8,\
                text="Logout " + self.user.username)
            if len(self.recommendations) == 0:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="Recommendations")
            else:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="All Restaurants")

    # Draw all of the info to the canvas - background, restaurant, and header
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.app.height,\
            fill=self.backgroundColor)

        if len(self.recommendations) == 0:
            # Draw each restaurant card
            for i in range(len(self.restaurants)):
                restaurant = self.restaurants[i]
                restaurant.draw(canvas, i)
        else:
            # Draw the recommendations card
            for i in range(len(self.recommendations)):
                restaurant = self.recommendations[i]
                restaurant.draw(canvas, i)

        # Draw the header
        self.drawSearch(canvas)
        self.drawLogin(canvas)

if __name__ == "__main__":
    UserInterface(width=600, height=600)