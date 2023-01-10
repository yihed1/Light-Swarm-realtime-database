import pyrebase
firebaseConfig={
    "apiKey": "AIzaSyBY-b_AJ9AI4VVR3DXGCTAqRkYAQbrvauM",
    "authDomain": "pyrebaserealtimedbdemo-7228c.firebaseapp.com",
    "databaseURL": "https://pyrebaserealtimedbdemo-7228c-default-rtdb.firebaseio.com",
    "projectId": "pyrebaserealtimedbdemo-7228c",
    "storageBucket": "pyrebaserealtimedbdemo-7228c.appspot.com",
    "messagingSenderId": "266812449433",
    "appId": "1:266812449433:web:67ed5b998cc6ff607f0e08",
    "measurementId": "G-6S5F5QLP8Y"

}

firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()

import RPi.GPIO as GPIO
import sys  
import time 
import random
import serial
import matplotlib.pyplot as plt
import select
from drawnow import *
from gpiozero import LED
from netifaces import interfaces, ifaddresses, AF_INET
from socket import *
import json
GPIO.cleanup()
VERSIONNUMBER = 6
# packet type definitions
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
CHANGE_TEST_PACKET = 2   # Not Implemented
RESET_ME_PACKET = 3
DEFINE_SERVER_LOGGER_PACKET = 4
LOG_TO_SERVER_PACKET = 5
MASTER_CHANGE_PACKET = 6
BLINK_BRIGHT_LED = 7
MYPORT = 2910
SWARMSIZE = 6
status = 0
logString = ""
# command from RasPiConnect Execution Code
columnDataPin = 20
rowDataPin = 21
latchPIN = 14
clockPIN = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup((columnDataPin,rowDataPin,latchPIN,clockPIN),GPIO.OUT)
yellow = LED(25)

selDigit = [18,16,4,26]
# Digits:   1, 2, 3, 4
display_list = [23,17,5,22,27,24,19] # define GPIO ports to use
#disp.List ref: A ,B ,C,D,E,F ,G
#digitDP = 5
#DOT = GPIO 20
# Use BCM GPIO references instead of physical pin numbers
# Set all pins as output
GPIO.setwarnings(False)
for pin in display_list:
  GPIO.setup(pin,GPIO.OUT) # setting pins for segments
for pin in selDigit:
  GPIO.setup(pin,GPIO.OUT) # setting pins for digit selector
#GPIO.setup(digitDP,GPIO.OUT) # setting dot pin
GPIO.setwarnings(True)
# DIGIT map as array of array ,
#so that arrSeg[0] shows 0, arrSeg[1] shows 1, etc
arrSeg = [[0,0,0,0,0,0,1],\
          [1,0,0,1,1,1,1],\
          [0,0,1,0,0,1,0],\
          [0,0,0,0,1,1,0],\
          [1,0,0,1,1,0,0],\
          [0,1,0,0,1,0,0],\
          [0,1,0,0,0,0,0],\
          [0,0,0,1,1,1,1],\
          [0,0,0,0,0,0,0],\
          [0,0,0,0,1,0,0]]

def showDisplay(digit):
 for i in range(0, 4): #loop on 4 digits selectors (from 0 to 3 included)
  sel = [0,0,0,0]
  sel[i] = 1
  GPIO.output(selDigit, sel) # activates selected digit
  numDisplay = int(digit[i])
  GPIO.output(display_list, arrSeg[numDisplay]) # segments are activated according to digit mapping
  time.sleep(0.001)
  
def splitToDisplay (toDisplay): # splits string to digits to display
 arrToDisplay=list(toDisplay)
 print (arrToDisplay)
 return arrToDisplay


