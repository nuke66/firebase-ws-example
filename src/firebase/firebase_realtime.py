from src.firebase.myusocket import connect
import time
from machine import Timer


class FirebaseRealTime ():

    """ The FirebaseRealTime class is used to connect to the firebase realtime database
    dbConnectionsDetails is a dictionary that contains the socketUrl of the firebase database
    the onDataReceived is a call back handler and will be called when data is received from the firebase database
    the class provides the user with the ability to subscribe to a realtime database and listen to incoming data
    the socket will be authenticated using the tokenID obtained from the authenticator class
    """
    
    def __init__(self, dbConnectionsDetails,rxLED,onDataReceived):
        self.socketAddress = dbConnectionsDetails['sockerUrl']
        self.firebaseSocket = connect(self.socketAddress)
        self.onDataReceived = onDataReceived
        self.rxLED = rxLED
        Timer(mode=Timer.PERIODIC, period=5000, callback=self.keepAlive)

    def authenticateWithSocket(self,tokenID):
        #print("******************************************")
        #print("refresh token in socket")
        credString = '{"t":"d","d":{"r":2,"a":"auth","b":{"cred":"'+tokenID+'"}}}'
        #print(credstring)
        self.firebaseSocket.send(credString)
        #print("******************************************")

    def keepAlive(self,timer):
        self.firebaseSocket.send('0')
 
    def subscribeToRealTime(self,path):
        
        #print("******************************************")
        #print("subscribeString")
        subscribeString = '{"t":"d","d":{"r":2,"a":"q","b":{"p":"'+path+'","h":""}}}'
        self.firebaseSocket.send(subscribeString)
        #print("******************************************")
        

    def listen(self,timer=None):
        incomingMessage = self.firebaseSocket.recv()
        self.onDataReceived(incomingMessage)
            
        # blink to the light to signify that incoming data is avaliable
        if not self.rxLED == None :
            self.rxLED.on()
            time.sleep(0.05)
            self.rxLED.off()
        
