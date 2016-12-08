# MapCMU

Project Overview
----------------
MapCMU is a software package that enables precise localization via Wireless Access Points and, using this technology, routing from the detected location to a new destination. The user operation of MapCMU takes place as follows: First, create a map of viable routes on a given floor using the Route Planning Mode (MapCMU comes pre-loaded with all floors of the Gates-Hillman Center). Also, walk all routable areas in which localization is desired, building a data-map of the wireless topology of the area, using the AP Mapping Mode. After these steps, routing from the current location can be performed in the Routing Mode using the route map and AP map that were previously generated.

Installation
------------
MapCMU requires somewhat low-level access to a computer's WiFi adapter in order to collect the requisite data. The drivers to facilitate this are very difficult to obtain in Windows, so I chose to build MapCMU in Linux, where such drivers are built-in. As such, MapCMU utilizes Linux-specific binaries (namely, iw) to operate. Note that MapCMU *should* 'operate' on a computer that does not support this, only all operations that rely on interaction with the WiFi adapter will not run/complete (e.g. routing will never begin, as a localization never finishes).

In addition to the aforementioned dependecy, MapCMU also requires **MongoDB** and **PyGame**. Follow the TA guide (https://docs.google.com/document/d/1-Nry4kxRC9d2VNEzIkSsZpN1Hov0-7_XThHxB1t0GxQ/edit?usp=sharing) on MongoDB installation to satisfy this dependency. Additionally, for PyGame, follow the installation guide in PyGame's "Getting Started" documentation (http://www.pygame.org/wiki/GettingStarted). 

NOTE: Make sure you have a MongoDB server running locally on the default port when you attempt to run MapCMU. It will not run without access to a database.
