from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#import chromedriver_binary
import time
import re
import os.path
from os import path
import sqlite3
import schedule
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import discord_webhook as dw
from sys import exit
import os

opt = Options()
#linux
#opt.add_argument('--headless')
opt.add_argument('--no-sandbox')
opt.add_argument('--disable-dev-shm-usage')
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1, 
    "profile.default_content_setting_values.notifications": 1 
 	 })


driver = None
URL = "https://teams.microsoft.com"
PASS = 'S7Lf(J%xgUXt\"8\''
CREDS = {'email':'email@gmail.com','passwd':PASS}

def out():
    driver.close()
    driver.quit()
    exit()
    quit()
    os._exit()

def login():
    global driver
    print('logging in...')
    dw.stext('Bot Started, logging in...')
    emailField=driver.find_element_by_xpath('//*[@id="i0116"]')
    emailField.click()
    emailField.send_keys(CREDS['email'])
    print('validating email...')
    driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #nextbutton
    time.sleep(5)
    try:
        passField=driver.find_element_by_xpath('//*[@id="i0118"]')
        passField.click()
        print('validating password...')
        passField.send_keys(CREDS['passwd'])
        driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
        time.sleep(5)
        print('just getting there...')
        driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
        print('LOGIN SUCCESS !!')
        print('[expected `LIST VIEW` of your teams]')
        time.sleep(5)


    except:
	    print('invalid email, kindly correct credentials in CRED Dictionary for help refer README.md')
	    raise SystemExit

def createDB():
    conn=sqlite3.connect('timetable.db')
    c=conn.cursor()
    #create table
    c.execute('''CREATE TABLE IF NOT EXISTS timetable (class text, start_time text, end_time text,day text, ID text)''')
    conn.commit()
    conn.close()
    print("Created timetable Database")

def validate_input(regex,inp):
	if not re.match(regex,inp):
		return False
	return True

def validate_day(inp):
	days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

	if inp.lower() in days:
		return True
	else:
		return False

def add_timetable():

	name = input("Enter class name : ")
	start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
	while not(validate_input("\d\d:\d\d",start_time)):
		print("Invalid input, try again")
		start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

	end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
	while not(validate_input("\d\d:\d\d",end_time)):
		print("Invalid input, try again")
		end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

	day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
	while not(validate_day(day.strip())):
		print("Invalid input, try again")
		end_time = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
	
	eyed=input("Enter any ID for the class: ")

	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()

	# Insert a row of data
	c.execute("INSERT INTO timetable VALUES ('%s','%s','%s','%s','%s')"%(name,start_time,end_time,day,eyed))

	conn.commit()
	conn.close()
	print(f"\nClass ID: {eyed}\nClass Name: {name}\nStart time: {start_time}\nEnd time: {end_time}\nDay: {day}")
	print("\nAdded to the database!\n")

def view_timetable():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	num=0
	print('\t Class Name \tStart Time \t End Time \t Day \t ID')
	for row in c.execute('SELECT * FROM timetable'):
		num+=1
		print(str(num)+'. ',row)
	conn.close()

def update_timetable():
	eyed = input("Enter the class ID you want to update: ")
	conn = sqlite3.connect('timetable.db')
	c = conn.cursor()
	c.execute("SELECT * FROM timetable WHERE ID = :id", {"id":eyed})
	results = c.fetchall()

	if len(results) == 0:
		print(f"Found no such class with ID: {eyed}!")
		return None

	while (True):
		start_time = input("Enter new class start time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",start_time)):
			print("Invalid input, try again")
			start_time = input("Enter new class start time in 24 hour format: (HH:MM) ")

		end_time = input("Enter new class end time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",end_time)):
			print("Invalid input, try again")
			end_time = input("Enter new class end time in 24 hour format: (HH:MM) ")

		day = input("Enter new day (Monday/Tuesday/Wednesday..etc) : ")
		while not(validate_day(day.strip())):
			print("Invalid input, try again")
			end_time = input("Enter new day (Monday/Tuesday/Wednesday..etc) : ")


		c.execute("UPDATE timetable SET start_time = :new_start_time WHERE ID = :class", {"new_start_time":start_time, "class":eyed})
		c.execute("UPDATE timetable SET end_time = :new_end_time WHERE ID = :class", {"new_end_time":end_time, "class":eyed})
		c.execute("UPDATE timetable SET day = :new_day WHERE ID = :class", {"new_day":day, "class":eyed})
		conn.commit()
		conn.close()
		print(f"\nClass with ID: {eyed} \nUpdated with:\nNew start time: {start_time}, \nNew end time: {end_time},\nNew day: {day} \nSUCCESSFUL! ")
		break

