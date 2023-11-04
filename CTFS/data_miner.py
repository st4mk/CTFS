#!/usr/bin/env python

import time
import os.path
import threading
import sys 
import getopt 
import pandas as pd 
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent


'''
	Data Mining Routine (Selenium & Beautiful Soup)
'''
def func(driver, filename, file_exist, start_time):
	edges_df = pd.read_csv ('linestring_edges.csv', dtype={'source_lng':str, 'source_lat':str, 'destination_lng':str, 'destination_lat':str})
	edges = []
	first_time = True

	for ind in edges_df.index:
		src_lng = edges_df.iloc[[ind], [0]].to_string(index = False, header = False)
		src_lat = edges_df.iloc[[ind], [1]].to_string(index = False, header = False)
		dest_lng = edges_df.iloc[[ind], [2]].to_string(index = False, header = False)
		dest_lat = edges_df.iloc[[ind], [3]].to_string(index = False, header = False)

		url = f'https://www.google.com/maps/dir/{src_lng},{src_lat}/{dest_lng},{dest_lat}/data=!4m2!4m1!3e0?hl=en' #the path that will be used for searching every edge on Google Maps (preset: english language and drive mode)

		result = None
		driver.get(url)

		if first_time == True:
			time.sleep(5) #wait for page to load
			button = driver.find_element(By.TAG_NAME, 'button') #find the button to click for the very first page on a new session (cookies)
			button.click()
			first_time = False

		while result == None :
			soup = BeautifulSoup(driver.page_source, 'lxml') #get html content of the page that we scraped
			result = soup.find('div', class_='XdKEzd') #navigate to the main class of the html file we are intrested in

		delay_div = result.find('div') #first div class name after the main class above has delay information

		if len(delay_div['class']) > 2:
			delay = delay_div['class'][2] #if third argument in class name exists, this is our delay
		else:
			delay = 'no-data'

		travel_time = result.find('div').text.replace(' min', '') #the text of this class is also our travel time information
		distance = soup.find('div', class_='ivN21e tUEI8e fontBodyMedium').text #find the class which text is our distance information

		if 'km' in distance:
			distance = distance.replace(' km', '')
			distance = float(distance)*1000
		else:
			distance = distance.replace(' m', '')
			
		speed = float(distance)/(int(travel_time)*60) 

		if delay == 'delay-heavy':
			speed /= 2
		if delay == 'delay-medium':
			speed /= 1.5

		final_speed = round(speed, 2) #round final speed to only two decimals

		if file_exist == False:
			edges.append([src_lng, src_lat, dest_lng, dest_lat, final_speed]) #information to store on the very first run for specific date 
		else:
			edges.append(final_speed)

		print(f'EdgeID: {ind} => Speed: {final_speed}, Delay: {delay}')

	driver.quit()

	if file_exist == False:
		edge_info = pd.DataFrame(edges, columns = ['source_lng', 'source_lat', 'destination_lng', 'destination_lat', start_time])
		edge_info.to_csv(f'data/{filename}', index=False)
	else:
		edge_info = pd.read_csv(f'data/{filename}')
		edge_info[start_time] = edges #set start time as column name for the information scrapped (speeds)
		edge_info.to_csv(f'data/{filename}', index=False)


'''
	Main Program 
'''
if __name__ =="__main__":
	duration = None
	time_slots = None
  
	try: 
		opts, args = getopt.getopt(sys.argv[1:], "d:s:")   
	except: 
		print("Format: $./data_miner.py -d <duration_in_hrs> -s <time_slots_in_mins>")
		sys.exit(2) 

	for opt, arg in opts:
		if opt in ['-d']: 
			duration = int(arg) 
		elif opt in ['-s']: 
			time_slots = int(arg) 

	sessions = (duration*60)/time_slots
	time_sleep = time_slots*60

	date = datetime.now().date()
	day = datetime.now().strftime('%A')
	filename = f'{day}({date}).csv' #file format

	file_exist = os.path.exists(f'data/{filename}') #check if file already exists

	for rep in range(int(sessions)):
		service = Service('/home/stam/Desktop/CTFS/chromedriver-linux64/chromedriver') #path for driver
		user_agent = UserAgent().random
		options = Options().add_argument(f'--user-agent={user_agent}') #use random user agent on each request to reduce recaptcha
		driver = webdriver.Chrome(options=options, service=service)

		#for second run, if first has not finished yet
		if rep == 1: 
			file_exist = True

		#on last run do not sleep, just join
		if rep != (int(sessions)-1): 
			current_time = datetime.now().strftime('%H:%M') #get start time to pass it to the target function
			thr = threading.Thread(target=func, args=(driver,filename,file_exist,current_time,)) #creating thread
			thr.start()
			time.sleep(time_sleep) #time to wait until a new session begins (in seconds)
		else:
			current_time = datetime.now().strftime('%H:%M') #get start time to pass it to the target function
			thr = threading.Thread(target=func, args=(driver,filename,file_exist,current_time,)) #creating thread
			thr.start()
			thr.join() #wait until last thread is completely executed