def shift_update_matrix(input_Col,Column_PIN,input_Row,Row_PIN,clock,latch):
  #put latch down to start data sending
  GPIO.output(clock,0)
  GPIO.output(latch,0)
  GPIO.output(clock,1)

  #load data in reverse order
  for i in range(7, -1, -1):
    GPIO.output(clock,0)
    #instead of controlling only 1 shift register, we drive both together
    GPIO.output(Column_PIN, int(input_Col[i]))
    GPIO.output(Row_PIN, int(input_Row[i]))
    GPIO.output(clock,1)

  #put latch up to store data on register
  GPIO.output(clock,0)
  GPIO.output(latch,1)
  GPIO.output(clock,1)

#map your output into 1 (LED off) and 0 (led on) sequences
smile=[["11111111"],\
       ["11000011"],\
       ["10111101"],\
       ["01011010"],\
       ["01111110"],\
       ["01100110"],\
       ["10111101"],\
       ["11000011"]]

matrix=[["11111111"],\
       ["01111111"],\
       ["00111111"],\
       ["00011111"],\
       ["00001111"],\
       ["00000111"],\
       ["00000011"],\
       ["00000001"],\
       ["00000000"]]

outmat=[["11111111"],\
       ["11111111"],\
       ["11111111"],\
       ["11111111"],\
       ["11111111"],\
       ["11111111"],\
       ["11111111"],\
       ["11111111"]]

test=[["00000000"],\
       ["00000000"],\
       ["00000000"],\
       ["00000000"],\
       ["00000000"],\
       ["00000000"],\
       ["00000000"],\
       ["00000000"]]



