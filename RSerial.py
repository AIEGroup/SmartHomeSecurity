#from typing import Literal
import serial
import time

import struct
import hashlib

from RExceptions import *

#start
_STARTCODE = 0xEF01

#serial address

address = [0xFF, 0xFF, 0xFF, 0xFF]


class PacketType:

    #Types of packets to include in headers

    _COMMANDPACKET = 0x01
    _DATAPACKET = 0x02
    _ACKPACKET = 0x07
    _ENDDATAPACKET = 0x08

class Reply:

    #Possible replies

    _OK = 0x00
    _ERROR_COMMUNICATION = 0x01
    _ERROR_WRONGPASSWORD = 0x13
    _ERROR_INVALIDREGISTER = 0x1A
    _ERROR_NOFINGER = 0x02
    _ERROR_READIMAGE = 0x03
    _ERROR_MESSYIMAGE = 0x06
    _ERROR_FEWFEATUREPOINTS = 0x07
    _ERROR_INVALIDIMAGE = 0x15
    _ERROR_CHARACTERISTICSMISMATCH = 0x0A
    _ERROR_INVALIDPOSITION = 0x0B
    _ERROR_FLASH = 0x18
    _ERROR_NOTEMPLATEFOUND = 0x09
    _ERROR_LOADTEMPLATE = 0x0C
    _ERROR_DELETETEMPLATE = 0x10
    _ERROR_CLEARDATABASE = 0x11
    _ERROR_NOTMATCHING = 0x08
    _ERROR_DOWNLOADIMAGE = 0x0F
    _ERROR_DOWNLOADCHARACTERISTICS = 0x0D

class Commands:

    #Commands to send to scanner

    _VERIFYPASSWORD = 0x13
    _SETPASSWORD = 0x12
    _SETADDRESS = 0x15
    _SETSYSTEMPARAMETER = 0x0E
    _GETSYSTEMPARAMETERS = 0x0F
    _TEMPLATEINDEX = 0x1F
    _TEMPLATECOUNT = 0x1D
    _GETIMAGE = 0x01
    _DOWNLOADIMAGE = 0x0A
    _CONVERTIMAGE = 0x02
    _CREATETEMPLATE = 0x05
    _STORETEMPLATE = 0x06
    _SEARCHTEMPLATE = 0x04
    _LOADTEMPLATE = 0x07
    _DELETETEMPLATE = 0x0C
    _CLEARDATABASE = 0x0D
    _GENERATERANDOMNUMBER = 0x14
    _COMPARECHARACTERISTICS = 0x03
    _UPLOADCHARACTERISTICS = 0x09
    _DOWNLOADCHARACTERISTICS = 0x08
    _SETLED = 0x35

class SystemParamsCodes:

    #Codes to get system params

    _SETSYSTEMPARAMETER_BAUDRATE = 4
    _SETSYSTEMPARAMETER_SECURITY_LEVEL = 5
    _SETSYSTEMPARAMETER_PACKAGE_SIZE = 6

class Buffers:

    #Char buffers

    _CHARBUFFER1 = 0x01
    _CHARBUFFER2 = 0x02



