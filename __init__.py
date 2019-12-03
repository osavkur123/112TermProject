# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

# The main file, __init__.py
# Runs the user interface and handles the recommendation and search algorithms
# Calls fuctions from userData.py to log users in and out
# Uses classes from restaurant.py to store all the information scraped from the internet

# TODO: scrollbar?

# CITATION - using CMU's 15-112 graphics library to help with drawing to the canvas
# From course notes: http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *

# CITATION - using tkinter as the graphics framework
# Url: https://github.com/python/cpython/tree/3.8/Lib/tkinter
from tkinter import *

# CITATION - using PIL's ImageTk class to display images on the canvas 
# and PIL's ImageEnhance class to reduce the brightness of images
# From https://pillow.readthedocs.io/en/3.1.x/index.html
from PIL import Image, ImageTk, ImageEnhance

# CITATION - using BeautifulSoup to parse webpages
# From https://pypi.org/project/beautifulsoup4/
from bs4 import BeautifulSoup

# CITATION - using requests to load webpages
# From https://pypi.org/project/requests/
import requests

# CITATION - using textblob to perform sentiment analysis
# on the reviews' comments to enhance the recommendation algorithm
# From https://textblob.readthedocs.io/en/dev/
import textblob

# Using python's builtin math library
import math

# Using python's statistics library
import statistics

# importing other files in same directory
import restaurant
import userData

# class that controls the user inteface
# switches between animations
class CMUFoodie(ModalApp):
    def appStarted(self):
        self.mainScreen = HomeScreen()
        self.newUserScreen = UserCreationScreen()
        self.setActiveMode(self.mainScreen)

