from routing_engine import *

router = RoutingEngine()

locA = "3800"
locB = "4800"

pointA = router.segTable.collection.find({"NOTE":locA})[0]["LOC_A"]
pointB = router.segTable.collection.find({"NOTE":locB})[0]["LOC_A"]

router.segTable.collection.insert({"LOC_A":pointA,"LOC_B":pointB,"NOTE":""})
