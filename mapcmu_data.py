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

    # Colors #
    backGray = (0xC5,0xC1,0xC0)
    denim = (0x1A,0x29,0x30)
    steel = (0x0A,0x16,0x12)
    marigold = (0xF7,0xCE,0x3E)
    backdrop = backGray
    titleText = steel

    # Help #
    footerHelp = "ESC: Back to Previous Screen | H: Toggle Help | Ctrl-C: Exit"
    helpForwardRouting = '''ARROWS: Pan around map (+ SHIFT for fine control)
PAGE UP: Move up a floor
PAGE DOWN: Move down a floor
'''
    helpRoutePlanning = '''ARROWS: Pan around map (+ SHIFT for fine control)
PAGE UP: Move up a floor
PAGE DOWN: Move down a floor

Click map to begin placing route nodes. Nodes are indicated
as blue dots, purple when existing nodes are selected.

Clicking in an open area places a new node at that location,
and clicking a new location from there places a new node linked
to the prior node. Press SPACE to break link for next press,
so the next node will NOT be linked to the prior node. Click
on an existing node to begin placing a path from that node,
or to connect the current path to that node. Hold CTRL
when clicking to create a NAMED SEGMENT that will be an
eligable destination. NAMED SEGMENTs should not continue
on to more nodes after being placed, that is, they should
be a terminus on the linked node map.
'''

    helpAPMap = '''ARROWS: Pan around map (+ SHIFT for fine control)
PAGE UP: Move up a floor
PAGE DOWN: Move down a floor
P: Toggle localization using recorded data (location shown as triangle)

Move the red cursor by using the ARROWS and PAGE UP/DOWN
to your physical location on the map. Then press R to
begin recording Signal Strength information, linking that
data to your physical location that was selected. Collect
at least five samples per location (indicated after 'RECORDING'
on screen). Press R again to halp recording. Physically
move to a new location, updating the cursor to match, and then
record data for that location. Using this process, fully map
the area in which you wish to localize. If you record invalid
data for a location, click on that green node and click
SHIFT + NUMPAD X where X is the sample number, indicated in the
top right, that you wish to remove.
'''
