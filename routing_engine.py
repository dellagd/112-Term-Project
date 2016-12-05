import mongodb_databases
from mapcmu_data import *

class RoutingEngine(object):
    def __init__(self):
        self.db = mongodb_databases.MDBDatabase(Constants.database)
        self.segTable = mongodb_databases.SegmentTable(self.db.database)
        #self.segTable.nukeTable()

    def testTable(self):
        self.segTable.addSegment([10,10,0,"GHC"], [10,100,0,"GHC"])
        self.segTable.addSegment([10,100,0,"GHC"], [100,100,0,"GHC"])
        self.segTable.addSegment([10,10,0,"GHC"], [100,10,0,"GHC"])
        self.segTable.addSegment([100,10,0,"GHC"], [200,10,0,"GHC"])
        self.segTable.addSegment([200,10,0,"GHC"], [100,100,0,"GHC"])
        self.segTable.addSegment([200,10,0,"GHC"], [100,150,0,"GHC"])
        self.segTable.addSegment([100,100,0,"GHC"], [100,150,0,"GHC"]) 
        self.segTable.addSegment([200,10,0,"GHC"], [200,220,0,"GHC"])
        self.segTable.addSegment([100,150,0,"GHC"], [200,220,0,"GHC"])
        

    def getRoomNode(self, room):
        return  self.segTable.collection.find(
                {"NOTE" : room})[0]["LOC_A"]


    def getAllSegments(self, onFloor=None):
        if onFloor == None:
            return self.segTable.collection.find()
        else:
            floorSegList = []
            floorZ = (onFloor-1) * Constants.floorHeight
            segments = self.segTable.collection.find()
            for seg in segments:
                if seg["LOC_A"][2] == floorZ and seg["LOC_B"][2] == floorZ:
                    floorSegList.append(seg)

            return floorSegList

    def getAllNodes(self, onFloor=None):
        locs = set()

        for row in self.getAllSegments(onFloor):
            locs.add(tuple(row["LOC_A"]))
            locs.add(tuple(row["LOC_B"]))

        locsLists = list(map(lambda x: list(x), locs))

        return locsLists

    def getAllConnections(self, node):
        node = list(node)
        
        q = { '$or' : [{"LOC_A" : node}, {"LOC_B" : node}]}
        res = self.segTable.collection.find(q)

        neighbors = []
        for row in res:
            if row["LOC_A"] == node:
                neighbors.append(RoutingEngine.AStarNode(row["LOC_B"],node))
            elif row["LOC_B"] == node:
                neighbors.append(RoutingEngine.AStarNode(row["LOC_A"],node))

        return neighbors

    class AStarNode(object):
        def __init__(self, nodeInfo, parent):
            self.info = nodeInfo
            self.parent = parent

        def __eq__(self, other):
            if isinstance(other, type(self)):
                return self.info == other.info
            elif isinstance(other, list):
                return other == self.info

        def __repr__(self):
            return repr(self.info)

        def euclDist(self,a,b):
            if isinstance(a, type(self)): ai = a.info
            else: ai = a
            if isinstance(b, type(self)): bi = b.info
            else: bi = b

            return ((ai[0] - bi[0])**2 + \
                    (ai[1] - bi[1])**2 + \
                    (ai[2] - bi[2])**2)**0.5
            

        def calcHCost(self,testNode,dst):
            # Just euclidian dist from current to end
            return self.euclDist(testNode, dst)

        def calcGCost(self,testNode):
            # Recursively calulate distance to origin through nodes
            # Euclidian distance between nodes (that's how the map's set up)
            if not isinstance(testNode.parent, type(self)):
                return 0

            return self.euclDist(testNode, testNode.parent) + \
                    self.calcGCost(testNode.parent)

        def calcFCost(self, testNode, dst):
            return self.calcHCost(testNode, dst) + \
                    self.calcGCost(testNode)
    
    def findRoute(self, origin, dst):
        nodes = self.getAllNodes()
       
        if origin not in nodes or dst not in nodes:
            return None

        openNodes = list()
        openNodes.append(RoutingEngine.AStarNode(origin, None))

        closedNodes = list()

        while(True):
            #print("Open: %r" % openNodes)
            #print("Closed: %r" % closedNodes)

            currentNode = self.findLowestFCost(openNodes,dst)
            if currentNode == None: 
                # Found No Path!
                return None
            
            openNodes.remove(currentNode)
            closedNodes.append(currentNode)
            
            if dst == currentNode:
                return self.retracePath(currentNode)

            for neighbor in self.getAllConnections(currentNode.info):
                if neighbor in closedNodes: continue

                if (neighbor not in openNodes or
                        (self.pathFromThru(neighbor, currentNode) < 
                        neighbor.calcGCost(neighbor))):
                    
                    neighbor.parent = currentNode # Setting new, better H cost
                    if neighbor not in openNodes:
                        openNodes.append(neighbor)


    def retracePath(self, node):
        if node == None:
            return []

        return self.retracePath(node.parent) + [node]

    def pathFromThru(self, startNode, thruNode): 
        segA = startNode.euclDist(startNode, thruNode)
        return segA + thruNode.calcGCost(thruNode)
        
    def findLowestFCost(self, nodes, dst):
        bestNode = None
        bestCost = 10e42
        for node in nodes:
            fCost = node.calcFCost(node, dst)

            if fCost < bestCost:
                bestCost = fCost
                bestNode = node

        return bestNode




