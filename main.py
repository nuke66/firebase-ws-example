# import WIFI_MANAGER 
from src.wifi.wifi import WIFI_MANAGER
from machine import Pin

# import FirebaseRealTime 
'''FIREBASE STACKS--------------'''
from src.firebase.firebase_realtime import FirebaseRealTime
from src.firebase.authenticator import Auth

# import configurations
'''CONFIGURATIONS STACKS--------------'''
from src.configs.readConfigs import currentListOfWifi,dbConnectionsDetails,accountDetail


# create the wifi led, as pin 15
wifiLED = Pin(15, Pin.OUT)

# create your current list of wifi

def onWifiConnected(payload):
    print("--------onWifiConnected------------")
    print(payload)
    print("-----------------------------------")

def onWifiConnectedFailed(payload):
    print("--------onWifiConnectedFailed------")
    print(payload)
    print("-----------------------------------")

def onScannedForWifi(payload):
    print("--------onScannedForWifi-----------")
    print(payload)
    print("-----------------------------------")

def onWifiDisconnected(payload):
    print("--------onWifiDisconnected---------")
    print(payload)
    print("-----------------------------------")

# create your wifi call back
WIFICallbacks = {
    "onWifiConnected":onWifiConnected,
    "onWifiConnectedFailed":onWifiConnectedFailed,
    "onScannedForWifi":onScannedForWifi,
    "onWifiDisconnected":onWifiDisconnected
}


# initialized wifi manager
wifi_manager = WIFI_MANAGER(currentListOfWifi,WIFICallbacks,wifiLED)

# let's check the connection
if wifi_manager.isWifiConnected():
    print("|------- WIFI IS NOW CONNECTED -----------|")
    print("|        Will Connect to RTDB             |")
    print("|-----------------------------------------|")
    
    # 1 - create the authenticator instance
    authenticator = Auth(dbConnectionsDetails['fbKey'])
    
    # extacting your user name and password
    firebaseUserName = accountDetail['firebaseUserName']
    firebaseUserPassword = accountDetail['firebaseUserPassword']
    
    # validate the user to get the ID token
    flg, headers = authenticator.validate_user(firebaseUserName, firebaseUserPassword)
    if flg :
        # once authenticated extract the idToken
        idToken = headers['idToken']

        # prepare the LED pin to indicate the data is being received
        rxLED = Pin("LED", Pin.OUT)

        # create the onDataReceived call back handler
        def onDataReceived(payload):
            # data received from firebase realtime database, do something with it
            print("--------onDataReceived-------------")
            print(payload)
            print("-----------------------------------")

        # create the firebase realtime instance passing in the 
        firebaseRealtime = FirebaseRealTime(dbConnectionsDetails,rxLED, onDataReceived)
        
        # authenticate with the socket using the idToken
        firebaseRealtime.authenticateWithSocket(idToken)

        # subscribe to a path in realtime database
        path = 'my_data/'
        firebaseRealtime.subscribeToRealTime(path)
        
        while True:
            # Keep listen for data update from the server
            firebaseRealtime.listen()
        

    else:
        print("Error authentication user name and password")   
    
else: 
    print("|------- SOME THING WRONG -----------|")
    print("| Check your wifi ssid and password? |")
    print("|------------------------------------|")