# Animation that displays the restaurant information
# and allows users to rate restaurants
class RestaurantScreen(Mode):
    def __init__(self, mainApp, rest):
        super().__init__()
        self.restaurant = rest
        self.mainApp = mainApp
        if self.mainApp.user is not None:
            if self.mainApp.otherUsers == []:
                self.mainApp.otherUsers = self.mainApp.user.getOtherUsers()
            if self.restaurant.name in self.mainApp.user.reviews:
                self.rating = str(self.mainApp.user.reviews[self.restaurant.name]["rating"])
                self.comment = self.mainApp.user.reviews[self.restaurant.name]["comment"]
            else:
                self.rating = self.comment = ""
        else:
            self.rating = self.comment = ""
    
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
                self.rating.isdigit() and 1 <= int(self.rating) <= 10 and self.comment != "" and self.comment is not None:
                self.mainApp.user.reviews[self.restaurant.name] = {
                    "rating": int(self.rating), "comment": self.comment}
                self.mainApp.user.updateFile()
    
    # Change the location of the buttons based on the size of the canvas
    def sizeChanged(self):
        self.getDimensions()

    # Puts spaces so that all the ratings and comments line up
    # Takes in list of users and outputs formatted string
    def evenlySpaceRatings(self, toDisplayLst):
        lst = [[user.username + ":", "Rating: " + str(user.reviews[self.restaurant.name]["rating"]), "Comment: " + user.reviews[self.restaurant.name]["comment"]] for user in toDisplayLst]
        maxSpace = 0
        for user in lst:
            maxSpace = max(maxSpace, len(user[0]), len(user[1]))
        maxSpace += 5
        maxSpace = 4 * ((3 + maxSpace) // 4)
        output = ""
        for i in range(len(lst)):
            user = lst[i]
            space1 = maxSpace - len(user[0])
            space2 = maxSpace - len(user[1])
            userStr = user[0] + " " * space1 + "\t" + user[1] + " " * space2 + "\t" + user[2]
            output = output + userStr
            if i != len(lst) - 1:
                output = output + "\n"
        return output

    # Gets what other users rated this restaurant
    # Draws this feedback above the rating buttons
    def drawOtherUsersRatings(self, canvas):
        otherUsers = sorted(self.mainApp.otherUsers, key=lambda user: user.username.lower(), reverse=True)
        toDisplayLst = []
        i = 0
        while len(toDisplayLst) < 5:
            if i >= len(otherUsers): break
            if self.restaurant.name in otherUsers[i].reviews:
                toDisplayLst.append(otherUsers[i])
            i += 1
        toDisplayLst.sort(key=lambda user:user.username)
        toDisplayStr = self.evenlySpaceRatings(toDisplayLst)
        canvas.create_text(self.width/2, self.height*5/8, text=toDisplayStr, font="Times 12", fill="white")
   
    # Draw the buttons and the restaurant name and description
    def redrawAll(self, canvas):
        img = self.restaurant.image
        imgWidth, imgHeight = img.size
        scale = max(self.width/imgWidth, self.height/imgHeight)
        img = img.resize((int(imgWidth * scale), int(imgHeight * scale)))
        img = ImageEnhance.Brightness(img).enhance(0.5)
        canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(img))
        canvas.create_rectangle(*self.exitButton, outline="white")
        canvas.create_text((self.exitButton[0]+self.exitButton[2])/2,\
            (self.exitButton[1]+self.exitButton[3])/2, text="EXIT", font="Times", fill="white")
        canvas.create_text(self.width/2, self.app.height/4,\
            text=self.restaurant.name, font="Times", fill="white")
        canvas.create_text(self.width/2, self.app.height/2,\
            text=self.restaurant.description, font="Times 10", fill="white")
        if self.mainApp.user is not None:
            canvas.create_text(self.width/2, self.app.height/10,\
                text="Welcome " + self.mainApp.user.username, font="Times", fill="white")
            self.drawOtherUsersRatings(canvas)
            canvas.create_rectangle(*self.ratingButton, outline="white")
            if self.rating == "" or self.rating is None:
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text="RATE", font="Times", fill="white")
            elif not self.rating.isdigit():
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text="PLEASE ENTER A NUMBER", font="Times", fill="white")
            elif not 1 <= int(self.rating) <= 10:
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text="PLEASE ENTER A NUMBER BETWEEN 1 AND 10", font="Times", fill="white")
            else:
                canvas.create_text((self.ratingButton[0]+self.ratingButton[2])/2,\
                    (self.ratingButton[1]+self.ratingButton[3])/2, text=f"RATING: {self.rating}", font="Times", fill="white")
            canvas.create_rectangle(*self.commentButton, outline="white")
            if self.comment == "" or self.comment is None:
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2,\
                    (self.commentButton[1]+self.commentButton[3])/2, text="COMMENT", font="Times", fill="white")
            else:
                canvas.create_text((self.commentButton[0]+self.commentButton[2])/2,\
                    (self.commentButton[1]+self.commentButton[3])/2, text=f"COMMENT: {self.comment}", font="Times", fill="white")
        else:
            canvas.create_text(self.width/2, self.app.height/10,\
                text=f"Sign In to see ratings and rate {self.restaurant.name}", font="Times", fill="white")

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
            if self.username is not None and self.username != "" and \
                self.pass1 == self.pass2 and self.pass1 != "" and self.pass1 is not None:
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
        canvas.create_text((box[0]+box[2])/2, (box[1]+box[3])/2, text=text, font="Times")

    # Display the boxes and text for the user
    def redrawAll(self, canvas):
        canvas.create_rectangle(*self.usernameBox)
        if self.username is None or self.username == "":
            UserCreationScreen.drawTextWithinBox("Enter Username", self.usernameBox, canvas)
        else:
            UserCreationScreen.drawTextWithinBox(self.username, self.usernameBox, canvas)
        canvas.create_rectangle(*self.pass1Box)
        if self.pass1 is None or self.pass1 == "":
            UserCreationScreen.drawTextWithinBox("Enter Password", self.pass1Box, canvas)
        else:
            UserCreationScreen.drawTextWithinBox("*" * len(self.pass1), self.pass1Box, canvas)
        canvas.create_rectangle(*self.pass2Box)
        if self.pass2 is None or self.pass2 == "":
            UserCreationScreen.drawTextWithinBox("Confirm Password", self.pass2Box, canvas)
        else:
            UserCreationScreen.drawTextWithinBox("*" * len(self.pass2), self.pass2Box, canvas)
        canvas.create_rectangle(*self.cancelBox)
        UserCreationScreen.drawTextWithinBox("Cancel", self.cancelBox, canvas)
        canvas.create_rectangle(*self.submitBox)
        UserCreationScreen.drawTextWithinBox("Submit", self.submitBox, canvas)

