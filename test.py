import mongodb_databases
from routing_engine import *

db = mongodb_databases.MDBDatabase("MapCMU")
mapTable = mongodb_databases.MapTable(db.database)

for row in mapTable.collection.find():
    _id = row["_id"]
    loc = row["Location"]
    print(loc)
    loc = loc[:-1] + ", 600)"
    print(loc)

    #mapTable.collection.update({"_id":_id},{"$set": {"Location":loc}})
