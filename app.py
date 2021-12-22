from time import sleep
from datetime import datetime, timezone
import RSerial
import RPi.GPIO as GPIO
import Functions
from events import Events
import threading
from flask import Flask

app = Flask(__name__)
    

_PIN = 4

enrollNew = False

i = 0

scanner = RSerial.RSerial()

event = Events()

def ChangeStatus():

    global enrollNew
    enrollNew = True
    print('changed ' + str(enrollNew))

@app.route('/')
def hello_world():
    event.on_changed += ChangeStatus()
    return 'Done'

def Start():
    app.run(host='0.0.0.0')






thread = threading.Thread(target = Start)
thread.start()




while(True):

    

    try:

        data = scanner.SearchModel()

    except Exception:
        continue
    print(data)

    scanner.LoadTemplate(data[0])

    sha = scanner.GetSHA256(data[0])

    print(sha)

    if data[0] != -1:

        scanner.LoadTemplate(data[0])
        i = 0

        if(Functions.CheckHash(sha) == True):
            Functions.GrantAccess()

           
    elif i == 11:
        Functions.TakePhoto()
        print('Photo has been taken')
        i = 0
    else:
        i += 1

    print(enrollNew)

    if enrollNew == True:
        scanner.EnrollNewModel()
        enrollNew = False