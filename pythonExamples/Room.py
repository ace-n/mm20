##Authored by Brendan Moriarty (github:Moriartyb)


class Room(object):
    ##
    # Passes in objects to be placed within the room.
    ##
    def __init__(self, furniture={}, doors={}):
        """
        Initializes a room object with the following attributes
        Keyword arguments:
        furniture -- a dictionary of furniture objects to be placed in the room
                   with a tuple key of coordinates for where it should be placed
        doors -- a dictionary of door objects with a tuple for placement coordinates
        """
        self.furniture = furniture  # key is a tuple coordinate(?), value is object to be placed in room.
        self.doors = doors

    def spawnObjects(self):
        """
        Spawns all objects that are currently in the furniture dictionary
        """
        for obj in self.furniture:
            Room.placeFurniture(self.furniture[obj], obj[0], obj[1])

    def placeFurniture(furn, x, y):
        """
        Adds the furniture object to the dictionary and places it at a given coordinate
        """
        if(furn not in furniture):
            furniture[(x,y)] = furn

        pass

    def randomizeFurnitureLocations():
        pass

    def removeFurniture(furn, x, y):
        pass
