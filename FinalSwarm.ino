#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

#undef DEBUG

char ssid[] = "DESKTOP-TQMDF64 3910";  //  your network SSID (name)
char pass[] = "12345678";       // your network password

#define VERSIONNUMBER 28

#define LOGGERIPINC 20
#define SWARMSIZE 6
// 30 seconds is too old - it must be dead
#define SWARMTOOOLD 30000

int mySwarmID = 0;
int receiveTime;

// Packet Types

#define LIGHT_UPDATE_PACKET 0
#define RESET_SWARM_PACKET 1
#define DEFINE_SERVER_LOGGER_PACKET 4
#define LOG_TO_SERVER_PACKET 5

static int led_on = 0;

unsigned int localPort = 2910;      // local port to listen for UDP packets
const int ledCount = 7; // the number of LEDs in the bar graph
uint8_t ledPins[] = {D1, D2, D3, D5, D6, D7, D8}; // an array of pin numbers to which LEDs are attached

// master variables
boolean masterState = true;   // True if master, False if not
int swarmValue[SWARMSIZE];
int swarmVersion[SWARMSIZE];
int swarmState[SWARMSIZE];
long swarmTimeStamp[SWARMSIZE];   // for aging

IPAddress serverAddress = IPAddress(0, 0, 0, 0); // default no IP Address

int swarmAddresses[SWARMSIZE];  // Swarm addresses

int voltage = 0;

// variables for light sensor

const int PACKET_SIZE = 14; // Light Update Packet
const int BUFFERSIZE = 1024;

byte packetBuffer[BUFFERSIZE]; //buffer to hold incoming and outgoing packets

// A UDP instance to let us send and receive packets over UDP
WiFiUDP udp;

IPAddress localIP;

void setup()
{

  Serial.begin(9600);
  Serial.println();
  Serial.println();

  Serial.println("");
  Serial.println("--------------------------");
  Serial.println("LightSwarm");
  Serial.print("Version ");
  Serial.println(VERSIONNUMBER);
  Serial.println("--------------------------");

  Serial.println(F(" 11/27/2022"));
  Serial.print(F("Compiled at:"));
  Serial.print (F(__TIME__));
  Serial.print(F(" "));
  Serial.println(F(__DATE__));
  Serial.println();

  //randomSeed(analogRead(A0));
  //Serial.print("analogRead(A0)=");
  //Serial.println(analogRead(A0));

  // everybody starts at 0 and changes from there
  mySwarmID = 0;

  // We start by connecting to a WiFi network
  Serial.print("LightSwarm Instance: ");
  Serial.println(mySwarmID);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  pinMode(D0, OUTPUT);
  pinMode(D4, OUTPUT);
  digitalWrite(D0, HIGH);
  digitalWrite(D4, HIGH);
  for (int thisLed = 0; thisLed < ledCount; thisLed++) {
      pinMode(ledPins[thisLed], OUTPUT);
  }
  // initialize Swarm Address - we start out as swarmID of 0
  

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");

  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("Starting UDP");

  udp.begin(localPort);
  Serial.print("Local port: ");
  Serial.println(udp.localPort());

  // initialize light sensor and arrays
  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {

    swarmAddresses[i] = 0;
    swarmValue[i] = 0;
    swarmTimeStamp[i] = -1;
  }
  swarmValue[mySwarmID] = 0;
  swarmTimeStamp[mySwarmID] = 1;   // I am always in time to myself
  voltage = swarmValue[mySwarmID];
  swarmVersion[mySwarmID] = VERSIONNUMBER;
  swarmState[mySwarmID] = masterState;
  Serial.print("Own value =");
  Serial.println(voltage);

  // set SwarmID based on IP address 
  
  localIP = WiFi.localIP();
  
  swarmAddresses[0] =  localIP[3];
  
  mySwarmID = 0;
  
  Serial.print("MySwarmID=");
  Serial.println(mySwarmID);

}


