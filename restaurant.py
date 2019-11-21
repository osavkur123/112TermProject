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
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        # TODO: Get menu and sepecials

    # Representing the objects as strings
    def __repr__(self):
        return f"\n{self.name}\t{self.description}"

    # Removing most whitespace from a list/string L
    def process(self, L):
        return [x for x in L if x!='\n' and x!="\t" and x!='\r']
    
    def calculateCoordinates(self, number):
        # Finding the row/col
        row = 0
        col = number
        while col >= self.app.cols:
            row += 1
            col -= self.app.cols
        
        # Calculating the bounds of the cell
        self.x0 = (self.app.margin + self.app.cellWidth) * col + self.app.margin
        self.y0 = (self.app.margin + self.app.cellHeight) * row + self.app.margin * 3\
            - self.app.scrollY + self.app.topHeight
        self.x1 = self.x0 + self.app.cellWidth
        self.y1 = self.y0 + self.app.cellHeight

    # Draws a rectangle for the restaurant
    def draw(self, canvas, number):
        self.calculateCoordinates(number)
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1)

        # Displaying the name as two lines if it's too long
        if len(self.name) > 24:
            words = self.name.split(" ")
            mid = len(words) // 2
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2-7, text=" ".join(words[:mid]))
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2+7, text=" ".join(words[mid:]))
        else:
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2, text=self.name)