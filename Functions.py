import cv2
from time import sleep
import base64
from datetime import datetime, timezone
import requests
import pytz
import RSerial
import RPi.GPIO as GPIO

timeZone = pytz.timezone("Europe/Berlin")

postUrl = 'http://77.55.211.131:4000/add/'

def TakePhoto():
    
    vid = cv2.VideoCapture(0)

    ret, frame = vid.read()

    today = datetime.now(timeZone)

    dateTimeValue = today.strftime("%y-%m-%d %H:%M:%S")
    name = today.strftime("%y-%m-%d_%H:%M:%S")
    cv2.imwrite(f'{name}.png', frame)
    vid.release()
    sleep(1)

    

    data = open(f'{name}.png', 'rb').read()

    output = base64.b64encode(data)

    jsonData = {
        "ID": "0",
        "BASE": output,
        "DATE" : dateTimeValue
    }

    response = requests.post(postUrl, json = jsonData)
    print(response.status_code)

def GrantAccess():

    SetUp()
    GPIO.output(4, GPIO.HIGH)
    sleep(1)
    GPIO.output(4, GPIO.LOW)

def SetUp():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)

def CheckHash(hash):

    with open('SHA256.txt', 'r') as f:
        data = f.readlines()
    
    for item in data:
        if item.strip() == hash:
            return True
    
    return False
