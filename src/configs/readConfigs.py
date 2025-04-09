import json

wifiPath = "sec/wifi.json"
dbConnectionsPath = "sec/connections.json"
accountPath = "sec/account.json"

def readJSONFile(path):
    try:
        fileReader = open(path)
        data = fileReader.read()
        jsonObj = json.loads(data)
        fileReader.close()
        return jsonObj
    except:
        raise Exception("Can not read file " + path)

def accountDetails():
    return readJSONFile(accountPath)

def DBConnectionsDetails():
    return readJSONFile(dbConnectionsPath)

def readWifi():
    return readJSONFile(wifiPath)


currentListOfWifi = readWifi()
dbConnectionsDetails = DBConnectionsDetails()
accountDetail = accountDetails()