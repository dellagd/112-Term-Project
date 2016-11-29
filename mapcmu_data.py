class Constants(object):
    class Building(object):
        def __init__(self):
            self.floors = []

        def getFloor(self, i):
            return self.floors[i-1]

    def __init__(self):
        pass
        
    buildings = {"GHC" : Building()}
    buildings["GHC"].floors.extend(["Gates-1.jpg", "Gates-2.jpg"])
