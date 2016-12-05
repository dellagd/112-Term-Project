class Constants(object):
    class Building(object):
        def __init__(self, minh, maxh):
            self.floors = []
            self.minFloor = minh
            self.maxFloor = maxh

        def getFloor(self, i):
            return self.floors[i-1]

    def __init__(self):
        pass
        
    buildings = {"GHC" : Building(1,9)}
    buildings["GHC"].floors.extend(["Gates-1.jpg", "Gates-2.jpg",
        "Gates-3.jpg", "Gates-4.jpg", "Gates-5.jpg",
        "Gates-6.jpg", "Gates-7.jpg", "Gates-8.jpg",
        "Gates-9.jpg"])
    floorHeight = 600

    database = "MapCMU"