void loop()
{
  voltage = analogRead(A0);
  int startTime = millis();
  //flash(voltage);
  
  int ledLevel = map(voltage, 0, 1023, 0, ledCount);
   // loop over the LED array:
  for (int thisLed = 0; thisLed < ledCount; thisLed++) {
    if (thisLed < ledLevel) {
        digitalWrite(ledPins[thisLed], HIGH);
    }else { // turn off all pins higher than the ledLevel:
        digitalWrite(ledPins[thisLed], LOW);
    }
  }
  //while (1)
  //{
  //  flash(voltage);
  //  if (millis() > (startTime + 200))
  //  {
  //    break;
  //  }
  //}
  int endTime = millis();
  Serial.print("\n");
  Serial.print("\n");
  Serial.print("start time: "); Serial.println(startTime);
  Serial.print("end time: "); Serial.println(endTime);
  Serial.print("Own value: "); Serial.println(voltage);
  swarmValue[mySwarmID] = voltage;

  int cb = udp.parsePacket();

  if (!cb) {
    //  Serial.println("no packet yet");
    Serial.print(".");
  }
  else {
    receiveTime = millis();
    Serial.print("receive time: "); Serial.println(receiveTime);
    // We've received a packet, read the data from it
    udp.read(packetBuffer, PACKET_SIZE); // read the packet into the buffer
    Serial.print("packetbuffer[1] =");
    Serial.println(packetBuffer[1]);
    if (packetBuffer[1] == LIGHT_UPDATE_PACKET)
    {
      Serial.print("LIGHT_UPDATE_PACKET received from LightSwarm #");
      Serial.println(packetBuffer[2]);
      setAndReturnMySwarmIndex(packetBuffer[2]);

      Serial.print("LS Packet Recieved from #");
      Serial.print(packetBuffer[2]);
      Serial.print(" SwarmState:");
      if (packetBuffer[3] == 0)
        Serial.print("SLAVE");
      else
        Serial.print("MASTER");
      Serial.print(" Remote value:");
      Serial.print(packetBuffer[5] * 256 + packetBuffer[6]);
      Serial.print(" Version=");
      Serial.println(packetBuffer[4]);

      // record the incoming clear color

      swarmValue[setAndReturnMySwarmIndex(packetBuffer[2])] = packetBuffer[5] * 256 + packetBuffer[6];
      swarmVersion[setAndReturnMySwarmIndex(packetBuffer[2])] = packetBuffer[4];
      swarmState[setAndReturnMySwarmIndex(packetBuffer[2])] = packetBuffer[3];
      swarmTimeStamp[setAndReturnMySwarmIndex(packetBuffer[2])] = millis();

      // Check to see if I am master!
      checkAndSetIfMaster();

    }
    if (packetBuffer[1] == RESET_SWARM_PACKET)
    {
      Serial.println(">>>>>>>>>RESET_SWARM_PACKETPacket Recieved");
      masterState = true;
      Serial.println("Reset Swarm:  I just BECAME Master (and everybody else!)");
      //digitalWrite(D0, HIGH);
      digitalWrite(D4, HIGH);
      serverAddress = IPAddress(0, 0, 0, 0);

    }
    if (packetBuffer[1] ==  DEFINE_SERVER_LOGGER_PACKET)
    {
      Serial.println(">>>>>>>>>DEFINE_SERVER_LOGGER_PACKET Packet Recieved");
      serverAddress = IPAddress(packetBuffer[4], packetBuffer[5], packetBuffer[6], packetBuffer[7]);
      Serial.print("Server address received: ");
      Serial.println(serverAddress);

    }
  }

  Serial.print("MasterStatus:");
  if (masterState == true)
  {
    digitalWrite(D4, LOW);
    Serial.print("MASTER");
  }
  else
  {
    digitalWrite(D4, HIGH);
    Serial.print("SLAVE");
  }
  Serial.print("/value=");
  Serial.print(voltage);
  Serial.print("/KS:");
  Serial.println(serverAddress);


  Serial.println("--------");
  broadcastARandomUpdatePacket();
  //Serial.print("broadcast done : ");
  //  sendARandomUpdatePacket();
  sendLogToServer();
}

void flash (int circle) {
  //for (int i = 0; i < 2; i++)
  //{
  //  int interval = circle / 2;
  //  led_on = !led_on;
  //  digitalWrite(D0, led_on ? LOW : HIGH);
   // delay(interval);
  //}
  analogWrite(D0, circle*255/1024);
}

