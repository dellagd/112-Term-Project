##########################################################################
# Author: Griffin Della Grotte (gdellagr@andrew.cmu.edu)
#
# This module wraps MongoDB into a nice interface for both the MapTable
# and SegmentTable, which hold the data for the AP data map and the
# routable paths map, respectively.
##########################################################################

from pymongo import MongoClient
import time

class MDBDatabase(object):
    def __init__(self, name):
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[name]

class MDBTable(object):
    # Superclass for a table object
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
        return self.collection.find(row)[0]["_id"]

class MapTable(MDBTable):
    # Table for storing data for the AP map
    def __init__(self, db):
        super().__init__("APMap", db)

    def addAP(self, loc, bssid, rssi, tS):
        toDict = {"Location" : loc, "BSSID" : bssid,
                "RSSI" : str(rssi), "TIME" : tS}
        self.insertRow(toDict)

    def getAPsAtLoc(self, loc):
        res = list(self.findRowsWhere({"Location" : loc},
                fields=['Location', 'BSSID', 'RSSI', 'TIME']))
        
        for x in res:
            x.pop("_id")
        
        return res

    def getAPsAtLocWithBSSID(self, loc, bssid):
        res = list(self.findRowsWhere({"Location" : loc, "BSSID" : bssid},
                fields=['Location', 'BSSID', 'RSSI', 'TIME']))
        
        for x in res:
            x.pop("_id")

        return res

class SegmentTable(MDBTable):
    # Table for storing data for routable paths
    def __init__(self, db):
        super().__init__("NodeMap", db)

    def addSegment(self, locA, locB, notes=""):
        toDict = {"LOC_A" : locA, "LOC_B" : locB, "NOTE" : notes}
        return self.insertRow(toDict)

