# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

from bs4 import BeautifulSoup

class User(object):
    def __init__(self, username, reviews, data):
        self.username = username
        self.reviews = reviews
        self.data = data

def login(username):
    if username is None or username == "":
        return None
    with open("users.xml", "r") as database:
        data = BeautifulSoup(database, "xml")
        user = data.find("user", username=username)
        if user is None:
            # Username does not exist in database
            return User(username, {}, database.read())
        revs = user.find_all("review")
        reviews = dict()
        for review in revs:
            restaurant = review["restaurant"]
            reviews[restaurant] = {"rating": review.rating.contents[0], "comment": review.comment.contents[0]}
        return User(username, reviews, database.read())


# Takes in user object and writes the updated profile into users.xml 
def logout(user):
    # Write updated user profile to users.xml
    return None

if __name__ == "__main__":
    user = login("testUser")
    print(user.reviews)