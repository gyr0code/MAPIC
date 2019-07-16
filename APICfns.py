import serial
import socket
import datetime
import numpy

class APIC:
    def __init__(self, address,tout,ipv4):
        self.tout = tout # Timeout
        self.address = address #COM port/or dev/tty
        self.ipv4 = ipv4
        #self.ser = serial.Serial(address,115200,timeout=tout)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(ipv4)

    def readI2C(self,pot):
        if pot != 0 or 1:
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([0,address])
        self.sock.send(sercom)
        reply = self.conn.recv(1)
        print(int.from_bytes(reply,'little'))

    def writeI2C(self,pot):
        if pot != 0 or 1:
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([1,address])
        value = int(input('value\n>'))
        self.sock.send(sercom)
        self.sock.send(bytes([value]))

    def test(self):
        sercom = bytearray([3,3])
        self.sock.send(sercom)
        print(self.conn.recv(6))
        print(self.sock.recv(6))

    def ADC_trig(self,datpts):
        sercom = bytearray([2,1])
        self.sock.send(sercom)
        data = numpy.zeros((datpts,8),dtype='uint16')
        times = numpy.zeros(datpts,dtype='uint32')  
        datptsb = datpts.to_bytes(8,'little',signed=False)
        readm = bytearray(16)
        logtimem = bytearray(4)
        d0 = datetime.datetime.now()
        self.sock.send(datptsb)
        
        for x in range(datpts):
            self.sock.recv_into(readm,16)
            self.sock.recv_into(logtimem,4)
            data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            times[x] = int.from_bytes(logtimem,'little')

        d1 = datetime.datetime.now()

        numpy.savetxt('datairq.txt',data)
        numpy.savetxt('timeirq.txt',times)

        d = d1-d0
        d = d.total_seconds()
        print(d)

'''
    def scanI2C(self):
        sercom = bytearray([0,2])
        self.sock.send(sercom)
        time.sleep(0.5)
        if self.ser.in_waiting()>0:
            print(self.conn.recvline().decode()[:-2])
        else:
            print('No I2C devices found.')
'''