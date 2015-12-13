import os,time,serial
import pyinotify
import RPi.GPIO as GPIO
import sys,logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


ser=serial.Serial("/dev/ttyUSB0",9600,timeout=1)
 
ser.open()
time.sleep(5)

class MyHandler(FileSystemEventHandler):
	def on_modified(self,event):
		print "msg send part"
		fp=open('./watchdir/sendmsg.txt','r')
		text=fp.read(64)
		text= text.split(',')
		print text[0]
		ser.write('AT+CMGS="'+text[0]+'"'+'\r\n')
		time.sleep(1)
		rcv = ser.read(500)
		print rcv
	
		time.sleep(1)

		ser.write(text[1]+'\r\n')  # Message
		time.sleep(1)
 		rcv = ser.read(500)
		print rcv
		

		ser.write("\x1A\r\n") # Enable to send SMS
		time.sleep(2)
		rcv = ser.read(500)
		print rcv
	
		ser.write('AT+CMGD=1,2\r\n')
                time.sleep(3)
                rcv=ser.read(500)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = './watchdir'
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

#    ser=serial.Serial("/dev/ttyUSB0",9600,timeout=1)
 
 #   ser.open()
  #  time.sleep(5)

    while True :
	  	ser.flush()
		time.sleep(2)
		ser.write('AT+CMGL="REC UNREAD"\r\n')
		time.sleep(4)
		rcv=ser.read(500)
		#print rcv
		lines = rcv.splitlines()
		#print len(lines)
		if len(lines)>3 :
			strings = ''
			for line in lines: 
				if "AT+CMGL=" not in line and "+CMTI:" not in line and line != '\r\n' and "OK" not in line and "AT+CMGD" not in line and len(line) > 3:
					strings = strings + line + ", \n"
			if strings != '':
				fp = open('new_msgs.txt','w')
				fp.write(strings)
				fp.close()
			#print rcv
				print "written"
				ser.write('AT+CMGD=1,2\r\n')
				time.sleep(5)
				rcv=ser.read(500)
		lines = []
		rcv = ''
		#rcv=ser.read(1190)
		#print rcv
    ser.close()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


























