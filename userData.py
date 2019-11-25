# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

# userData.py - has helper functions and classes for the main file to use
# Stores user information in users.xml and parses the file with Beautiful Soup

# CITATION - using BeautifulSoup to parse webpages
# From https://pypi.org/project/beautifulsoup4/
from bs4 import BeautifulSoup

# User object - has user name and dictionary of reviews mapping the
# restaurants' names a dictionary contataining the user's review and rating
class User(object):
    def __init__(self, username, password, reviews):
        self.username = username
        self.password = password
        self.reviews = reviews
    
    # Hashing based on username and password
    def __hash__(self):
        return passwordHash(self.username) + int(self.password)

    # Checking equality based on username
    def __eq__(self, other):
        return isinstance(other, User) and self.username == other.username

    # Print username
    def __repr__(self):
        return self.username

    # Taking the username and reviews and converting it back into 
    # xml to be written to the users.xml file
    def convertToXmlString(self):
        first = f"<user username=\"{self.username}\" password=\"{self.password}\">\n"
        last = "</user>\n"
        middle = ""
        for restaurant in self.reviews:
            middle += (f'\t<review restaurant=\"{restaurant}\">\n' + 
                f'\t\t<rating>{self.reviews[restaurant]["rating"]}</rating>\n' + 
                f'\t\t<comment>{self.reviews[restaurant]["comment"]}</comment>\n' + 
                f'\t</review>\n')
        return first + middle + last

    # Creates list of all the other users in file besides the current users
    def getOtherUsers(self):
        otherUsers = []
        # Reading all the existing data from the xml file
        with open("users.xml", "r") as database:
            data = BeautifulSoup(database, "xml")
            users = data.find_all("user")
            for user in users:
                if user["username"] != self.username:
                    reviews = user.find_all("review")
                    otherUsers.append(User(user["username"], user["password"], createReviewsDictionary(reviews)))
        return otherUsers        

    # Overwrites users.xml to save information beyond running the project once
    def updateFile(self):
        header = '<?xml version="1.0" encoding = "UTF-8"?>\n<users>\n'
        otherUsers = self.getOtherUsers()
        otherUsersStr = ""
        footer = "</users>"
        for user in otherUsers:
            otherUsersStr += user.convertToXmlString()
        # Write updated user profile to users.xml
        stringToWrite = header + self.convertToXmlString() + otherUsersStr + footer
        database = open("users.xml", "w")
        database.write(stringToWrite)

    # Takes in user object and writes the updated profile into users.xml 
    def logout(self):
        self.updateFile()
        return None

# Takes in a Beautiful Soup object with the list of the review xml tags
# Returns a dictionary mapping the restaurant name to the user's rating and comment
def createReviewsDictionary(revs):
    reviews = dict()
    for review in revs:
        restaurant = review["restaurant"]
        reviews[restaurant] = {"rating": int(review.rating.contents[0]), "comment": review.comment.contents[0]}
    return reviews

# login function - if the username and hashed password are in users.xml,
# it creates a User object - otherwise, returns None
def login(username, password):
    if username is None or username == "" or password is None or password == "":
        return None
    with open("users.xml", "r") as database:
        data = BeautifulSoup(database, "xml")
        user = data.find("user", username=username)
        # Username does not exist in database or password or username are wrong
        if user is None or int(user["password"]) != password:
            return None
        revs = user.find_all("review")
        reviews = createReviewsDictionary(revs)
        return User(username, password, reviews)

# Function that hashes passwords - can't use python's builtin hash function 
# because the salt for that changes each the program runs
# CITATION: modified from Daniel J. Bernstein's hash funcion
# Source: https://en.wikipedia.org/wiki/Universal_hashing#Hashing_strings
def passwordHash(password):
    if password is None:
        return 0
    hashVal = 11087
    multiplier = 151
    largePrime = 123456794327
    for i in range(len(password)):
        hashVal = (hashVal * multiplier + i + ord(password[i])) % largePrime
    return hashVal

if __name__ == "__main__":
    # Importing python's builtin acscii letters
    from string import ascii_letters as l
    # Populating xml file with more users to test KNN
    # Importing python's random module to get ratings
    import random

    with open("restaurants.txt", "r") as f:
        restaurants = f.readlines()
    restaurants = [rest[:-1] for rest in restaurants]
    hashes = {}
    for a in l:
        for b in l:
            for c in l:
                # Testing hash collisions
                s = a+b+c
                x = passwordHash(s)
                if x in hashes:
                    print("Collision", s, hashes[x])
                else:
                    hashes[x] = s
                
                # Creating users - apparently runs for way too long
                for d in l:
                    name = a+b+c+d
                    pwrd = passwordHash("password123")
                    user = User(name, pwrd, {})
                    random.shuffle(restaurants)
                    for rest in restaurants[:random.randint(10,len(restaurants)-2)]:
                        user.reviews[rest] = {"rating": random.randint(1,10), "comment":"Random"}
                    user.updateFile()
