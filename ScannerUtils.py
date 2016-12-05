from subprocess import check_output, call
import os
import copy
import time
import threading

class APScanner(threading.Thread):
    def __init__(self, lp=False, trigFunc=None):
        threading.Thread.__init__(self)
        self.foundAPs = []
        self.mapAPs = []
        self.loopPrint = lp
        self.trigFuncs = [trigFunc]
        self.__populateMap()
        self.kill = False
    
    def run(self):
        self.__mainloop()

    ############################
    # Map stuff
    ############################

    def __populateMap(self):
        import csv
        with open('compsvcmap.csv', 'rt') as f:
            reader = csv.reader(f)
            csvlist = list(reader)

        for line in csvlist:
            if line[1] == "g-HT":
                self.mapAPs.append(MapAP(line[2], line[0]))
    
    def __getLocFromBSSID(self, bssid):
        for i in range(len(self.mapAPs)):
            ap = self.mapAPs[i]
            if ap.bssid.lower() == bssid.lower():
                return self.mapAPs[i].loc

        return "Unknown AP"


    #############################
    # FoundAP stuff
    #############################

    def __rssiInt(self, rssiStr):
        return int(float(rssiStr.split()[0]))

    def __updateBSSIDWithRSSI(self, bssid, rssi, apList):
        for ap in apList:
            if ap.bssid == bssid:
                ap.updateRSSI(rssi)


    def __getAPFromBSSID(self, bssid, apList):
        for ap in apList:
            if bssid == ap.bssid:
                return ap

    def __sortAPList(self):
        self.foundAPs.sort(reverse=True, key=lambda ap: ap.rssi)
        self.foundAPs.sort(key=lambda ap: ap.age)

    def __repr__(self):
        print ("AGE\tSSID\t\tBSSID\t\t\tLOCATION\t\tRSSI\tFREQ")
        for ap in self.foundAPs:
            if ap.rssi < -70: continue
            print (str(ap.age) + "\t" + ap.ssid + ("\t" if len(ap.ssid) >= 8 else "\t\t") + \
                    ap.bssid + "\t" + self.__getLocFromBSSID(ap.bssid) + \
                    "\t\t" + str(ap.rssi) + "\t" + ap.freq)
   
    def getResultsList(self):
        resl = []
        for ap in self.foundAPs:
            if ap.rssi < -60: continue
            resl.append(
                    {"AGE":str(ap.age),
                    "SSID":ap.ssid,
                    "BSSID":ap.bssid,
                    "LOCATION":self.__getLocFromBSSID(ap.bssid),
                    "RSSI":str(ap.rssi),
                    "FREQ":str(ap.freq)}
                    )
        return resl

    ############################
    # Main loop
    ############################

    def __mainloop(self):
        devnull = open(os.devnull, 'w')
        while not self.kill:
            out = check_output(
                    "echo 'password' | sudo -kS iw dev wlan0 scan | gawk -f scan.awk",
                    shell=True, stderr=devnull)
            if (self.loopPrint): call(["clear"])
    
            out=out.decode()

            result=out.splitlines()
            header=result.pop(0)

            seenAPs = []
            for line in result:
                if len(line.strip()) < 1: continue

                items = line.split()
                seenAPs.append(FoundAP(items[0], items[1],
                    self.__rssiInt(items[3]), freq=items[2]))

            if len(seenAPs) >= 1:
                for ap in seenAPs:
                    if ap in self.foundAPs:
                        self.__updateBSSIDWithRSSI(ap.bssid, ap.rssi, self.foundAPs)
                    else:
                        self.foundAPs.append(ap)

                #for ap in self.foundAPs:
                #    if ap not in seenAPs:
                #        ap.ageTick()

                self.__sortAPList()    
                if (self.trigFuncs != None): 
                    for f in self.trigFuncs:
                        f(self.getResultsList())
            else:
                # Error in scan
                pass

            if (self.loopPrint): self.__repr__()

            time.sleep(0.01)

class FoundAP(object):
    def __init__(self, bssid, ssid, rssi, freq="None"):
        self.bssid = bssid
        self.rssi = rssi
        self.ssid = ssid
        self.freq = freq
        self.age = 0
        self.birth = time.time()
    
    def updateRSSI(self, rssi):
        self.rssi = rssi
        self.age = 0
        self.birth = time.time()

    def ageTick(self):
        self.age += 1

    def getAgeMS(self):
        return int(time.time()-birth)

    def __eq__(self, other):
        return (isinstance(other,type(self)) and
                self.bssid == other.bssid)

    def __repr__(self):
        return "[ " + self.bssid + ":" + str(self.rssi) + " ]"

class MapAP(object):
    def __init__(self, bssid, loc):
        self.bssid = bssid
        self.loc = loc

