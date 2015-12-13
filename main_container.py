import pyinotify
import time
import RPi.GPIO as GPIO
import MySQLdb
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5,GPIO.OUT)
GPIO.output(5,True)

print "program started"
 
state = 0

def onChange(env):
	global state
        print "Change Detected\n"
	fp = open('new_msgs.txt','r')
	
	msg = ''.join(fp.read())
	fp.close()
	msg = msg.split(',')
	print msg
	number = msg[2]
	text = msg[6]
	print number
	username = text.split('/')[0]
	username = username[1:]
	print username
	password = text.split('/')[1]
	command  = text.split('/')[2]
	print password
	number =number[4:]
	number = number[:-1]
	print number
	db = MySQLdb.connect(host = 'localhost',user ='root',passwd = "raspberry" ,db ="DoorSMS")
	cur = db.cursor()
	cur.execute("select username,passwd from cred where mobile = '"+number+"'")
	result = cur.fetchone()
	print result
	if result is None:
		fp_open=open("./watchdir/sendmsg.txt","w")
                fp_open.write(number)
                fp_open.write(',')
                fp_open.write('Number not found , Invalid User')
                fp_open.close()
	else :
		print result[0]
		print result[1]
		if username.strip() ==  result[0].strip() and password.strip()== result[1].strip():
			if command == 'addUser':
				newuser= text.split('/')[3].strip()
				newpass = text.split('/')[4].strip()
				newmob = text.split('/')[5].strip()
				cur.execute('Insert into cred values ("'+newuser+'","'+newpass+'","'+newmob+'")')
				
				db.commit() 
			elif command == 'open' and state == 0:
				fp_open=open("./watchdir/sendmsg.txt","w")
                		fp_open.write(number)
                		fp_open.write(',')
                		fp_open.write('Sucessful Authentication, Door Opened')
                		fp_open.close()
				state =1
				GPIO.output(5,False)
				time.sleep(5)
				GPIO.output(5,True)
			elif command == 'open' and state ==1:
				fp_open=open("./watchdir/sendmsg.txt","w")
                                fp_open.write(number)
                                fp_open.write(',')
                                fp_open.write('Door is already open')
                                fp_open.close()
			elif command == 'close' and state == 1 :
				fp_open=open("./watchdir/sendmsg.txt","w")
                                fp_open.write(number)
                                fp_open.write(',')
                                fp_open.write('Sucessful Authentication,Door Locked')
                                fp_open.close()
                                state =0
                                GPIO.output(5,False)
                                time.sleep(5)
                                GPIO.output(5,True)
			else :
				fp_open=open("./watchdir/sendmsg.txt","w")
                                fp_open.write(number)
                                fp_open.write(',')
                                fp_open.write('Door is already closed')
                                fp_open.close()


		else :
			fp_open=open("./watchdir/sendmsg.txt","w")
	                fp_open.write(number)
        	        fp_open.write(',')
               		fp_open.write('Invalid Username/passwd,')
                	fp_open.close()


'''	if "open" in text:
		GPIO.setmode(GPIO.BOARD)
		#GPIO.setup(5,GPIO.OUT)
		GPIO.output(5,False)
		time.sleep(5)
		print "Open"
		fp_open=open("./watchdir/sendmsg.txt","w")
		number = number[4:]
		number = number[:-1]
		fp_open.write(number)
		fp_open.write(',')
		fp_open.write('Username/Password')
		fp_open.close()
		GPIO.setup(5,GPIO.OUT)
		GPIO.output(5,True)
		time.sleep(5)'''

wm = pyinotify.WatchManager()
wm.add_watch('new_msgs.txt', pyinotify.IN_MODIFY, onChange)
notifier = pyinotify.Notifier(wm)
notifier.loop()
