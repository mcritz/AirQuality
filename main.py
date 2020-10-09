from dotstar import DotStar
import json
from machine import SPI, Pin
import network
import socket
import time
import urequests
import uos
from purpleair import PurpleAir

try:
    directoryContents = uos.listdir('.')
    if 'log.bak.csv' in directoryContents:
        uos.remove('log.bak.csv')
    if 'log.csv' in directoryContents:
        uos.rename('log.csv', 'log.csv.bak')
    print('logs ready')
except:
    print('error cleaning logs')

spi = SPI(sck=Pin(12), mosi=Pin(2), miso=Pin(19))
dstar = DotStar(spi, 1) # Just one DotStar
dstar[0] = (32, 0, 0)

class WiFi():
    ssid = ''
    password = ''
    wlan = network.WLAN( network.STA_IF )
    
    def __init__(self, configs):
        self.ssid = configs['ssid']
        self.password = configs['password']
    def connect(self):
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        while not self.wlan.isconnected:
            pass
        self.wlan.ifconfig()
    def shutdown(self):
        print('disconnect')
        self.wlan.active(False)

class AirQualityStatus():
    Unknown = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4
    Level5 = 5
    Level6 = 6

    # DotStar compatible color as (R, G, B, A)
    def colorValue(self, value):
        colorValueSwitcher = {
            0: (20, 22, 23, 0.5),
            1: (0, 128, 24, 1.0),
            2: (64, 64, 0, 1.0),
            3: (128, 64, 0, 1.0),
            4: (128, 0, 0, 1.0),
            5: (128, 0, 128, 1.0),
            6: (128, 0, 64, 1.0),
        }
        return colorValueSwitcher.get(value, (0, 0, 0, 0))

    # English name of color
    def colorName(self):
        switcher = {
            0: "Gray",
            1: "Green",
            2: "Yellow",
            3: "Orange",
            4: "Red",
            5: "Purple",
            6: "DarkPurple",
        }
        return switcher.get(self.value, "Black")


# Handles network requests
class AQNetwork:
    wifi = ""
    url = ""
    createdAt = 0
    rawAQ = 0
    convertedAQ = 0
    aqStatus = AirQualityStatus()
    purpleAir = PurpleAir()
    
    def __init__(self, configFilePath):
        try:
            with open('config.json', 'r') as file:
                data = json.load(file)
                print('config.json data: ', data)
                self.url = data['url']
                wifiConfig = {
                    'ssid': data['ssid'],
                    'password': data['password']
                }
                self.wifi = WiFi(wifiConfig)
        except:
           print('Could not load or parse config.json')

    def parseStats(self, value):
        data = json.loads(value)
        # v1 is the 10 minute average
        return float(data["v1"])

    def fetchQuality(self):
        self.wifi.connect()
        time.sleep(15)
        print("connect")
        response = urequests.get(self.url)
        jssn = response.json()
        self.createdAt = jssn["results"][0]["LastSeen"]
        self.rawAQ = self.parseStats(jssn["results"][0]["Stats"])
        self.convertedAQ = self.purpleAir.aqFromPM(self.rawAQ)
        self.aqStatus = self.aqValue(self.convertedAQ)
        self.wifi.shutdown()

    # Good                              0 - 50           0.0 - 15.0         0.0 – 12.0
    # Moderate                         51 - 100          >15 - 40        12.1 – 35.4
    # Unhealthy for Sensitive Groups  101 – 150         > 40 – 65          35.5 – 55.4
    # Unhealthy                       151 – 200         > 65 – 150       55.5 – 150.4
    # Very Unhealthy                  201 – 300         > 150 – 250     150.5 – 250.4
    # Hazardous                       301 – 400         > 250 – 350     250.5 – 350.4
    # Hazardous                       401 – 500         > 350 – 500     350.5 – 500
    def aqValue(self, rawAQ):
        self.aqStatus = 0
        if rawAQ < 0:
            self.aqStatus = 0
            return self.aqStatus
        if rawAQ <= 12:
            self.aqStatus = 1
            return self.aqStatus
        if rawAQ <= 35:
            self.aqStatus = 2
            return self.aqStatus
        if rawAQ <= 55:
            self.aqStatus = 3
            return self.aqStatus
        if rawAQ <= 150:
            self.aqStatus = 4
            return self.aqStatus
        if rawAQ <= 250:
            self.aqStatus = 5
            return self.aqStatus
        if rawAQ > 250:
            self.aqStatus = 6
            return self.aqStatus
        return self.aqStatus

def writeLog(text):
    print(text)
    try:
        logFile = open("log.csv", "a")
        logFile.write(text)
        logFile.write("\n")
        logFile.close()
    except:
        print("log error")

aqn = AQNetwork('config.json')
aqs = AirQualityStatus()
sleepTime = 5 * 60 # 5 minutes

writeLog("time,value,status")

while True:
    dstar[0] = (0, 0, 0, 0)
    try:
        aqn.fetchQuality()
        aqColor = aqs.colorValue(aqn.aqStatus)
        thisDatum = "{0},{1},{2}"
        dstar[0] = aqColor
        writeLog(thisDatum.format(aqn.createdAt, aqn.convertedAQ, aqn.aqStatus))
        time.sleep(sleepTime)
    except:
        print('error,error,error')
        time.sleep(30)
