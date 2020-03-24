from bs4 import BeautifulSoup as bs
import requests,logging
from collections import defaultdict 
import constants
import json
import slack 
from tabulate import tabulate
def TabulateData():
    
    headers=constants.statsKeys[2:]
    headers.insert(0,"State")
    tableRows=[]
    
    for state in constants.StateStatsDB.keys():
        tableRows.append([state.rstrip(),constants.StateStatsDB[state][constants.statsKeys[2]],constants.StateStatsDB[state][constants.statsKeys[3]],constants.StateStatsDB[state][constants.statsKeys[4]],constants.StateStatsDB[state][constants.statsKeys[5]]])
    return tabulate(tableRows,headers,tablefmt="psql")

isUpdatesPresent=False

def GetDataByStateName(stateName):
    return constants.StateStatsDB[stateName]

def LoadData():
    with open("result.json","r") as fp:
        data =json.load(fp)
    return data

def writeChanges():
    logging.info("Updates Present ")
    with open('results.json','a') as fp:
        json.dump(constants.updates, fp)
    
def checkStatePresent(stateName):
    try:
        if constants.StateStatsDB[stateName]:
            logging.info("Valid state : " + stateName+" received")
            return True
    except KeyError:
        logging.error("Invalid State received : "+stateName+"\n Fix: \n1.  Check for proper formatting!\n2.statename in the DB is different \n3.Junk StateName")
    return False

def CheckAndRefreshCache():
    logging.info("Refreshing DB for Updates")
    GetDataAndProcess()


def CheckForValidState(tableInput):
    logtag="Inside CheckForValidState"
    dataSize=len(tableInput)
    if dataSize>5:
        logging.info("Received State Data")
        stateName=tableInput[1].text
        logging.info("[State] received"+ stateName)
        if checkStatePresent(stateName):
            for i in range(2,len(tableInput)):
                try:
                    if constants.StateStatsDB[stateName][constants.statsKeys[i]]!=tableInput[i].text:
                        constants.StateStatsDB[stateName][constants.statsKeys[i]]=tableInput[i].text
                        updates.append
                        isUpdatesPresent=True
                except KeyError:
                    logging.error(logtag+"Invalid key while populating stats")
        return
    if dataSize==5:
        logging.info("Received Complete India's stats")
        return 
    
    logging.info("Received spam data")
    return

def saveFile():
    with open('result.json', 'w') as fp:
        json.dump(constants.StateStatsDB, fp)



def GetDataAndProcess():
    url="https://www.mohfw.gov.in/"
    req=requests.get(url) 
    soup = bs(req.content, 'html.parser')
    rows=soup.find_all("tr")
    for row in rows:
        col=row.find_all("td")
        if len(col)>0:
            logging.info("[FOUND] Tables found with columns")
            CheckForValidState(col)
    saveFile()
    if isUpdatesPresent:
        writeChanges()
    slack.slacker()(TabulateData())

if __name__ == "__main__":
    #isUpdatesPresent=False
    currData=LoadData()
    CheckAndRefreshCache()
    TabulateData()
    