# class that displays the main screen
class HomeScreen(Mode):
    def appStarted(self):
        self.getRestaurantInfo()
        self.scrollY = 0
        self.backgroundColor = "light cyan"
        self.user = None
        self.otherUsers = []
        self.query = None
        self.location = None
        self.resetSearchAndRecommendations()
        self.getDimensions()
        # CITATION: using image from https://i.pinimg.com/originals/cf/d3/2e/cfd32ecb5df69b18dad171345dd8c18a.jpg as background
        imgContent = requests.get("https://i.pinimg.com/originals/cf/d3/2e/cfd32ecb5df69b18dad171345dd8c18a.jpg").content
        self.backgroundImg = Image.open(BytesIO(imgContent))
    
    def getRestaurantInfo(self):
        # Get the webpage with the info of all of the CMU Restaurants
        url = "https://apps.studentaffairs.cmu.edu/dining/conceptinfo/?page=listConcepts"
        parser = restaurant.Restaurant.loadParser(url)
        if parser is None:# If bad request or something failed, load from cached file
            with open("cmuCache.html", "r") as f:
                parser = BeautifulSoup(f, "html.parser")
        else:# Write to cached file results
            with open("cmuCache.html", "w") as f:
                # CITATION: Saving CMU dining information in case
                # the website can't be loaded in the future
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
        if len(self.recommendations) == 0 and len(self.searchResults) == 0:
            self.rows = math.ceil(len(self.restaurants) / self.cols)
        elif len(self.recommendations) == 0:
            self.rows = math.ceil(len(self.searchResults) / self.cols)
        else:
            self.rows = math.ceil(len(self.recommendations) / self.cols)
        self.cellWidth = (self.width - self.margin * (self.cols + 1)) // self.cols
        self.cellHeight = self.cellWidth
        self.maxScrollY = max(0, self.rows * (self.cellHeight + self.margin) +\
            self.margin * 3 + self.topHeight - self.app.height)
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
            self.topHeight > self.height + self.maxScrollY:
            self.getDimensions()

    # Resets all values back to default (empty)
    def resetSearchAndRecommendations(self):
        self.distances = dict()
        self.searchResults = []
        self.recommendations = []
        self.matches = dict()

    # Handles searching, login, registration, logout, and recommendation
    def mousePressed(self, event):
        if 0 <= event.x - self.margin <= self.searchBarWidth and\
            0 <= event.y - self.margin <= self.topHeight:
            if len(self.recommendations) == 0 and len(self.searchResults) == 0:
                self.query = self.getUserInput("What do you want to eat?")
                self.searchRestaurants()
            elif len(self.searchResults) == 0:
                self.location = self.getUserInput("What is your address?")
                self.sortRestaurantsByDistance(self.recommendations)
            else:
                self.location = self.getUserInput("What is your address?")
                self.sortRestaurantsByDistance(self.searchResults)
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
                    if len(self.searchResults) == 0 and len(self.recommendations) == 0:
                        # New User Screen
                        self.app.setActiveMode(self.app.newUserScreen)
                    else:
                        # Get all the restaurants
                        self.resetSearchAndRecommendations()
                        self.getDimensions()
            else:
                if self.margin <= event.y <= self.margin + self.topHeight / 2 - self.margin/4:
                    # Logout
                    self.user = self.user.logout()
                    self.resetSearchAndRecommendations()
                elif self.margin + self.topHeight / 2 + self.margin / 4 <= event.y <=\
                    self.margin + self.topHeight:
                    if len(self.recommendations) == 0 and len(self.searchResults) == 0:
                        # call the recommendation function
                        self.resetSearchAndRecommendations()
                        self.getRecommendations()
                    else:
                        # Get all restaurants
                        self.resetSearchAndRecommendations()
                        self.getDimensions()
        elif event.y > self.topHeight + self.margin * 2:
            self.findClickedRestaurant(event)

    # Finds which restaurant has been clicked and
    # opens that restaurant's info/review page
    def findClickedRestaurant(self, event):
        if len(self.recommendations) == 0 and len(self.searchResults) == 0:
            for rest in self.restaurants:
                if rest.x0 <= event.x <= rest.x1 and\
                    rest.y0 <= event.y <= rest.y1:
                    self.app.setActiveMode(RestaurantScreen(self, rest))
                    break
        elif len(self.recommendations) == 0:
            for rest in self.searchResults:
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
        if self.otherUsers == []:
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
        self.matches = dict()
        for recommendation in self.recommendations:
            self.matches[recommendation] = self.getMatchPercentage(recommendation, neighbors, distances)
        self.recommendations.sort(key=lambda rest: self.matches[rest], reverse=True)
        self.getDimensions()

    # Calculates the "distance" between the current user and the other user
    # Distance is based on the similarities of the ratings between users and
    # the sentiment polarity of the comment (positive is +1, negative is -1)
    # If the users both have the same rating, they get a 0 for that restaurant
    # If only one user rated a restaurant, then the other users' score is a 5 by default
    # If neither user rated a restaurant, then the default is 7
    def getDistance(self, otherUser):
        distanceSquared = 0
        for restaurant in self.restaurants:
            if restaurant.name in self.user.reviews:
                userSentiment = textblob.TextBlob(self.user.reviews[restaurant.name]["comment"]).sentiment.polarity
                if restaurant.name in otherUser.reviews:
                    otherUserSentiment = textblob.TextBlob(otherUser.reviews[restaurant.name]["comment"]).sentiment.polarity
                    distanceSquared += (otherUser.reviews[restaurant.name]["rating"] - self.user.reviews[restaurant.name]["rating"]) ** 2
                    distanceSquared += 50 * (userSentiment - otherUserSentiment) ** 2
                else:
                    distanceSquared += (5 - self.user.reviews[restaurant.name]["rating"]) ** 2
                    distanceSquared += 50 * userSentiment ** 2
            elif restaurant.name in otherUser.reviews:
                otherUserSentiment = textblob.TextBlob(otherUser.reviews[restaurant.name]["comment"]).sentiment.polarity
                distanceSquared += (otherUser.reviews[restaurant.name]["rating"] - 5) ** 2
                distanceSquared += 50 * otherUserSentiment ** 2
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

    # Finds how similar the recommendation is to the user based on the neighbors
    # Finds the average percent difference between the neighbors and the max distance
    # and weights that with the z-score of the rating the neighbors gave the restaurant 
    def getMatchPercentage(self, recommendation, neighbors, distances):
        maxDistance = max(distances.values())
        similarity = []
        neighborRatings = []
        for neighbor in neighbors:
            distance = distances[neighbor]
            similarity.append(1 - distance / maxDistance)
            if recommendation.name in neighbor.reviews:
                neighborRatings.append(neighbor.reviews[recommendation.name]["rating"])
        allRatings = []
        for user in self.otherUsers:
            if recommendation.name in user.reviews:
                allRatings.append(user.reviews[recommendation.name]["rating"])
        zScore = (statistics.mean(neighborRatings) - statistics.mean(allRatings)) / statistics.pstdev(allRatings)
        if len(similarity) == 0:
            return 50
        else:
            return min(95, 100 * statistics.mean(similarity) + 50 * zScore)

    # Search function that orders the restaurants based on their
    # relevance to the query - creates a new list self.searchResults
    def searchRestaurants(self):
        if self.query == "" or self.query == None:
            return
        scores = dict()
        url = "https://www.thesaurus.com/browse/" + self.query.replace(" ", "%20")
        parser = restaurant.Restaurant.loadParser(url)
        synonyms = [self.query.upper()]
        if parser is not None:
            ul = parser.find("ul", class_="css-1lc0dpe et6tpn80")
            if ul is not None:
                for word in ul.children:
                    synonyms.append(word.span.contents[0].text.upper())
        for rest in self.restaurants:
            for word in synonyms:
                    scores[rest] = scores.get(rest, 0) + rest.name.upper().count(word) + rest.description.upper().count(word) + rest.specials.upper().count(word)
        self.searchResults = [rest for rest in scores.keys() if scores[rest] > 0]
        self.searchResults.sort(key=lambda rest:scores[rest], reverse=True)

    # Sorts the restaurant list by walking distance
    def sortRestaurantsByDistance(self, restLst):
        if self.location == "" or self.location is None:
            return
        if self.location.find("Pittsburgh") == -1:
            self.location = self.location + " Pittburgh"
        if self.location.find("PA") == -1:
            self.location = self.location + ", PA"
        self.location = self.location + " "
        self.location.replace(" ", "%20")
        apiKey = "Ai8o_qE0pCvSmu2Pz4PgXowMyetWm0J6B0Q_Q7yGJ-ZXQB1Hjc0pz6gXWYCcSk1R"
        self.distances = dict()
        for rest in restLst:
            restaurantLoc = str(rest.latitude) + "," + str(rest.longitude)
            # CITATION: using Bing Maps REST Services to determine
            # walking distances between the user's location and the restaurant
            url = f"http://dev.virtualearth.net/REST/v1/Routes/Walking?wayPoint.1={self.location}&waypoint.2={restaurantLoc}&key={apiKey}&output=xml"
            response = requests.get(url)
            if response.status_code == 200:
                xmlData = BeautifulSoup(response.text, "xml")
                # Convert miles into kilometers
                self.distances[rest] = float(xmlData.find("Route").TravelDistance.text) / 1.6
            else:
                # Assume about its a mile away
                self.distances[rest] = 1
        restLst.sort(key=lambda rest: self.distances[rest])

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
        if len(self.searchResults) == 0 and len(self.recommendations) == 0:
            canvas.create_text(self.margin + self.searchBarWidth / 2,\
                self.margin + self.topHeight / 2, text="Search", font="Times")
        else:
            canvas.create_text(self.margin + self.searchBarWidth / 2,\
                self.margin + self.topHeight / 2, text="Sort by walking distance", font="Times")

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
                self.margin + self.topHeight / 4 - self.margin / 8, text="Login", font="Times 12")
            if len(self.searchResults) == 0:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="Sign Up", font="Times 12")
            else:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="All Restaurants", font="Times 12")
        else:
            # Display the text for the logout and recommendation buttons
            canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                self.margin + self.topHeight / 4 - self.margin / 8,\
                text="Logout " + self.user.username, font="Times 12")
            if len(self.recommendations) == 0 and len(self.searchResults) == 0:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="Recommendations", font="Times 12")
            else:
                canvas.create_text(self.width - self.margin - self.loginWidth / 2,\
                    self.margin + self.topHeight * 3 / 4 + self.margin / 8,\
                    text="All Restaurants", font="Times 12")

    # Draws the distance a restaurant is
    def drawDistance(self, rest, canvas):
        if rest in self.distances:
            dist = self.distances[rest]
            canvas.create_text((rest.x0+rest.x1)/2,\
                rest.y0 + (rest.y1-rest.y0)*3/4,\
                text="Distance: %0.3f miles" % dist, font="Times 10")
    
    # Draws how confident a recommendation is
    def drawMatch(self, rest, canvas):
        if rest in self.matches:
            match = self.matches[rest]
            canvas.create_text((rest.x0+rest.x1)/2,\
                rest.y0 + (rest.y1-rest.y0)/4,\
                text=("%0.f%% Match" % match), font="Times 10")

    # Draw all of the info to the canvas - background, restaurant, and header
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill=self.backgroundColor)
        # img = self.backgroundImg
        # imgWidth, imgHeight = img.size
        # scale = max(self.width/imgWidth, self.height/imgHeight)
        # img = img.resize((int(imgWidth * scale), int(imgHeight * scale)))
        # canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(img))

        if len(self.recommendations) == 0 and len(self.searchResults) == 0:
            # Draw each restaurant card
            for i in range(len(self.restaurants)):
                restaurant = self.restaurants[i]
                restaurant.draw(canvas, i)
        elif len(self.recommendations) == 0:
            # Draw each search result card
            for i in range(len(self.searchResults)):
                restaurant = self.searchResults[i]
                restaurant.draw(canvas, i)
                self.drawDistance(restaurant, canvas)
        else:
            # Draw the recommendations card
            for i in range(len(self.recommendations)):
                restaurant = self.recommendations[i]
                restaurant.draw(canvas, i)
                self.drawDistance(restaurant, canvas)
                self.drawMatch(restaurant, canvas)

        # Draw the header
        self.drawSearch(canvas)
        self.drawLogin(canvas)

if __name__ == "__main__":
    CMUFoodie(width=600, height=600)