unsigned long sendLightUpdatePacket(IPAddress & address)
{

  Serial.print("sending Light Update packet to:");
  Serial.println(address);

  // set all bytes in the buffer to 0

  memset(packetBuffer, 0, PACKET_SIZE);
  Serial.print("memset : ");
  // Initialize values needed to form Light Packet
  // (see URL above for details on the packets)
  
  packetBuffer[0] = 0xF0;   // StartByte
  packetBuffer[1] = 0;     // Packet Type
  packetBuffer[2] = localIP[3];     // Sending Swarm Number
  packetBuffer[3] = masterState;  // 0 = slave, 1 = master
  packetBuffer[4] = VERSIONNUMBER;  // Software Version
  packetBuffer[5] = (voltage & 0xFF00) >> 8;
  packetBuffer[6] = (voltage & 0x00FF); 
  packetBuffer[7] = 0x0F;  //End Byte
  for (int j = 0; j<=7; j++)
  {
    Serial.print(packetBuffer[j]);
    Serial.print(";  ");
  }

  //Serial.print("packetBuffer done: ");

  // all Light Packet fields have been given values, now
  // you can send a packet requesting coordination
  
  udp.beginPacketMulticast(address,  localPort, WiFi.localIP()); //
  
  //udp.beginPacket(address,  localPort); //
  udp.write(packetBuffer, PACKET_SIZE);
  //Serial.print("write done : ");
  udp.endPacket();
  //Serial.print("endPacket done : ");
  return 0;
}

