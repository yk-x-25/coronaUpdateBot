from bs4 import BeautifulSoup as bs
import requests,logging
from collections import defaultdict 
import constants
import json
import datetime
import slack 
from tabulate import tabulate
updates=[]
stateWiseChanges=defaultdict(bool)
totalStats=[]
isUpdatesPresent=False

def TabulateData():
    
    headers=constants.statsKeys[2:]
    headers.insert(0,"State")
    tableRows=[]
    
    for state in constants.StateStatsDB.keys():
        tableRows.append([state.rstrip(),constants.StateStatsDB[state][constants.statsKeys[2]],constants.StateStatsDB[state][constants.statsKeys[3]],constants.StateStatsDB[state][constants.statsKeys[4]],constants.StateStatsDB[state][constants.statsKeys[5]]])
    tableRows.append(totalStats)

    return tabulate(tableRows,headers,tablefmt="psql")



def GetDataByStateName(stateName):
    return constants.StateStatsDB[stateName]

def LoadData():
    with open("result.json","r") as fp:
        data =json.load(fp)
    return data

def ScanAndFillUpdateData(stName,statsKeyIndex,prevData,currData):
    global updates
    global stateWiseChanges

    if stateWiseChanges[stName]:
        updates.append("\n"+constants.statsKeys[statsKeyIndex]+" Previous : "+prevData+" Now: "+currData)
        
    else:
        stateWiseChanges[stName]=True
        updates.append("\n******\n"+stName+" :\n"+constants.statsKeys[statsKeyIndex]+" Previous : "+prevData+" Now: "+currData)
  
def checkStatePresent(stateName):
    try:
        if constants.StateStatsDB[stateName]:
            logging.info("Valid state : " + stateName+" received")
            return True
    except KeyError:
        logging.error("Invalid State received : "+stateName+"\n Fix: \n1.  Check for proper formatting!\n2.statename in the DB is different \n3.Junk StateName")
    return False


def CheckForValidState(tableInput,updateTimeInfo):
    global isUpdatesPresent
    logtag="Validate_State"
    dataSize=len(tableInput)
    
    if dataSize>=5:
        logging.info("Received State Data")
        stateName=tableInput[1].text
        logging.info(logtag+" State received"+ stateName)
        
        if checkStatePresent(stateName):
            
            for i in range(2,len(tableInput)):
                try:
                    prevData=constants.StateStatsDB[stateName][constants.statsKeys[i]]
                    currData=tableInput[i].text
                    logging.info("{}: Data {} for State: {}".format(logtag,stateName,currData))
                    if prevData!=currData:
                        ScanAndFillUpdateData(stateName,i,prevData,currData)
                        constants.StateStatsDB[stateName][constants.statsKeys[i]]=currData
                        isUpdatesPresent=True
                except KeyError:
                    logging.error(logtag+": Invalid key while populating stats")

    if dataSize>=4:
        logging.info("Received Complete India's stats")
        
        for i in tableInput:
            if i.text !=" ":
                totalStats.append(i.text.rstrip().lstrip())
        
    return

def saveFile(Object,FileName):
    with open(FileName, 'w') as fp:
        json.dump(Object, fp)



def GetDataAndProcess():
    global isUpdatesPresent
    global updates
    url="https://www.mohfw.gov.in/"
    updateTimeInfo="Updates at : "+str(datetime.datetime.now())
    req=requests.get(url) 
    soup = bs(req.content, 'html.parser')
    rows=soup.find_all("tr")
    for row in rows:
        col=row.find_all("td")
        if len(col)>0:
            logging.info("[FOUND] Tables found with columns {}" .format(col))
            
            CheckForValidState(col,updateTimeInfo)
    
    if isUpdatesPresent:
        updates.insert(0,updateTimeInfo)
        slackSendMessage=""
        for i in updates:
            slackSendMessage+=i
        slack.slacker()(slackSendMessage)    
        
    saveFile(constants.StateStatsDB,'result.json')
    
    slack.slacker()(TabulateData())

if __name__ == "__main__":
    logging.basicConfig(filename='BotErrs.log',level=logging.DEBUG)
    constants.StateStatsDB=LoadData()
    GetDataAndProcess()
