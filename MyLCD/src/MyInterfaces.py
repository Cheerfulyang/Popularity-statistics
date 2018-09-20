import socket
import threading
import logging
from Queue import Queue  
#import time
#import binascii
import traceback
import struct
import ICN_data as pkt
import os
import forwarding

logger = logging.getLogger('MyInterfaces')

BIND_SEND_PORT = [9998, 9999]
BIND_RECV_PORT = 0x00
sendport = 0x00
ETH_P_ALL = 0x0003
ETH_HEADER_LEN = 14
output_num = 0
input_num= 0
file_path = '/home/yangqf/test/mytext.txt'
BUFFER_SIZE = 1024

localInterfaces = forwarding.localInterfaces_132
localMac = forwarding.localMac_132
FWD_TABLE = forwarding.FWD_TABLE_132
ARPTable = forwarding.ARPTable_132

def calculate_packet_num() :
    print "output packet number :%d" %(output_num)
    print "recv packet number : %d" %(input_num)    
def cache_file(data):
    pass
    
def send_file(sock, head):
    file_size = os.path.getsize(file_path)
    logger.debug("file_size :%d" %file_size)
    sent_size = 0
    print "Start connect"

    with open(file_path) as fd:
        while sent_size < file_size:
            remained_size = file_size - sent_size
            send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
            send_file = fd.read(send_size)
            sent_size += send_size
            data = b''
            data += head
            data += struct.pack("!%ds" %send_size, send_file)
            sock.send(data)
    print "Closing connect"    


class forwardPacket(threading.Thread): 
    def __init__(self, t_name, q):  
  
        threading.Thread.__init__(self, name=t_name)  
  
        self.queue = q  
    def run(self):  
        global output_num
        while True :
            
            data = self.queue.get() 
            if struct.unpack('!H', data[42:44])[0] != 0x0064:
                continue
            raw = pkt.Ethpacket(data)
            dstIP = raw.ipHeader.dipstr
            srcIP = raw.ipHeader.sipstr
            content_name = raw.icnHeader.content_name
            InterfaceID = FWD_TABLE[dstIP]
            logger.debug( 'InterfaceID : %s' % (InterfaceID))
            #request
            if raw.icnHeader.icn_type == 0x00: 
                if dstIP in localInterfaces: 
                    dstIP = srcIP
                    #response with content
                    logger.debug( 'get local request packet for : %s' % (content_name))
                    namestr = ''
                    for i in content_name:
                        namestr += i
                    print(content_name == "mytext.txt")
                    if content_name == "mytext.txt":
                        sock = UDPSender.Outputsock[InterfaceID]
                        raw.ethHeader.dmac = ARPTable[dstIP]
                        raw.ethHeader.smac = localMac[FWD_TABLE[dstIP]]
                        raw.icnHeader.icn_type = 0x01
                        raw.icnHeader.LCD_Tag = 0x01
                        head = raw.packed()
                        send_file(sock, head)
                    else:
                        logger.debug( 'dst does not store content : %s' % (content_name))
                else:
                    #forward
                    logger.debug( 'forward request packet for : %s' % (content_name))
                    data_send = b''
                    raw.ethHeader.dmac = ARPTable[dstIP]
                    raw.ethHeader.smac = localMac[FWD_TABLE[dstIP]]
                    data_send += raw.ethHeader.packed()
                    data_send += data[14:]
                    UDPSender.Outputsock[InterfaceID].send(data_send)
                
            #content
            elif raw.icnHeader.icn_type == 0x01:
                
                if dstIP in localInterfaces: 
                    logger.debug( 'get content: %s' % (content_name) )
                    with open(file_path, 'a') as fw:
                        fw.write(raw.icnHeader.content)
                else:
                    if raw.icnHeader.LCD_Tag == 0:
                        #not_lcd
                        logger.debug( 'forward content: %s' % (content_name))
                        data_send = b''
                        raw.ethHeader.dmac = ARPTable[dstIP]
                        raw.ethHeader.smac = localMac[FWD_TABLE[dstIP]]
                        data_send += raw.ethHeader.packed()
                        data_send += data[14:]
                        UDPSender.Outputsock[InterfaceID].send(data_send)
                    else:
                        #lcd_cache
                        logger.debug( 'forward content and cache: %s' % (content_name))
                        with open(file_path, 'a') as fw:
                            fw.write(raw.icnHeader.content)
                        data_send = b''
                        raw.ethHeader.dmac = ARPTable[dstIP]
                        raw.ethHeader.smac = localMac[FWD_TABLE[dstIP]]
                        data_send += raw.ethHeader.packed()
                        data_send += data[14:]
                        UDPSender.Outputsock[InterfaceID].send(data_send)
            else:
                logger.debug("icn_type error : %d" %raw.icnHeader.icn_type)
            

 

class MyICNHandle():
    def __init__( self, ethname_list =[] ):
        self.OutputPort = []
        self._bindeth(ethname_list, self.OutputPort)
        self._handledata(ethname_list)
               
    def _bindeth(self, ethname, OutputPort):
        for i in range( 0, len(ethname) ):
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            try:
                sock.bind( (ethname[i], BIND_RECV_PORT) )
            except:
                raise Exception("create connection to ICN network failed")
            OutputPort.append(sock)
            
    def handledata_thread(self, interface_name, queue):
        global input_num
        self.queue = queue
        recv_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
        recv_socket.bind((interface_name, BIND_RECV_PORT))
        
        logger.debug( 'listening on %s' % (interface_name) )

        while True :
                data, addr = recv_socket.recvfrom(1514) 
                smac = struct.unpack("6B", data[6:12])
                Srcmac = []
                for i in range(len(smac)):
                    Srcmac.append(smac[i])
                if Srcmac in localMac:
                    pass
                else:
                    ethertype = struct.unpack('!H', data[12:14])[0]
                    logger.debug("ethtype: %d" %ethertype )
                    if ethertype != 0x0800 :
                        pass
                    else : 
                        logger.debug("put icn_version!: %d" %struct.unpack("!H", data[42:44])[0])
                        self.queue.put(data)
                input_num += 1  

    def _handledata(self, ethname_list):
        
        for i in range(0, len(ethname_list)) :
            queue = Queue() 
            
            get_data = threading.Thread(target=self.handledata_thread, args=(ethname_list[i], queue) )
            get_data.setDaemon(True)
            get_data.start()
            
            send_data = forwardPacket('SendPacket' + str(i), queue)
            send_data.setDaemon(True)
            send_data.start()



class MyUDPSender():
    def __init__(self, interface_list =[]):
        self.Outputsock = []
        self._bind(interface_list, self.Outputsock)
    
    def _bind(self, interface, Outputsock):
        for i in range( 0, len(interface) ):
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            try:
                sock.bind( (interface[i], sendport) )
            except:
                raise Exception("create connection to ICN network failed")
            Outputsock.append(sock)

               


def instantiate_UDPSender(interface_list=[]):
    global UDPSender
    try:
        UDPSender = MyUDPSender(interface_list)
    except:
        print traceback.format_exc()
        raise Exception("instantiate ICNHandle failed!")
    return

def instantiate_ICNHandle(ethname=[]):
    global ICN_Handler
    try:
        ICN_Handler = MyICNHandle(ethname)
    except:
        print traceback.format_exc()
        raise Exception("instantiate ICNHandle failed!")
    return
