

import os
import constants
import requests, zipfile, io
import pathlib
import time
import pickle
import APIlinks
import json
import winreg;
from urllib.request import urlopen
import admin
import shutil



# if update available
#stop program before update
def stopProgram():
    os.system("TASKKILL /F /IM "+constants.software_name+".exe")


def isConnected():
    url = "http://www.google.com"
    timeout = 5

    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        return True

    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet connection.")
        return False


# after update run screentime
def runSoftware():
    print("runSoftware updater")
    try:
        os.startfile(constants.software_name+".exe")
    except:
        print("except updater 1")
        # try:
        # #print('"'+str(pathlib.Path().resolve())+'\\'+constants.updater_name+'.py"')
        #     os.system('"'+str(pathlib.Path().resolve())+'\\'+constants.software_name+'.exe"')
        # except:
        #     print("except updater 2")
        #     pass
        pass

# add updater to startup
def addToReg():

    try:
        ##get current file path
        package_dir = os.path.abspath(os.path.dirname(__file__))
        file_dir = os.path.join(package_dir,  constants.updater_name+'.exe')

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,winreg.KEY_SET_VALUE);
        winreg.SetValueEx(key, 'speed', 0,winreg.REG_SZ,file_dir); # file_path is path of file 
        #print ("add exe in regex successful")

    except Exception as e:
        print ("Error to add exe in regex moreinfo="+str(e))


#download zip from url and extract in folder
def downloadFile(url):
    #TODO add second method  
    print("downloading update.. please wait")
    #print(pathlib.Path().resolve())
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # pathlib.Path().resolve() is full path to current file folder
    #TODO remove test
    z.extractall(str(pathlib.Path().resolve()))

    # print (url)
    # file_name = "screentime_v3.zip"
    # r = requests.get(url, stream = True) 
          
    # #download started 
    # with open(file_name, 'wb') as f: 
    #     for chunk in r.iter_content(chunk_size = 1024*1024): 
    #         if chunk: 
    #             f.write(chunk)


def showUpdateUI():
    print("showing ui")


def deleteAllFiles():
    print("removing old version "+str(pathlib.Path().resolve()))
    try:
        shutil.rmtree(str(pathlib.Path().resolve())+"\\certifi")
        shutil.rmtree(str(pathlib.Path().resolve())+"\\psutil")
        shutil.rmtree(str(pathlib.Path().resolve())+"\\PyQt5")
    except:
        pass

    #shutil.rmtree(str(pathlib.Path().resolve()))

    mydir = str(pathlib.Path().resolve())
    filelist = [ f for f in os.listdir(mydir) ]
    for f in filelist:
        if(f.startswith(constants.updater_name)!=True):
            print(str(mydir+"\\"+f))
            #os.chmod(os.path.join(mydir, f), 0o777)
            #os.unlink(str(mydir+f))
            print("removed file ="+str(f))
        


def crossCheck():
    print("checking version..")
    version=constants.software_version
    # get version via pickle


    try:
        file = open(constants.software_version_pickle_name, 'rb')
        version = pickle.load(file)
        file.close()
        print("current version "+str(version))
    except:
        print("error while checking version")
    

    #get version from API
    try:
        response = requests.get(APIlinks.software_update_api)
    except:
        response = requests.get(APIlinks.software_update_api_backup)


    response_dict =response.json()
    online_version = response_dict['version']
    online_link= response_dict['link']

    if(online_version!=version):
        admin.run_as_admin()
        print("update found..")
        print ("updating program... please wait")
        #if update found stop program
        stopProgram()

        #show UI of update using thread
        #showUpdateUI()

        #downlaod and run new software
        #TODO enable this
        #deleteAllFiles()

        downloadFile(online_link)

        #run software after update
        runSoftware()




#loop if connected to internet
def checkNet():
    
    while True:
        print('checking internet connection..')
        if(isConnected()):
            # if user online go to checking API
            crossCheck()
            break
        else:
            time.sleep(2)

print('running Screentime updater')
print("please don't close this window")

import sys

def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    input("Press RETURN. ")

sys.excepthook = myexcepthook

addToReg()
# loop internt checker
checkNet()

