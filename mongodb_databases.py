from pymongo import MongoClient
import time

class MDBDatabase(object):
    def __init__(self, name):
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[name]

class MDBTable(object):
    def __init__(self, name, db):
        self.collection = db[name]

    def nukeTable(self):
        self.collection.delete_many({})

    def getAllRows(self):
        return list(self.collection.find())

    def findRowsWhere(self, cases=None, fields=None):
        return self.collection.find(cases, fields)

    def insertRow(self, row):
        self.collection.insert_one(row)

class MapTable(MDBTable):
    def __init__(self, db):
        super().__init__("APMap", db)

    def addAP(self, loc, bssid, rssi):
        toDict = {"Location" : loc, "BSSID" : bssid, "RSSI" : str(rssi)}
        self.insertRow(toDict)

    def getAPsAtLoc(self, loc):
        res = list(self.findRowsWhere({"Location" : loc},
                fields=['Location', 'BSSID', 'RSSI']))
        
        for x in res:
            x.pop("_id")
        
        return res

    def getAPsAtLocWithBSSID(self, loc, bssid):
        res = list(self.findRowsWhere({"Location" : loc, "BSSID" : bssid},
                fields=['Location', 'BSSID', 'RSSI']))
        
        for x in res:
            x.pop("_id")

        return res