class RSerial:

    address = 0xFFFFFFFF

    def __init__(self):
        self.uart = serial.Serial(port = '/dev/ttyS0', baudrate = 115200, bytesize = serial.EIGHTBITS, timeout = 15)

    def ShiftRight(self, byte: int, steps: int):

        #Shift given byte to the right by given steps

        return byte >> steps & 0xFF

    def ShiftLeft(self, byte: int, steps: int):

        #Shift given byte to the left by given steps

        return byte << steps

    def OpenSerial(self):
        if self.uart.isOpen():
            self.uart.close()

        self.uart.open()

    def CloseSerial(self):
        self.uart.close()

    def SendPacket(self, data: list, packetType: PacketType) -> list:

        #writes packet with headers and payload to serial

        SEND_PACKET_HEADERS = [self.ShiftRight(_STARTCODE, 8), self.ShiftRight(_STARTCODE, 0)] + address

        packetToSend = SEND_PACKET_HEADERS
        packetToSend.append(packetType)

        dataLength = len(data) + 2

        packetToSend.append(self.ShiftRight(dataLength, 8))
        packetToSend.append(self.ShiftRight(dataLength, 0))

        packetToSend += data

        checkSum = sum(packetToSend[6:])

        packetToSend.append(self.ShiftRight(checkSum, 8))
        packetToSend.append(self.ShiftRight(checkSum, 0))

        self.uart.write(bytearray(packetToSend))

    def GetPacket(self) -> list:

        #Reads a packet received from serial
        
        data = []
        i = 0

        while True:
            
            oneByte = self.uart.read()

            if len(oneByte) != 0:

                fragment = struct.unpack('@B', oneByte)[0]
                data.append(fragment)
                i += 1

                if i >= 12: #12 is minimal packet length

                    if data[0] != self.ShiftRight(_STARTCODE, 8) or data[1] != self.ShiftRight(_STARTCODE, 0):
                        raise Exception('Invalid headers')

                    packetPayloadLength = self.ShiftLeft(data[7], 8)
                    packetPayloadLength = packetPayloadLength | self.ShiftLeft(data[8], 0)

                    if ( i < packetPayloadLength + 9 ):
                            continue

                    packetType = data[6]

                    payload = []
                    packetCheckSum = packetType + data[7] + data[8]

                    for j in range(9, 9 + packetPayloadLength - 2):
                        payload.append(data[j])
                        packetCheckSum += data[j]


                    receivedChecksum = self.ShiftLeft(data[i - 2], 8)
                    receivedChecksum = receivedChecksum | self.ShiftLeft(data[i - 1], 0)

                    if packetCheckSum != receivedChecksum:
                        raise Exception('Packet is corrupted!')

                    return [packetType, payload]

            else:
                raise Exception('Byte is empty!')

    def GetSystemParameters(self):
        packetPayload = [
            Commands._GETSYSTEMPARAMETERS,
        ]

        self.SendPacket(packetPayload, PacketType._COMMANDPACKET)
        response = self.GetPacket()

        receivedPacketType = response[0]
        receivedPacketPayload = response[1]

        if ( receivedPacketType != PacketType._ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read successfully
        if ( receivedPacketPayload[0] == Reply._OK):

            statusRegister     = self.ShiftLeft(receivedPacketPayload[1], 8) | self.ShiftLeft(receivedPacketPayload[2], 0)
            systemID           = self.ShiftLeft(receivedPacketPayload[3], 8) | self.ShiftLeft(receivedPacketPayload[4], 0)
            storageCapacity    = self.ShiftLeft(receivedPacketPayload[5], 8) | self.ShiftLeft(receivedPacketPayload[6], 0)
            securityLevel      = self.ShiftLeft(receivedPacketPayload[7], 8) | self.ShiftLeft(receivedPacketPayload[8], 0)
            deviceAddress      = ((receivedPacketPayload[9] << 8 | receivedPacketPayload[10]) << 8 | receivedPacketPayload[11]) << 8 | receivedPacketPayload[12] ## TODO
            packetLength       = self.ShiftLeft(receivedPacketPayload[13], 8) | self.ShiftLeft(receivedPacketPayload[14], 0)
            baudRate           = self.ShiftLeft(receivedPacketPayload[15], 8) | self.ShiftLeft(receivedPacketPayload[16], 0)

            return [statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate]

        elif ( receivedPacketPayload[0] == Reply._ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))


    def GetStorageCapacity(self):

        return self.GetSystemParameters()[2]

    def ClearDatabase(self):
        self.SendPacket([Commands._CLEARDATABASE], PacketType._COMMANDPACKET)
        return self.GetPacket()[1]

    def SaveTemplate(self, positionNumber = -1):
        ## Find a free index
        positionNumber = 1


        packetPayload = [
            Commands._STORETEMPLATE,
            0x01,
            self.ShiftRight(positionNumber, 8),
            self.ShiftRight(positionNumber, 0),
        ]

        self.SendPacket(packetPayload, PacketType._COMMANDPACKET)
        receivedPacket = self.GetPacket()

    def LoadTemplate(self, position, charBuffer: Buffers = Buffers._CHARBUFFER1):
        
        packetPayload = [
        Commands._LOADTEMPLATE,
        charBuffer,
        self.ShiftRight(position, 8),
        self.ShiftRight(position, 0),
        ]

        self.SendPacket(packetPayload, PacketType._COMMANDPACKET)
        return(self.GetPacket())

    def SearchTemplate(self):

        charBufferNumber = Buffers._CHARBUFFER1
        positionStart = 0x0000
        templatesNumber = self.GetStorageCapacity()

        packetPayload = [
            Commands._SEARCHTEMPLATE,
            0x01,
            0x00,
            0x00,
            templatesNumber >> 8,
            templatesNumber & 0xFF
        ]

        self.SendPacket(packetPayload, PacketType._COMMANDPACKET)
        receivedPacket = self.GetPacket()[1]

        print(receivedPacket)

        if ( receivedPacket[0] == 0 ):

            positionNumber = self.ShiftLeft(receivedPacket[1], 8)
            positionNumber = positionNumber | self.ShiftLeft(receivedPacket[2], 0)

            accuracyScore = self.ShiftLeft(receivedPacket[3], 8)
            accuracyScore = accuracyScore | self.ShiftLeft(receivedPacket[4], 0)

            print('Number ' + str(positionNumber) + ' ' + str(accuracyScore))

            return [positionNumber, accuracyScore]
        
        return [-1, 0]

    def GetImage(self):
        self.SendPacket([Commands._GETIMAGE], PacketType._COMMANDPACKET)
        return self.GetPacket()[1]

    def ImageToCharacteristics(self, charBuffer: Buffers = Buffers._CHARBUFFER1):
        self.SendPacket([Commands._CONVERTIMAGE, charBuffer], PacketType._COMMANDPACKET)
        return self.GetPacket()[1]

    def CreateTemplate(self):
        self.SendPacket([Commands._CREATETEMPLATE], PacketType._COMMANDPACKET)
        return self.GetPacket()[1]

    def BitAtPosition(self, n, p):
        twoP = 1 << p
        result = n & twoP
        return int(result > 0)

    def GetTemplateIndex(self, page):
        if ( page < 0 or page > 3 ):
            raise ValueError('The given index page is invalid!')

        packetPayload = [
            Commands._TEMPLATEINDEX,
            page
        ]

        self.SendPacket(packetPayload, PacketType._COMMANDPACKET)
        receivedPacket = self.GetPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != PacketType._ACKPACKET ):
            raise NoTemplateException('The received packet is no ack packet!')

        ## DEBUG: Read index table successfully
        if ( receivedPacketPayload[0] == Reply._OK):

            templateIndex = []

            ## Contain the table page bytes (skip the first status byte)
            pageElements = receivedPacketPayload[1:]

            for pageElement in pageElements:
                ## Test every bit (bit = template position is used indicator) of a table page element
                for p in range(0, 7 + 1):
                    positionIsUsed = (self.BitAtPosition(pageElement, p) == 1)
                    templateIndex.append(positionIsUsed)

            return templateIndex

    def StoreTemplate(self, position = 1, charBuffer: Buffers = Buffers._CHARBUFFER1):
        self.SendPacket([Commands._STORETEMPLATE, charBuffer, self.ShiftRight(position, 8), self.ShiftRight(position, 0)], PacketType._COMMANDPACKET)
        return self.GetPacket()[1]
        

    def GetTemplatesNumber(self):
        self.SendPacket([Commands._TEMPLATECOUNT], PacketType._COMMANDPACKET)

        response = self.GetPacket()[1]

        if  response[0] ==  Reply._OK:

            number = self.ShiftLeft(response[1], 8)
            number = number | self.ShiftLeft(response[2], 0)

            return number

    def EnrollNewModel(self):

        time.sleep(1)

        print('Waiting for finger....')

        while self.GetImage()[0] != 0:
            pass
        
        self.ImageToCharacteristics(Buffers._CHARBUFFER1)

        while self.GetImage()[0] != 2:
            pass

        time.sleep(1)

        print('Waiting for finger....')

        while self.GetImage()[0] != 0:
            pass

        self.ImageToCharacteristics(Buffers._CHARBUFFER2)
        self.CreateTemplate()

        

        with open('templatesNumber.txt', 'r') as f:
            number = int(f.read().strip())
        number += 1
        
        with open('templatesNumber.txt', 'w') as f:
            f.write(str(number))
        result =  self.StoreTemplate(number)

        sha = hashlib.sha256(str(self.DownloadCharacteristics()).encode('utf-8')).hexdigest()

        with open('SHA256.txt', 'a') as f:
            f.write(f'{sha}' + '\n')
        print(sha)

        return result

    def SearchModel(self):

        while self.GetImage()[0] != 0:
            pass

        self.ImageToCharacteristics()
        return self.SearchTemplate()

    def GetSHA256(self, position = -1):

        try:
            if position == -1:
                raise NoTemplateException('No template')
            self.LoadTemplate(position, Buffers._CHARBUFFER1)
            return hashlib.sha256(str(self.DownloadCharacteristics()).encode('utf-8')).hexdigest()
        except NoTemplateException:
            return -1

    def DownloadCharacteristics(self, charBuffer: Buffers = Buffers._CHARBUFFER1):

        self.SendPacket([Commands._DOWNLOADCHARACTERISTICS, charBuffer], PacketType._COMMANDPACKET)

        actionInfo =  self.GetPacket()
        return self.GetPacket()[1]

    
    def SetLed(self, color: int, mode: int, speed: int, cycles: int):
        self.SendPacket([Commands._SETLED], PacketType._COMMANDPACKET)
        return self.GetPacket()
