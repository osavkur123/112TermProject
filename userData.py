# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

from bs4 import BeautifulSoup

# User object - has user name and dictionary of reviews mapping the
# restaurants' names to the user's review and rating
class User(object):
    def __init__(self, username, password, reviews):
        self.username = username
        self.password = password
        self.reviews = reviews
    
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

    def updateFile(self):
        header = '<?xml version="1.0" encoding = "UTF-8"?>\n<users>\n'
        otherUsers = ""
        footer = "</users>"
        # Reading all the existing data from the xml file
        with open("users.xml", "r") as database:
            data = BeautifulSoup(database, "xml")
            users = data.find_all("user")
            for user in users:
                if user["username"] != self.username:
                    reviews = user.find_all("review")
                    newUser = User(user["username"], user["password"], createReviewsDictionary(reviews))
                    otherUsers += newUser.convertToXmlString()
        # Write updated user profile to users.xml
        stringToWrite = header + self.convertToXmlString() + otherUsers + footer
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

# TODO: Create a button for Create a new account
# TODO: Hash passwords to store in the xml file
def login(username, password):
    if username is None or username == "":
        return None
    with open("users.xml", "r") as database:
        data = BeautifulSoup(database, "xml")
        user = data.find("user", username=username)
        # Username does not exist in database or password or username are wrong
        if user is None or user["password"] != password:
            return None
        revs = user.find_all("review")
        reviews = createReviewsDictionary(revs)
        return User(username, password, reviews)

if __name__ == "__main__":
    user = login("other", "potatoes")
    user.reviews["THE UNDERGROUND"] = {"rating": 5, "comment": "No Comment"}
    user.logout()