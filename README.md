
This is a fixed version of this repo

https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time

---


# Firebase Realtime Database Listener in Micropython on Pico W

*Our goal: "Get the Raspberry Pico W Connect to Firebase and Listen to changes to data nodes".*

This article will show you how to get your Pico W do the following:

1. Connect to your Pico w to your home wifi
2. Authenticate with Firebase (using Google Identity Kit rest API)
3. Listen to Firebase Realtime database (rtdb) using a web socket.
<details>
<summary style="font-size:2em"> Some basic concept </summary>

Before getting on with our journey, let's make sure that we understand some key technologies that we will have to deal with while trying to get to our goal, which are listed below:

+ I will be using [Thonny](https://thonny.org/) on a Mac. Even though I got VSCode (my go-to-text editor) set up to work with Pico and Micropython, I find Thonny is good enough to get the job done. So make sure we have installed Thonny and know your way around it. Also, I would assume that you are familiar with Python syntax, as well as you know how to set up your PicoZeroW for mircopython as instructed [here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
+ We will be using [Firebase](https://console.firebase.google.com/u/0/), including  Firebase Authentication, and Firebase Realtime Databases. So make sure that you have a Firebase project set up, and have at least accounts (email and password) that are ready to go. Since you are here I would assume you know your way around Firebase.
+ We will be dealing with [OAuth](https://oauth.net/2/), which is a way to authenticate ourselves into the database. OAuth has many good explanations already, so I wouldn't talk about it in detail here. However, if you are new to OAuth, I would suggest taking 20 minutes to get an idea of what OAuth is by watching [video below](https://www.youtube.com/watch?v=CPbvxxslDTU), just note that (in term of terminologies used in the video):
  + "MyBucksApplication" is equivalent to our Pico W,
  + "Memorial Bank Authorization Server" is equivalent to "Google Identity Kit"
  + "Memorial Bank Resource Server "is equivalent to "Firebase real-time database"

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/CPbvxxslDTU/0.jpg)](https://www.youtube.com/watch?v=CPbvxxslDTU)

+ And lastly WebSocket. I think Fireship explains it well. However, when I first got used to WebSocket, I found that the terminologies are complicated, Making it hard to figure out which functions to be used for setting up socket server and which functions should only be used for client setup. This post [here](https://stackoverflow.com/questions/27014955/socket-connect-vs-bind) really helps to clear it out.

***No soldering or wiring is needed for this. We will only use the built-in LED for indicate the status of connections.***

During the development of this project I have been using a varieties of other tools, however the most useful one is https://websocketking.com/ can be used to test your web socket.

</details>
<details>
<summary style="font-size:2em"> Environment </summary>

Of course,  we will be using: micropython and Thonny for development.

Let's talk about the project structure:

+ `sec/` (This folder stores all the keys, and credentials of your project, including firebase, wifi password, or your service_account.json files) *so it is a good idea **NOT** to commit this folder in your public repo*
+ `src/` (This folder stores all the classes that we will be implementing in our project)
+ `src/configs/readConfig.py` [This file loads all your configurations from the sec/ folder ]
+ `src/firebase` (This folder stores all the code relating to Firebase, and real-time database setup)
+ `src/wifi` (This folder stores all the code relating wifi connection setup)
+ `main.py` (The main file for setting up the project and piecing everything together)

Quick Note on programming style. Throughout this post, I will be using a lot of callBack injection, it is very similar to handler, callback, or delegate in other programming languages. the basic idea is: when we initiate an instance of a class, we also pass in a callbacks objects (a dictionary of functions aka def) so that, once an event is triggered, we can call that function. This allows us to define the behaviors of the the system in a main.py file or any other file without having to modify our class
</details>

## 1. Configuration setup

To make thing a bit easier with credential management and configuring the firebase project, we will be storing these data in different json files, when we run the code: we will read the json files and feed them to our class/function


### Wifi

In the `sec/` folder create a new file and give it a name: **wifi.json** with the following content
``` json
{ "your_ssid": { "ssid": "your_ssid", "pw": "79797979" }}
```
Of course you will need to change all occurrence of `"your_ssid"` with your home ssid and `"79797979"` with your wifi password. 

*Note: you can also provide a list of ssid and password as following*
``` json
{ "ssid_1": { "ssid": "ssid_1", "pw": "pwd01234" },"ssid_2": { "ssid": "ssid_2", "pw": "pwd56789" }}
```
-------
### Firebase Connection

In the `sec/` folder create a new file and give it a name: **connections.json** with the following content 

```json
{
  "socketUrl": "REPLACE YOUR FIREBASE SOCKET URL",
  "fbKey": "REPLACE WITH YOUR FIREBASE Key"
}
```

<details>

<summary>How to find your socket url ?</summary>

Use your web browser (In my case I used Google Chrome) and do the following:
1. Access the firebase realtime console at: https://console.firebase.google.com/u/0/project/{PROJECT_ID}/database/{realtime-database-namespase}/data
2. Open up your browser inspector (right click on the page and select "Inspect")
3. Click on the "Network" tab 
4. Click on "WS" filter
5. Click on the Button with the record icon the top left corner 
![Pico RTDB Overview](https://raw.githubusercontent.com/autumnssun/Pico_W_Firebase_Database_Real_Time/main/assets/how_to_get_socket_url_1.png)
6. cmd + r to reload the page, you should see the network connection running
7. after a few seconds the network should stop and you will see something like this
![Pico RTDB Overview](https://raw.githubusercontent.com/autumnssun/Pico_W_Firebase_Database_Real_Time/main/assets/how_to_get_socket_url_2.png)
8. click on the websocket to inspect it 
![Pico RTDB Overview](https://raw.githubusercontent.com/autumnssun/Pico_W_Firebase_Database_Real_Time/main/assets/how_to_get_socket_url_3.png)  
9. The request URL is your websocket address. 

The web socket should be something like this:
``` html
wss://s-usc1a-nss-2062.firebaseio.com/.ws?v=5&r=f&ns={your-project-id}-default-rtdb
```
</details>


<details>

<summary>How to find your fb key ?</summary>
In your web browser go to your project setting / general: https://console.firebase.google.com/u/0/project/{your-project-id}/settings/general

Your Firebase Key Should be listed there
</details>

-------

### Firebase Account

In the sec/ folder create a new file and give it a name: **account.json** with the following content
*This is your firebase username and password of users listed in your https://console.firebase.google.com/u/0/project/{PROJECT_ID}/authentication/users*

```json
{
  "firebaseUserName": "Firebase user name",
  "firebaseUserPassword": "firebase password"
}
```
</details>

## 2. Connecting Pico W to Wifi:

### Create Wifi Manager class

In the src/wifi folder create a new file and give it a name: **wifi.py**
and paste in this code: 

https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/blob/c3352f83f9f4509cab7fe400a2ce2de21bfcbdfd/src/wifi/wifi.py#L1-L213

You have just created a class to Manage Wifi connection. Now you can start using this class to connect your Pico W to wifi

### Connect to wifi using the WIFI_MANAGER 

In the root folder of your project create a new file: **main.py** (main.py file will be execute automatically every time the Pico W is restarted or booted up).

Paste the following code in the main.py file:

```python
# import WIFI_MANAGER 
from src.wifi.wifi import WIFI_MANAGER
from machine import Pin
# create the wifi led, as pin 15
wifiLED = Pin(15, Pin.OUT)

# import configurations your list of wifi
'''CONFIGURATIONS STACKS--------------'''
from src.configs.readConfigs import currentListOfWifi


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
    
else: 
    print("|-------- SOMETHING WENT WRONG -----------|")
    print("|    Check your wifi ssid and password?   |")
    print("|-----------------------------------------|")
```

Now let's run your main.py file on you Pico W. You should see the following printed out in the Thonny terminal

``` log

--------onWifiConnected------------
{'result': True, 'data': "$YOUR_WIFI_SSID connectedNetwork connected('192.168.18.36', '255.255.255.0', '192.168.18.1', '192.168.18.1')", 'cmd': None}
----------------------------------
|------- WIFI IS NOW CONNECTED -----------|
|        Will Connect to RTDB             |
|-----------------------------------------|

```

## 3. Connect to Realtime Database
Now your Pico W is connected to the Internet, it would be able to do many thing, however we will be focusing on connecting to Firebase specifically Firebase Realtime Database.

As mentioned above I expected you to know your way around Firebase, you had the following already set up in your Firebase project:

+ One user, authenticated by email and password, please note your user name and passwords
+ Realtime Database has been set up with the databases rules, you can use the following rule for the ease of prototyping, of course you will need to implement your own rules in your production project (we wont be cover it here):

``` json
{
  "rules": {
    ".read" : "auth !== null",
    ".write": "auth !== null",
  }
}

```
<details>
<summary> Overview of Realtime Database Connection</summary>
The following diagram shows the steps necessary for connecting and subscribing to Firebase Realtime Database.
As you can see there will be 2 main steps:
+ Authenticate your firebase user account with Google Identity Kit to obtain an ID_Token
+ Use the ID_Token to subscribe to RTDB websocket.

![Pico RTDB Overview](https://raw.githubusercontent.com/autumnssun/Pico_W_Firebase_Database_Real_Time/main/assets/overview_diagram.svg)

</details>

--------
### 3.1 Create authentication class

In src/firebase folder create a new file, give it the name: "authenticator.py" and paste in this code:

https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/blob/c3352f83f9f4509cab7fe400a2ce2de21bfcbdfd/src/firebase/authenticator.py#L1-L100

You have just created a class to Authenticator connection. Now you can start using this class to authenticate your Pico W with Google Identity Kit. However we won't be using it in the main file, we will use it in our firebase_realtime.py file instead

### 3.2 Create firebase realtime class

+ In src/firebase folder create a new file, give it the name: 'firebase_realtime.py'
https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/blob/c3352f83f9f4509cab7fe400a2ce2de21bfcbdfd/src/firebase/firebase_realtime.py#L1-L43

+ in the same folder create "myusocket.py" with the folowing content
https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/blob/c3352f83f9f4509cab7fe400a2ce2de21bfcbdfd/src/firebase/myusocket.py#L1-L66

+ and "protocol.py" with the following contents
https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/blob/c3352f83f9f4509cab7fe400a2ce2de21bfcbdfd/src/firebase/protocol.py#L1-L248

These 3 files will be responsible for create and managing the web socket connection between your Pico W and Firebase Realtime database, using the wire protocol.

# 4. Putting everything together
Congratulation!!! we now have all the pieces to put everything together. If you have been following this post, well done! or you could have download the project from:
https://github.com/autumnssun/Pico_W_Firebase_Database_Real_Time/tree/main 

So at this point you should have created all of the files needed for the project, your project should have all of these files and folders:

![Project tree](https://raw.githubusercontent.com/autumnssun/Pico_W_Firebase_Database_Real_Time/main/assets/folder.png)

Let's update the `main.py` file to use our firebase code. 

Replace the following

``` python
  # let's check the connection
  if wifi_manager.isWifiConnected():
    print("|------- WIFI IS NOW CONNECTED -----------|")
    print("|        Will Connect to RTDB             |")
    print("|-----------------------------------------|")
    
```
with 

```python

  # let's check the connection
  if wifi_manager.isWifiConnected():
    # print("|------- WIFI IS NOW CONNECTED -----------|")
    # print("|        Will Connect to RTDB             |")
    # print("|-----------------------------------------|")

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

```
Now you should be able to run your `main.py` file and the following message will be displayed in Thonny Terminal (I have redacted some sensitive info)

``` log

--------onWifiConnected------------
{'result': True, 'data': "Network connected('192.168.18.36', '255.255.255.0', '192.168.18.1', '192.168.18.1')"}
-----------------------------------
--------onDataReceived-------------
{"t":"c","d":{"t":"h","d":{"ts":1713601266283,"v":"5","h":"s-usc1a-nss-2062.firebaseio.com","s":"***************"}}}
-----------------------------------
--------onDataReceived-------------
{"t":"d","d":{"r":2,"b":{"s":"ok","d":{"auth":{"email_verified":true,"provider":"password","email":"autumns.sun@gmail.com","user_id":"***************","token":{"email_verified":true,"email":"autumns.sun@gmail.com","exp":1713604863,"user_id":"***************","iat":1713601263,"sub":"***************","aud":"***************","auth_time":1713601263,"iss":"https://securetoken.google.com/***************","firebase":{"identities":{"email":["autumns.sun@gmail.com"]},"sign_in_provider":"password"}},"uid":"***************"},"expires":1713604863}}}}
-----------------------------------
--------onDataReceived-------------
{"t":"d","d":{"r":2,"b":{"s":"ok","d":{}}}}
-----------------------------------


```
While keep the terrminal in Thonny running. 

+ Go to the Firebase Console > Realtime Database and create a new data node: `"my_data"` with any value of your choice eg: {"foo":"hello","bar":"world"}. commit the change 
+ And observer the new data being print out.

``` log
--------onDataReceived-------------
{"t":"d","d":{"b":{"p":"my_data","d":{"bar":"world","foo":"hello"}},"a":"d"}}
-----------------------------------
```
+ Change the data around and observer the print out message. Eg: change "world" to hi
```log
{"t":"d","d":{"b":{"p":"my_data/bar","d":"hi"},"a":"d"}}
```