def show_matrix():
    matValue=[0,0,0,0,0,0,0,0]
    length = len(swarmValue0)
    step = int(length/8)
    for i in range(0, 8, 1):
        if (length == 0):
            break
        if (swarmValue0[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue0[step * i]
        if (swarmValue1[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue1[step * i]
        if (swarmValue2[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue2[step * i]    
        if (swarmValue3[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue3[step * i]   
        if (swarmValue4[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue4[step * i]
        if (swarmValue5[step * i] == None):
            matValue[i] = matValue[i] + 0
        else:
            matValue[i] = matValue[i] + swarmValue5[step * i]

        if (matValue[i] < 128):
            outmat[i] = matrix[1]
        elif (128 <= matValue[i] < 256):
            outmat[i] = matrix[2]
        elif (256 <= matValue[i] < 384):
            outmat[i] = matrix[3]
        elif (384 <= matValue[i] < 512):
            outmat[i] = matrix[4]        
        elif (512 <= matValue[i] < 640):
            outmat[i] = matrix[5]        
        elif (640 <= matValue[i] < 768):
            outmat[i] = matrix[6]
        elif (768 <= matValue[i] < 896):
            outmat[i] = matrix[7]
        elif (896 <= matValue[i] <= 1024):
            outmat[i] = matrix[8]
    print(matValue)
            
# UDP Commands and packets

def SendDEFINE_SERVER_LOGGER_PACKET(s):
    print("DEFINE_SERVER_LOGGER_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# get IP address
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            print('%s: %s' % (ifaceName, ', '.join(addresses)))
  
    # last interface (wlan0) grabbed 
    print(addresses) 
    myIP = addresses[0].split('.')
    print(myIP) 
    data= ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1,'little') 
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(myIP[0]).to_bytes(1,'little') # 1 octet of ip
    data[5] = int(myIP[1]).to_bytes(1,'little') # 2 octet of ip
    data[6] = int(myIP[2]).to_bytes(1,'little') # 3 octet of ip
    data[7] = int(myIP[3]).to_bytes(1,'little') # 4 octet of ip
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))


def SendRESET_SWARM_PACKET(s):
    print("RESET_SWARM_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(RESET_SWARM_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
      	
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
	
def SendRESET_ME_PACKET(s, swarmID):
    print("RESET_ME_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(RESET_ME_PACKET).to_bytes(1,'little')
    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1,'little')
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
      	
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
      	
def SendCHANGE_TEST_PACKET(s, swarmID):
    print("RESET_ME_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(RESET_ME_PACKET).to_bytes(1,'little')
    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1,'little')
    
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
      	
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
	

def SendBLINK_BRIGHT_LED(s, swarmID, seconds):
    print("BLINK_BRIGHT_LED Sent") 
    print("swarmStatus=", swarmStatus);
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(0,14)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(BLINK_BRIGHT_LED).to_bytes(1,'little')
    print("swarmStatus[swarmID][5]", swarmStatus[swarmID][5]) 
    
    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1,'little')
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    if (seconds > 12.6):
        seconds = 12.6
    data[4] = int(seconds*10).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
    data[8] = int(0x00).to_bytes(1,'little')
    data[9] = int(0x00).to_bytes(1,'little')
    data[10] = int(0x00).to_bytes(1,'little')
    data[11] = int(0x00).to_bytes(1,'little')
    data[12] = int(0x00).to_bytes(1,'little')
    data[13] = int(0x0F).to_bytes(1,'little')
      	
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))

	
def parseLogPacket(message):
       
	incomingSwarmID = setAndReturnSwarmID((message[2]))
	print("Log From SwarmID:",(message[2]))
	print("Swarm Software Version:", (message[4]))
	
	print("StringLength:",(message[3]))
	logString = ""
	for i in range(0,(message[3])):
		logString = logString + chr((message[i+5]))

	print("logString:", logString)	
	return logString
# build Webmap

def readValue(logString, swarmsize):
    global readtime
    frametime = time.time() - readtime
    readtime = time.time()
    data= [0 for i in range(swarmsize)]
    status= [0 for i in range(swarmsize)]
    swarmList = logString.split("|")
    for i in range(0,swarmsize):
        swarmElement = swarmList[i].split(",")
        set = 0
        for j in range(0,swarmsize):
            if ((int(swarmElement[5])) == 0):
                if ((int(swarmElement[0])) == j):
                    SwarmID = j
            else:
                SwarmID = setAndReturnSwarmID(int(swarmElement[5]))
        if (SwarmID == 0):
            data[0] = int(swarmElement[3])
            status[0] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[1] == 0)) and (status[2] == 0) and (status[3] == 0) and (status[4] == 0) and (status[5] == 0)):
                swarmValue0.append(int(swarmElement[3]))
                masterTime0.append(frametime)
                masterTimee0.append(frametime)
            else:
                swarmValue0.append(0)
                masterTime0.append(0)
                masterTimee0.append(frametime)
        elif (SwarmID == 1):
            data[1] = int(swarmElement[3])
            #swarmValue1.append(int(swarmElement[3]))
            status[1] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[0] == 0)) and (status[2] == 0) and (status[3] == 0) and (status[4] == 0) and (status[5] == 0)):
                swarmValue1.append(int(swarmElement[3]))
                masterTime1.append(frametime)
                masterTimee1.append(frametime)
            else:
                swarmValue1.append(0)
                masterTime1.append(0)
                masterTimee1.append(0)
        elif (SwarmID == 2):
            data[2] = int(swarmElement[3])
            #swarmValue2.append(int(swarmElement[3]))
            status[2] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[0] == 0)) and (status[1] == 0) and (status[3] == 0) and (status[4] == 0) and (status[5] == 0)):
                swarmValue2.append(int(swarmElement[3]))
                masterTime2.append(frametime)
                masterTimee2.append(frametime)
            else:
                swarmValue2.append(0)
                masterTime2.append(0)
                masterTimee2.append(0)
        elif (SwarmID == 3):
            data[3] = int(swarmElement[3])
            #swarmValue2.append(int(swarmElement[3]))
            status[3] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[0] == 0)) and (status[1] == 0) and (status[2] == 0) and (status[4] == 0) and (status[5] == 0)):
                swarmValue3.append(int(swarmElement[3]))
                masterTime3.append(frametime)
                masterTimee3.append(frametime)
            else:
                swarmValue3.append(0)
                masterTime3.append(0)
                masterTimee3.append(0)
        elif (SwarmID == 4):
            data[4] = int(swarmElement[3])
            #swarmValue2.append(int(swarmElement[3]))
            status[4] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[0] == 0)) and (status[1] == 0) and (status[2] == 0) and (status[3] == 0) and (status[5] == 0)):
                swarmValue4.append(int(swarmElement[3]))
                masterTime4.append(frametime)
                masterTimee4.append(frametime)
            else:
                swarmValue4.append(0)
                masterTime4.append(0)
                masterTimee4.append(0)
        elif (SwarmID == 5):
            data[5] = int(swarmElement[3])
            #swarmValue2.append(int(swarmElement[3]))
            status[5] = int(swarmElement[1])
            if ((((int(swarmElement[1])) == 1) and (status[0] == 0)) and (status[1] == 0) and (status[2] == 0) and (status[3] == 0) and (status[4] == 0)):
                swarmValue5.append(int(swarmElement[3]))
                masterTime5.append(frametime)
                masterTimee5.append(frametime)
            else:
                swarmValue5.append(0)
                masterTime5.append(0)
                masterTimee5.append(0)
    return data, status

