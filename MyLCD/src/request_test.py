import socket
from Queue import Queue
import struct
import os

eth_132 = [0x00,0x0c,0x29,0xbe,0x4a,0xe6]

eth_130 = [0x00,0x0c,0x29,0x89,0xaf,0x38]
eth_133 = [0x00, 0x0c, 0x29, 0xfb, 0xfb, 0xd8]


ip_130 = [0xc0, 0xa8, 0x87, 0x82]
ip_132 = [192, 168, 135, 132]
ip_133 = [192, 168, 215, 133]


HOST0='192.168.135.130'
HOST1='192.168.135.132'
PORT=9999
interface = "eth1"
RAW_PORT = 0X00

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
s.bind((interface,RAW_PORT))
while True:
    data = b''
    for i in eth_132:
        data += struct.pack("!B", i)
    for i in eth_130:
        data += struct.pack("!B", i)
    data += struct.pack("!H", 0x0800)
    data += struct.pack("!B", 0x45)

    #data += struct.pack("!11s", '')
    data += struct.pack("!B", 0x00)
    data += struct.pack("!B", 0x00)
    data += struct.pack("!B", 0x30)
    data += struct.pack("!B", 0x53)
    data += struct.pack("!B", 0x2c)
    data += struct.pack("!B", 0x40)
    data += struct.pack("!B", 0x00)
    data += struct.pack("!B", 0x40)
    data += struct.pack("!B", 0x11)
    data += struct.pack("!B", 0x57)
    data += struct.pack("!B", 0x39)

    for i in ip_130:
        data += struct.pack("!B", i)
    for i in ip_132:
        data += struct.pack("!B", i)
    
    
    #data += struct.pack("!8s", '')
    data += struct.pack("!H", 0x270f)
    data += struct.pack("!H", 0x270f)
    data += struct.pack("!H", 0x001a)
    data += struct.pack("!H", 0x9085)


    data+= struct.pack("!HHBBBB", 100, 0x0064, 0x00, 0X01, 0X01, 0X00 )
    name = "mytext.txt"
    name_len = len(name)
    data+= struct.pack("!H%us"%name_len, name_len, name)
    s.send(data)
    print("send over")


    ss = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    ss.bind((interface,RAW_PORT))
    res, addr = ss.recvfrom(1514)
    print res[42:]
    break

s.close()
