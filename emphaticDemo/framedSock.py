import re

class FramedStreamSock:
     sockNum = 0
     def __init__(self, sock, debug=False, name=None):
          self.sock, self.debug = sock, debug
          self.rbuf = b""       # receive buffer
          if name:
               self.name = name
          else:                 # make default name
               self.name = "FramedStreamSock-%d" % FramedStreamSock.sockNum
               FramedStreamSock.sockNum += 1
     def __repr__(self):
          return self.name
     def sendmsg(self, payload):
          if self.debug: print("%s:framedSend: sending %d byte message" % (self, len(payload)))
          msg = str(len(payload)).encode() + b':' + payload
          while len(msg):
               nsent = self.sock.send(msg)
               msg = msg[nsent:]
     def receivemsg(self):
          state = "getLength"
          msgLength = -1
          while True:
               if (state == "getLength"):
                    match = re.match(b'([^:]+):(.*)', self.rbuf) # look for colon
                    if match:
                         lengthStr, self.rbuf = match.groups()
                         try: 
                              msgLength = int(lengthStr)
                         except:
                              if len(self.rbuf):
                                   print("badly formed message length:", lengthStr)
                                   return None
                         state = "getPayload"
               if state == "getPayload":
                    if len(self.rbuf) >= msgLength:
                         payload = self.rbuf[0:msgLength]
                         self.rbuf = self.rbuf[msgLength:]
                         return payload
               r = self.sock.recv(100)
               self.rbuf += r
               if len(r) == 0:  # zero length read
                    if len(self.rbuf) != 0:
                         print("FramedReceive: incomplete message. \n  state=%s, length=%d, self.rbuf=%s" % (state, msgLength, self.rbuf))
                    return None
               if self.debug: print("%s:FramedReceive: state=%s, length=%d, self.rbuf=%s" % (self, state, msgLength, self.rbuf))

     #remove debug and put filename instead
     #from there recieve can look for same file and then detect duplicates!
     def sendFile(sock, payload, debug=0):
          if debug:
               print("fileSend: sending %d byte file" % len(payload))
               print("the file name typed in is: ",payload)
               print("finding the path")
               try:
                    writePayload = open(payload, "rb")

                    #debugging
                    #print("and that file path is: ", rFilePath)
                    #print("reading file!")
     
                    length = writePayload.read(100)
                    print("length is", length)
                    empty = os.stat(payload).st_size == 0
                    if (empty):
                         print("error, empty file!")
                    while (length and not (empty)):
                         sock.send(length)
                         length = writePayload.read(100)
                         #print("file has finished being sent")
                    sock.close()
                    writePayload.close()
     except IOError:
          print ("File not found, please check your input")

     def getFile(sock, debug=0):

          readF = open("CopyFile.txt", "wb")
          length = sock.recv(100)
          while(length):
               readF.write(length)
               length = sock.recv(100)
               print("file copied!")
               readF.close()
               sock.close()