def makeFig():
    plt.subplot(1,2,1)
    plt.ylim(0, 400)
    plt.title('Value of 6 boards')
    plt.grid(True)
    plt.ylabel('sensor value')
    plt.xlabel('data frame')
    plt.plot(swarmValue0, 'r', label = 'board0')
    plt.plot(swarmValue1, 'g', label = 'board1')
    plt.plot(swarmValue2, 'b', label = 'board2')
    plt.plot(swarmValue3, 'brown', label = 'board3')
    plt.plot(swarmValue4, 'black', label = 'board4')
    plt.plot(swarmValue5, 'yellow', label = 'board5')
    plt.legend(loc ='upper left')
    plt.subplot(1,2,2)
    plt.ylim(0, 30)
    left = [1, 2, 3, 4, 5, 6]
    tick_label = [swarmStatus[0][5], swarmStatus[1][5], swarmStatus[2][5], swarmStatus[3][5], swarmStatus[4][5], swarmStatus[5][5]]
    plt.bar(left, masterTimeSum, tick_label = tick_label,
            width = 0.8, color = ['red', 'green', 'blue', 'brown', 'black', 'yellow'])
    plt.xlabel('board-address')
    plt.ylabel('master time of past 30s')
    plt.title('My bar chart!')

def buildLogFile():
    curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    str1 = "/home/pi/Desktop/Log/"
    str2 = ".txt"
    name = str1 + curtime + str2
    f = open(name, "w")
    content = ""
    content += "Button Pressed!\n"
    content += "Broadcast Self address to ESPs...\n"
    content += "Received Log:\n"
    content += "PacketIndex ESPIndex MasterStatus SensorValue Address\n"
    f.write(content)
    f.close()
    return name

def buildJsonFile():
    curtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    str1 = "/home/pi/Desktop/Json/"
    str2 = ".log"
    name = str1 + curtime + str2
    f = open(name, "w")
    #f.write(content)
    f.close()
    return name

def writeLog():
    f = open(filename, "a+")
    log = ""
    for i in range(SWARMSIZE):
        log += str(packetIndex)
        log += "    "
        log += str(i)
        log += "    "
        log += str(state[i])
        log += "    "
        log += str(value[i])
        log += "    "
        log += str(swarmStatus[i][5])
        log += "\n"
    f.write(log)
    f.close()

def writeJson():
    f = open(filename, "w")
    value = {
        'swarmValue0': swarmValue0,
        'swarmValue1': swarmValue1,
        'swarmValue2': swarmValue2,
        'swarmValue3': swarmValue3,
        'swarmValue4': swarmValue4,
        'swarmValue5': swarmValue5,
        'swarmAddress': [swarmStatus[0][5], swarmStatus[1][5], swarmStatus[2][5], swarmStatus[3][5], swarmStatus[4][5], swarmStatus[5][5]],
        'masterTimeSum': masterTimeSum2,
        }
    db.child('datadata').set(value)
    json.dump(value, f, indent=4, ensure_ascii=False)

