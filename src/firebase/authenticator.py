import ujson
import urequests as requests
import time
from machine import Timer

class Auth(object):
    """ 
    Authenticate the user using the firebase authentication service
    the class will take the api key and use it to authenticate the user with google identity tool kit using a simple post request
    the validate_user method will take the user email and password and return the user data if the user is authenticated successfully
    the
    
    """
    def __init__(self, apiKey):
        # construct the enpoint with the api key        
        self.apiKey = apiKey
        self.refreshURL = "https://securetoken.googleapis.com/v1/token?key="+self.apiKey
        self.signInURL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key="+self.apiKey
    
    def validate_user(self, user_email, password):
        # declaring  2 globals varaibles to be used in this scope
        global tokenID
        global expiresAt

        # constructing the username and password, in the header
        data = {"email":user_email,"password":password,"returnSecureToken":True}
        headers = {"content-type": "application/json"}
        post_data = ujson.dumps(data)
        
        # getting the url from the
        _url = self.signInURL
        
        try:
            # send the request to he URL
            res = requests.post(_url, headers = headers,data=post_data)
        except Exception as e:
            # catch any expecption
            return False, e
        # start of extracting headers data
        header_data = ''
        if res.status_code == 200 :
            
            # if the request is successful, extracting headers: idToken, email, refreshToekn, expiresIn, localId
            res_data = res.json()
            header_data = { "content-type": 'application/json; charset=utf-8'}
            for header in ("idToken", "email", "refreshToken", "expiresIn", "localId"):
                header_data[header] = str(res_data[header])
        else:
            # return false, and reason of failing
            # print(res)
            return False, res.json()
        
        # once extract the headers, save data to locals varables
        self.refreshToken = header_data['refreshToken']
        self.localID = header_data['localId']
        self.idToken = header_data['idToken']
        
        # update the global variables with data from the headers 
        tokenID = header_data['idToken']
        expiresAt = int(time.time()) - 60 + int(header_data['expiresIn'])
        
        # set up a timer that trigger the update refresh token function every 1000ms to update the token using the refresh token
        Timer(mode=Timer.PERIODIC, period=1000, callback=self.updateRefreshToken)
        
        # sucessfully authenticated so return true and the header data inclduing the idToken
        return True, header_data

        
    def updateRefreshToken(self,timer=None) :
        global tokenID
        global expiresAt
        if time.time() < expiresAt :
            return False, None, None
        
        # print("refreshing token")
        _url = self.refreshURL
        refreshToken = self.refreshToken
        data = {"grant_type":"refresh_token","refresh_token":refreshToken}
        post_data = ujson.dumps(data)
        try:
            res = requests.post(_url,
                                headers = {'content-type': 'application/json'},
                                data=post_data)
        except Exception as e:
            return False, e, None
        header_data = ''
        if res.status_code == 200 :
            # if the request is successful, extracting headers: id_token, refresh_token, access_token
            res_data = res.json()
            #print(res_data)
            header_data = { "content-type": 'application/json; charset=utf-8'}
            for header in ("id_token", "refresh_token", "access_token","expires_in"):
                header_data[header] = str(res_data[header])
        else:
            # return false, and reason of failing
            return False, res.json(), None    
        self.refreshToken = header_data['refresh_token']
        self.idToken = header_data['id_token']
        
        expiresAt = int(time.time()) - 60 + int(header_data['expires_in'])
        tokenID = header_data['id_token']
        
        if not self.rt == None:
            self.rt.authenticateWithSocket(tokenID)
        
        return True, expiresAt,tokenID