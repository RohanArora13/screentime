
import win32api
import os
from datetime import date
import datetime
import socket   
import requests
## mostly static functions 

def getFileProperties(fname):
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            ## print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        pass

    return props



def getFileDescription(fname):
    """
    pass file location
    Read file description.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        # props['FixedFileInfo'] = fixedInfo
        # props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
        #         fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
        #         fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        
        strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, "FileDescription")
        ## print str_info
        file_description = win32api.GetFileVersionInfo(fname, strInfoPath)


    except:
        pass

    return file_description


def current_table_name():
    current_date = date.today()
    #year = str(current_date.year)
    #month = str(current_date.month)

    return "program_db"


def ConvertSecondtoTime(n):
 
    day = n // (24 * 3600)
 
    n = n % (24 * 3600)
    hour = n // 3600
 
    n %= 3600
    minutes = n // 60
 
    n %= 60
    seconds = n
    
    dictList = {
        "days":day,
        "hours":hour,
        "minutes": minutes,
        "seconds":seconds}

    return dictList


def getTime(n):

    # dictList = {
    #     "days":day,
    #     "hours":hour,
    #     "minutes": minutes,
    #     "seconds":seconds}

    lst = ConvertSecondtoTime(n)

    day = lst['days']
    hour = lst['hours']
    mins = lst['minutes']
    secs = lst['seconds']

    hourNotEmpty = False
    minNotEmpty = False

    if day > 0:

        return str(day)+" Day"

    else:
        if hour > 0:
            hourNotEmpty = True
            if hour == 1:
                return str(hour)+" Hr "+str(int(mins))+" Mins"
            else:
                return str(hour)+" Hrs "+str(int(mins))+" Mins"            
        else:
            if mins >= 0:
                if(hourNotEmpty):
                    if hour == 1:
                        return str(hour)+" Hr "+str(int(mins))+" Mins"
                    else:
                        return str(hour)+" Hrs "+str(int(mins))+" Mins"
                elif(mins > 0):
                    return str(int(mins))+" Minutes"
                else:
                    if secs > 0:
                        return str(int(secs))+" Sec"
                    else:
                        return "0"
 


def sendToAnalytics():

    ipaddr="0.0.0.0"
    try:
        x = requests.get('https://api.ipify.org/?format=text')
        ipaddr = x.text
    except Exception as e:
         print("error in ip address")
    
    #print(ipaddr)

    payload="v=1&t=pageview&tid=UA-216354496-1&cid="+ipaddr+"&uip="+ipaddr+"&dp=run"
    weblink="https://www.google-analytics.com/collect?"

    headers = {
    "Host": "www.google-analytics.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding":"gzip, deflate, br",
    "DNT": "1",
    "Connection":"keep-alive",
    "Upgrade-Insecure-Requests":"1",}

    try:
        x = requests.get(weblink+payload,headers=headers)
    except Exception as e:
        print("error while sending data")
    #print(weblink+payload)
    

# sendToAnalytics()