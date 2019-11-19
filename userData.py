# Name: Omkar Savkur
# AndrewID: osavkur
# 112 Term Project

class User(object):
    def __init__(self, username, data):
        self.username = username
        self.data = data

def login(username):
    if username is None or username == "":
        return None
    return User(username, {})

def logout():
    return None