def delete_timetable():
	class_name = input("Enter ID of the class you want to delete: ")
	conn = sqlite3.connect("timetable.db")
	c = conn.cursor()
	c.execute("SELECT * FROM timetable WHERE ID = :class", {"class":class_name})
	results = c.fetchall()

	if len(results) == 0:
		print(f"Found no class with ID {class_name}!")
		return None

	_ = input(f"Are you sure you want to delete class {class_name}? This action cant be undone. Press any key to continue. ")
	c.execute("DELETE FROM timetable WHERE ID = :class", {"class":class_name})
	conn.commit()
	conn.close()
	print(f"Deleted Class with ID '{class_name}' Successully! ")

def start_browser():
    global driver
    try:    
	    print("starting browser...")
	    driver=webdriver.Chrome(options=opt)
	    print('getting URL')
	    driver.get(URL)
	    print('awaiting login promt')
	    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
	    if("login.microsoftonline.com" in driver.current_url):
		    login()
    except SystemExit:
	    out()
    except:
	    print('Error loading the browser driver, check function start_browser()')


def attend(class_name,start_time,end_time):
	time.sleep(4)
	webcam = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
	if(webcam.get_attribute('title')=='Turn camera off'):
		webcam.click()
	time.sleep(1)
	print('switched off webcam...')
	microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
	if(microphone.get_attribute('title')=='Mute microphone'):
		microphone.click()
	print('switched off microphone...')
	dw.stext('camera and microphone is turned off...')
	time.sleep(1)
	joinnowbtn = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
	joinnowbtn.click()
	print('Joining class SUCCESSFUL\n currently attending class...')
	dw.stext('Joining class SUCCESSFUL\n currently attending class...')
	
	#dw.send_msg(class_name,'joined',start_time,end_time)
	
	
	#now schedule leaving class
	tmp = "%H:%M"

	class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(start_time,tmp)

	time.sleep(class_running_time.seconds)
	print('time to leave the class')
	dw.stext('time to leave the class')

	try:
		driver.find_element_by_class_name("ts-calling-screen").click()
		driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click() #come back to homepage
		time.sleep(1)
		driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
		print("Class left")
		dw.stext('Class left Successfully!')
		try:
			driver.get(URL)
			WebDriverWait(driver, 20).until(
				EC.presence_of_element_located((By.ID, "left-rail-header")))
		except:
			print('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
			dw.stext('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
			#dw.send_msg(class_name,"left",start_time,end_time)

	except:
		print('seems the lecture has already stopped...')
		dw.stext('seems the lecture has alreay stopped...')
		try:
			driver.get(URL)
			WebDriverWait(driver, 20).until(
				EC.presence_of_element_located((By.ID, "left-rail-header")))
		except:
			print('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
			dw.stext('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
			#dw.send_msg(class_name,'left',start_time,end_time)

def button_present(class_name):
	try:
		button=class_name.find_element_by_class_name("cle-marker")
		button.click()
		print('hey looks like the meeting has been started')
		time.sleep(10)
		return True
	except:
		return False

def check_class(class_name,start_time,end_time):
	global driver
	present=button_present(class_name)
	count=1
	time.sleep(10)
	while count<=15:
		count+=1
		
		if present:
			count-=1
			print('class found...')
			time.sleep(10)
			driver.find_element_by_class_name("ts-calling-join-button").click()
			print('now joining class...')
			dw.stext('class found, now joining...')
			attend(class_name,start_time,end_time)
			break
			
			
		else:
			print('class not found...rechecking after few minutes')
			dw.stext('class not found...rechecking after few minutes')
			time.sleep(20)
			present=button_present(class_name)
	
	if count==16:
		print('Seems there is no class, aborting this search')
		#dw.send_msg(class_name,"noclass",start_time,end_time)



def joinclass(class_name,start_time,end_time):
	global driver	
	print('In function join class: $$')
	
	try:
		driver.get(URL)
		WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.ID, "left-rail-header")))
	except:
		print('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
		dw.stext('Something went wrong in opening the team window,\ncan\'t find the expected window of class list.')
		raise NameError
	
	time.sleep(2)
	try:
		#classes_available = driver.find_elements_by_class_name("name-channel-type")
		classes_available = driver.find_elements_by_class_name("team")
	except:
		print('Not able to find the element by class name [teams]')
		dw.stext('Not able to find the element by class name [teams]')
		raise NameError
	try:
		for i in classes_available:
			print('checking class names')
			if class_name.lower() in i.get_attribute('innerHTML').lower():
				print("Target Subject Found: ",class_name)
				dw.stext("Subject Found..."+str(class_name))
				time.sleep(5)
				print('Checking Class status...')
				dw.stext('Checking Class status...')
				check_class(i,start_time,end_time)
				break
	except NameError:
		pass
	except SystemExit:
		out()
	

def join_specific():
	print('\nSELECT ONE:')
	view_timetable()
	want=int(input("Enter your choice:"))

	name=None
	start_time=None
	end_time=None
	day=None

	conn=sqlite3.connect('timetable.db')
	c=conn.cursor()
	
	cc =0

	for row in c.execute('SELECT * FROM timetable'):
		cc+=1
		if cc==want:
			name=row[0]
			start_time=row[1]
			end_time=row[2]
			day=row[3]
			break
	conn.close()
	if want > cc:
		print('invalid input')
	else:
		print("\nyou have selected class:",name,"\nstarting from:",start_time,"\nto:",end_time,"\non",day)	
		tek=input("Do you want to initiate Bot? [y/n] : ")
		if tek=='y' or tek=='Y':
			start_browser()
			print('initiating join class ... ')
			
			joinclass(name,start_time,end_time)
			print(name,start_time,end_time)

def alert():
	FORM="%H:%M:%S"
	now=datetime.now()
	vv=now.strftime(FORM)
	dw.stext('bot is active at: ' + vv)


def sched():
	tuna=0
	schedule.every(1).minute.do(alert)
	print("scheduling classes...")
	conn=sqlite3.connect('timetable.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		name=row[0]
		start_time=row[1]
		end_time=row[2]
		day=row[3]

		
		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="friday":
			schedule.every().friday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))

	#Start browser
	start_browser()
	
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		print("i am waiting for the class: elapsed time " + str(tuna) + "s")
		tuna+=10
		schedule.run_pending()
		time.sleep(10)

if __name__=="__main__":
	# joinclass("Maths","15:13","15:15","sunday")
	createDB()
	while True:
		op = int(input(("\n\n1. Start Bot \n2. View Timetable \n3. Update Timetable \n4. Add Class \n5. Delete Class\n6. Join Specific Class\n7. Exit\nEnter option : ")))
		if(op==1):
			sched()	
		elif(op==2):
			view_timetable()
		elif (op==3):
			update_timetable()
		elif (op==4):
			add_timetable()
		elif(op==5):
			delete_timetable()
		elif(op==6):
			dw.send_msg('TEST',"testing",'00:00','11:11')
			join_specific()
		else:
			print("Invalid input!")
			exit()