// delay 0-MAXDELAY seconds
#define MAXDELAY 500
void broadcastARandomUpdatePacket()
{

  int sendToLightSwarm = 255;
  Serial.print("Broadcast ToSwarm = ");
  Serial.print(sendToLightSwarm);
  Serial.print(" ");
  while (1)
  {
    if (millis() > (receiveTime + 100))
    {
      int sendTime = millis();
      Serial.print("send time: "); Serial.println(sendTime);
      break;
    }
    delay(10);
  }
  // delay 0-MAXDELAY seconds
  /*
  int randomDelay;
  randomDelay = random(0, MAXDELAY);
  Serial.print("Delay = ");
  Serial.print(randomDelay);
  Serial.print("ms : ");

  delay(randomDelay);
  //delay(500);
  Serial.print("randomDelay : ");
  */
  IPAddress sendSwarmAddress(192, 168, 137, sendToLightSwarm); // my Swarm Address
  //Serial.print("IPAddress done : ");
  sendLightUpdatePacket(sendSwarmAddress);
  //Serial.print("sendLight done : ");

}
void checkAndSetIfMaster()
{

  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {


#ifdef DEBUG

    Serial.print("swarmValue[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.print(swarmValue[i]);
    Serial.print("  swarmTimeStamp[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.println(swarmTimeStamp[i]);
#endif

    Serial.print("#");
    Serial.print(i);
    Serial.print("/");
    Serial.print(swarmState[i]);
    Serial.print("/");
    Serial.print(swarmVersion[i]);
    Serial.print(":");
    // age data
    int howLongAgo = millis() - swarmTimeStamp[i] ;

    if (swarmTimeStamp[i] == 0)
    {
      Serial.print("TO ");
    }
    else if (swarmTimeStamp[i] == -1)
    {
      Serial.print("NP ");
    }
    else if (swarmTimeStamp[i] == 1)
    {
      Serial.print("ME ");
    }
    else if (howLongAgo > SWARMTOOOLD)
    {
      Serial.print("TO ");
      swarmTimeStamp[i] = 0;
      swarmValue[i] = 0;

    }
    else
    {
      Serial.print("PR ");


    }
  }

  Serial.println();
  boolean setMaster = true;

  for (i = 0; i < SWARMSIZE; i++)
  {

    if (swarmValue[mySwarmID] >= swarmValue[i])
    {
      // I might be master!

    }
    else
    {
      // nope, not master
      setMaster = false;
      break;
    }

  }
  if (setMaster == true)
  {
    if (masterState == false)
    {
      Serial.println("I just BECAME Master");
      digitalWrite(0, LOW);
    }

    masterState = true;
  }
  else
  {
    if (masterState == true)
    {
      Serial.println("I just LOST Master");
      digitalWrite(0, HIGH);
    }

    masterState = false;
  }

  swarmState[mySwarmID] = masterState;

}


int setAndReturnMySwarmIndex(int incomingID)
{
 
  int i;
  for (i = 0; i< SWARMSIZE; i++)
  {
    if (swarmAddresses[i] == incomingID)
    {
       return i;
    } 
    else
    if (swarmAddresses[i] == 0)  // not in the system, so put it in
    {
    
      swarmAddresses[i] = incomingID;
      Serial.print("incomingID ");
      Serial.print(incomingID);
      Serial.print("  assigned #");
      Serial.println(i);
      return i;
    }
    
  }  
  
  // if we get here, then we have a new swarm member.   
  // Delete the oldest swarm member and add the new one in 
  // (this will probably be the one that dropped out)
  
  int oldSwarmID;
  long oldTime;
  oldTime = millis();
  for (i = 0;  i < SWARMSIZE; i++)
 {
  if (oldTime > swarmTimeStamp[i])
  {
    oldTime = swarmTimeStamp[i];
    oldSwarmID = i;
  }
  
 } 
 
 // remove the old one and put this one in....
 swarmAddresses[oldSwarmID] = incomingID;
 // the rest will be filled in by Light Packet Receive
 
  
}


// send log packet to Server if master and server address defined

void sendLogToServer()
{

  // build the string
  //Serial.print("sendLogtoServer starts : ");
  char myBuildString[1000];
  myBuildString[0] = '\0';

  if (masterState == true)
  {
    // now check for server address defined
    if ((serverAddress[0] == 0) && (serverAddress[1] == 0))
    {
      return;  // we are done.  not defined
    }
    else
    {
      // now send the packet as a string with the following format:
      // swarmID, MasterSlave, SoftwareVersion, clearColor, Status | ....next Swarm ID
      // 0,1,15,3883, PR | 1,0,14,399, PR | ....



      int i;
      char swarmString[20];
      swarmString[0] = '\0';
      //Serial.print("before for : ");
      for (i = 0; i < SWARMSIZE; i++)
      {

        char stateString[5];
        stateString[0] = '\0';
        if (swarmTimeStamp[i] == 0)
        {
          strcat(stateString, "TO");
        }
        else if (swarmTimeStamp[i] == -1)
        {
          strcat(stateString, "NP");
        }
        else if (swarmTimeStamp[i] == 1)
        {
          strcat(stateString, "PR");
        }
        else
        {
          strcat(stateString, "PR");
        }

        sprintf(swarmString, " %i,%i,%i,%i,%s,%i ", i, swarmState[i], swarmVersion[i], swarmValue[i], stateString, swarmAddresses[i]);

        strcat(myBuildString, swarmString);
        if (i < SWARMSIZE - 1)
        {

          strcat(myBuildString, "|");

        }
      }
      //Serial.print("after for : ");


    }


    // set all bytes in the buffer to 0
    memset(packetBuffer, 0, BUFFERSIZE);
    // Initialize values needed to form Light Packet
    // (see URL above for details on the packets)
    packetBuffer[0] = 0xF0;   // StartByte
    packetBuffer[1] = LOG_TO_SERVER_PACKET;     // Packet Type
    packetBuffer[2] = localIP[3];     // Sending Swarm Number
    packetBuffer[3] = strlen(myBuildString); // length of string in bytes
    packetBuffer[4] = VERSIONNUMBER;  // Software Version
    
    int i;
    for (i = 0; i < strlen(myBuildString); i++)
    {
      packetBuffer[i + 5] = myBuildString[i];// first string byte
    }
    
    packetBuffer[i + 5] = 0x0F; //End Byte
    Serial.print("Sending Log to Sever:");
    Serial.println(myBuildString);
    int packetLength;
    packetLength = i + 5 + 1;
    Serial.print("Packetlength:");
    Serial.println(packetLength);
    udp.beginPacket(serverAddress,  localPort); //

    udp.write(packetBuffer, packetLength);
    udp.endPacket();

  }



}