def writeTime():
    f = open(filename, "a+")
    log = ""
    log += "Master lasting time from last button to this button:\n"
    log += "ESPIndex Time\n"
    for i in range(SWARMSIZE):
        log += str(i)
        log += "    "
        log += str(masterTimeSum2[i])
        log += "\n"
    f.write(log)
    f.close()
    

def setAndReturnSwarmID(incomingID):
    for i in range(0,SWARMSIZE):
        if (swarmStatus[i][5] == incomingID):
            return i
        else:
            if (swarmStatus[i][5] == 0):  # not in the system, so put it in
    
                swarmStatus[i][5] = incomingID;
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                return i
  
# set up sockets for UDP

s=socket(AF_INET, SOCK_DGRAM)
host = 'localhost';
s.bind(('',MYPORT))
packetIndex = 0

print ("--------------")
print ("LightSwarm Logger")
print ("Version ", VERSIONNUMBER)
print ("--------------")
 
# first send out DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information 
plt.ion()
# swarmStatus
swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]
swarmValue0 = []
swarmValue1 = []
swarmValue2 = []
swarmValue3 = []
swarmValue4 = []
swarmValue5 = []
masterTime0 = []
masterTime1 = []
masterTime2 = []
masterTime3 = []
masterTime4 = []
masterTime5 = []
masterTimee0 = []
masterTimee1 = []
masterTimee2 = []
masterTimee3 = []
masterTimee4 = []
masterTimee5 = []


for i in range(0,SWARMSIZE):
	swarmStatus[i][0] = "NP"

swarmStatus[i][5] = 0

showtime = time.time()
readtime = time.time()
starttime = time.time() + 30
cnt = 0

value = [0 for i in range(SWARMSIZE)]
state = [0 for i in range(SWARMSIZE)]
masterTimeSum = [0 for i in range(SWARMSIZE)]
masterTimeSum2 = [0 for i in range(SWARMSIZE)]

#filename = buildJsonFile()
masterAdd = "0000"

