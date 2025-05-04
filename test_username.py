
import os
import win32api
import psutil
import sys

def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    input("Error occurred please send a mail to developer or using contact us!.Press Enter to exit.")

sys.excepthook = myexcepthook

print ("os.environ.get('USERNAME') = "+str(os.environ.get('USERNAME')))

print ("os.environ.get('USER') = "+str(os.environ.get('USER')))

print ("os.getlogin() = "+str(os.getlogin()))

# print ("pwd.getpwuid( os.getuid() )[ 0 ] = "+str(pwd.getpwuid( os.getuid() )[ 0 ]))


print ("win32api.GetUserName() = "+str(win32api.GetUserName()))


print (" os.path.expanduser('~') = "+str(os.path.expanduser('~')))

userhome = os.path.expanduser('~')
name = os.path.split(userhome)[-1]
print (name)

print (" psutil.Process().username() = "+str(psutil.Process().username()))

from os import environ,getcwd
getUser = lambda: environ["USERNAME"] if "C:" in getcwd() else environ["USER"]
user = getUser()

print (" getUser = lambda: environ['USERNAME'] if 'C:' in getcwd() else environ['USER'] = "+str(user))

input("enter ")