while(1):
	#while (status == 0):
	RowSelect=[1,0,0,0,0,0,0,0]
	show_matrix()
	showDisplay(splitToDisplay(masterAdd))
	for i in range(0,8): # last value in rage is not included by default
		# send row data and row selection to registers
		shift_update_matrix(''.join(map(str, outmat[i])),columnDataPin,\
		                    ''.join(map(str, RowSelect)),rowDataPin,clockPIN,latchPIN)
		#shift row selector
		RowSelect = RowSelect[-1:] + RowSelect[:-1]
		time.sleep(0.001)
	input_state = GPIO.input(6)
	if (input_state == False):
		#writeTime()
		#writeJson()
		SendRESET_SWARM_PACKET(s)
		yellow.on()
		time.sleep(1)
		SendDEFINE_SERVER_LOGGER_PACKET(s)
		time.sleep(1)
		SendDEFINE_SERVER_LOGGER_PACKET(s)
		time.sleep(1)
		SendDEFINE_SERVER_LOGGER_PACKET(s)
		yellow.off()
		filename = buildJsonFile()
		
		SendDEFINE_SERVER_LOGGER_PACKET(s)
		#global status
		status = 1
		s.close()
		s=socket(AF_INET, SOCK_DGRAM)
		host = 'localhost';
		s.bind(('',MYPORT))
		showtime = time.time()
		readtime = time.time()
		starttime = time.time() + 30
		logString = ""
		swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]
		swarmValue0 = []
		swarmValue1 = []
		swarmValue2 = []
		swarmValue3 = []
		swarmValue4 = []
		swarmValue5 = []
		masterTime0 = []
		masterTime1 = []
		masterTime2 = []
		masterTime3 = []
		masterTime4 = []
		masterTime5 = []
		masterTimee0 = []
		masterTimee1 = []
		masterTimee2 = []
		masterTimee3 = []
		masterTimee4 = []
		masterTimee5 = []
		packetIndex = 0
		for i in range(0,SWARMSIZE):
			swarmStatus[i][0] = "NP"
			swarmStatus[i][5] = 0

		showtime = time.time()
		readtime = time.time()
		starttime = time.time() + 30
		
		value = [0 for i in range(SWARMSIZE)]
		state = [0 for i in range(SWARMSIZE)]
		masterTimeSum = [0 for i in range(SWARMSIZE)]
		masterTimeSum2 = [0 for i in range(SWARMSIZE)]
        
	d = s.recvfrom(1024)

	message = d[0]
	addr = d[1]
	if (len(message) == 14):
		
		if (message[1] == RESET_SWARM_PACKET):
		     print ("Swarm RESET_SWARM_PACKET Received")
		     print ("received from addr:",addr)	

		if (message[1] == CHANGE_TEST_PACKET):
		     print ("Swarm CHANGE_TEST_PACKET Received")
		     print ("received from addr:",addr)	

		if (message[1] == RESET_ME_PACKET):
		     print ("Swarm RESET_ME_PACKET Received")
		     print ("received from addr:",addr)	

		if (message[1] == DEFINE_SERVER_LOGGER_PACKET):
		     print ("Swarm DEFINE_SERVER_LOGGER_PACKET Received")
		     print ("received from addr:",addr)	
		
		if (message[1] == MASTER_CHANGE_PACKET):
		     print ("Swarm MASTER_CHANGE_PACKET Received")
		     print ("received from addr:",addr)	

	else:
		if (message[1] == LOG_TO_SERVER_PACKET):
			masterAdd = str(message[2])
			
			if (len(masterAdd) == 2):
				masterAdd = "00" + masterAdd
			elif (len(masterAdd) == 3):
				#masterAdd = "0" + masterAdd
				masterAdd = "0" + masterAdd              
			elif (len(masterAdd) == 1):
    				#masterAdd = "0" + masterAdd
				masterAdd = "000" + masterAdd 
			print ("Swarm LOG_TO_SERVER_PACKET Received")
			print (outmat)
			
			# process the Log Packet
			logString = parseLogPacket(message)
			print ("log message length = ",len(message))
			value, state = readValue(logString, SWARMSIZE)
			#if (time.time() > starttime):
				#swarmValue0.pop(0)
				#swarmValue1.pop(0)
				#swarmValue2.pop(0)
				#swarmValue3.pop(0)
				#swarmValue4.pop(0)
				#swarmValue5.pop(0)
				#masterTime0.pop(0)
				#masterTime1.pop(0)
				#masterTime2.pop(0)
				#masterTime3.pop(0)
				#masterTime4.pop(0)
				#masterTime5.pop(0)
			masterTimeSum[0] = sum(masterTime0)
			masterTimeSum[1] = sum(masterTime1)
			masterTimeSum[2] = sum(masterTime2)
			masterTimeSum[3] = sum(masterTime3)
			masterTimeSum[4] = sum(masterTime4)
			masterTimeSum[5] = sum(masterTime5)
			masterTimeSum2[0] = sum(masterTimee0)
			masterTimeSum2[1] = sum(masterTimee1)
			masterTimeSum2[2] = sum(masterTimee2)
			masterTimeSum2[3] = sum(masterTimee3)
			masterTimeSum2[4] = sum(masterTimee4)
			masterTimeSum2[5] = sum(masterTimee5)
			print ("masterTimeSum2: ",masterTimeSum2)
			if (status == 1):
				#writeLog()
				packetIndex = packetIndex + 1

		else:
			print ("error message length = ",len(message))
	if ((status == 1) and (time.time() > showtime)):
		#drawnow(makeFig)
		writeJson()        
		showtime = time.time() + 1
	#SendDEFINE_SERVER_LOGGER_PACKET(s)