"""
Function to wrap all functions
"""

"""
Load libraries
"""
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
	
import argparse
import csv
import functools
import glob
import logging
import os
import time
import re
import sys
import pandas as pd
reload(sys)
sys.setdefaultencoding('utf8')

import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO		
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator, TextConverter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
from cStringIO import StringIO
#from xlrd import open_workbook
#import pdftables_api

"""
Read CSV files 
"""
KeywordsPG = pd.read_csv("D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\MastersBOW.csv")
KeywordsGrad = pd.read_csv("D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\BachelorsBOW.csv")
Pin_code_list= pd.read_csv("D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\20170127_all_india_pin_code.csv")
KeywordsHSC=pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\HSC.csv')
KeywordsSSC=pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\SSC.csv')
UniversityTier= pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\20170117_BagOfWords_Education_V1.csv')
Univ_list = pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Data_Masters\\20170117_BagOfWords_Education_V1.csv')
Univ_list["Univ_Lower"]=Univ_list['New_name'].str.lower()
Univ_list["Univ_length"]=Univ_list['Univ_Lower'].str.len()
Univ_list= Univ_list[Univ_list['Univ_length']>10]
Univ_list= Univ_list.reset_index()


"""
Read all pdf files from the working directory
"""

"""
define working directory
"""
os.chdir("D:\\WinPython-64bit-2.7.6.4\\PDF to Table")
#os.chdir("C:/Users/tmehta/Desktop/Subrajit/Axis Bank/Tabular")

#Today's date for filename
date = time.strftime("%Y%m%d")

import os.path

filesname= []

filesname=pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\filespath206.csv')
filesname=filesname['filepath']


# for root, directories, files in os.walk("D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\CV"):
	# for filename in files:
		# # Join the two strings in order to form the full filepath.
		# filepath = os.path.join(root, filename)
		# filesname.append(filepath)
			

###Declare the master dataframe
columns = ["Name_Path","Email_Address","Mobile_Number","YOB","Address_PIN","District","State","Is_Post_Graduate","Is_Graduate","Post_Graduate_details","Graduate_details","Post_Graduate_details_key","Graduate_details_key","Post_Graduate_College","Graduate_College","PG_percentage","Graduate_percentage","PG_Univ_Tier","Graduate_Univ_Tier","Banking_Role","Circle","Region","City","Post_Graduate_College_Score","Graduate_College_Score","Post_Graduate_College_text","Graduate_College_text","Is_Bank","Graduate_Parttime","Post_Graduate_Parttime","Age","Years_Experience","Is_sales","Check_Pin"]	

df_master= pd.DataFrame(columns = columns)

k=0
for i in range(0,len(filesname)): 
	
	##read the exact file name to pass to reading xls file		
	try:
		input_pdf_path = filesname[i]
		split_path = input_pdf_path.split('\\')
		length = len(split_path)
		split_path = split_path[length-1]
		regex = re.compile("(.+?)"+r".pdf")
		result = re.search(regex,split_path ) 
		# To remove ".pdf" from the file name
		file_title = result.group(1)
	except:
		continue
		

	###Declare empty variables
	Name_Path,Age,Email_Address,Mobile_Number,YOB,Address_PIN,District,State,Is_Post_Graduate,Is_Graduate,Post_Graduate_details,Graduate_details,Post_Graduate_details_key,Graduate_details_key,Post_Graduate_College,Graduate_College,PG_percentage,Graduate_percentage,PG_Univ_Tier,Graduate_Univ_Tier,Banking_Role,Circle,Region,City, Post_Graduate_College_Score,Graduate_College_Score,Post_Graduate_College_text,Graduate_College_text,Is_Bank,Graduate_Parttime,Post_Graduate_Parttime,Years_Experience,Is_sales,Check_Pin="","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""

	###return name, mobile number and pin code
	string_to_search = convert_pdf_to_txt(input_pdf_path)
	# Substitue multiple double spaces with a single space
	string_to_search = re.sub(' +',' ',string_to_search)
	Name_Path = filesname[i]
	Mobile_Number,Email_Address,Address_PIN,District,State
	Mobile_Number = check_phone_number(string_to_search)
	Email_Address = check_email(string_to_search)

	##return pin number address and circle
	list_of_values = return_pin_location(string_to_search)
	if list_of_values:
		Address_PIN = list_of_values[0]
		District = list_of_values[1]
		State = list_of_values[2]
		Check_Pin = list_of_values[3]
		Circle = list_of_values[4]
	##print output
	Address_PIN, District, State

	##return year of birth
	YOB = return_year_of_birth(string_to_search)
	try:
		YOB = int(YOB)
	except:
		None
	if YOB > 1950 and YOB < 2000:
		YOB = YOB
	else:
		YOB = float('nan')
		

	## return Age
	if YOB:
		Age = int(time.strftime("%Y")) - YOB
		if ((Age>60) or (Age<18)):
			Age = float('nan')
		else:
			None
	else:
		Age = float('nan')

	###calling functions for education
	# check_for_ed_table = fun_istable(string_to_search)

	###extract PG, UG and percentage values
	Is_Post_Graduate = fun_isPG(string_to_search)[0]
	Post_Graduate_details = fun_isPG(string_to_search)[1]
	Post_Graduate_details_key = Post_Graduate_details
	Post_Graduate_Parttime = Partime(string_to_search,"PG")
	Is_Graduate = fun_isGrad(string_to_search)[0]
	Graduate_details = fun_isGrad(string_to_search)[1]
	Graduate_details_key = Graduate_details
	Graduate_Parttime = Partime(string_to_search,"G")
	

	### TO BE DELETED
	#check for education table presense and pass to dataframe
	# if check_for_ed_table==0:
		# is_ed_table="No"
	# else:
		# is_ed_table="Yes"
		
	if Is_Post_Graduate=="Yes":
		PG_percentage = fun_get_percentage(string_to_search,Post_Graduate_details)
	if Is_Graduate=="Yes":	
		Graduate_percentage = getMarksForGrad(input_pdf_path)
			
	
	
	###check for table for percentage values
		
	'''
	##check for graduation details
	output=	fuzzywuzzy_check2(string_to_search,Is_Graduate,Graduate_details_key)
	try:
		Graduate_College= output[1]
		Graduate_College_Score= output[0]
		Graduate_College_text= output[2]
	except:
		None

	##check for post graduate details
	output=	fuzzywuzzy_check2(string_to_search,Is_Post_Graduate,Post_Graduate_details_key)
	try:
		Post_Graduate_College= output[1]
		Post_Graduate_College_Score= output[0]
		Post_Graduate_College_text= output[2]
	except:
		None		
	'''
	
	##check for experience years
	Years_Experience = Experience(string_to_search,Is_Post_Graduate, YOB)
	
	
	
	##check for banking experience
	Is_Bank = banking(string_to_search)
	if Is_Bank == "Yes" and Years_Experience>0:
		Is_Bank = "Yes"
	else:
		Is_Bank = "No"
		
	##check for sales experience
	Is_sales = Sales(string_to_search)
	if Is_sales == "Yes" and Years_Experience>0:
		Is_sales = "Yes"
	else:
		Is_sales="No"
	row = [Name_Path,Email_Address,Mobile_Number,YOB,Address_PIN,District,State,Is_Post_Graduate,Is_Graduate,Post_Graduate_details,Graduate_details,Post_Graduate_details_key,Graduate_details_key,Post_Graduate_College,Graduate_College,PG_percentage,Graduate_percentage,PG_Univ_Tier,Graduate_Univ_Tier,Banking_Role,Circle,Region,City,Post_Graduate_College_Score,Graduate_College_Score,Post_Graduate_College_text,Graduate_College_text,Is_Bank,Graduate_Parttime,Post_Graduate_Parttime,Age,Years_Experience,Is_sales,Check_Pin]
	df_master.loc[k]=row
	k=k+1

###cleaning the data
df_master["Avg_marks"] = df_master[['Graduate_percentage', 'PG_percentage']].mean(axis=1)
df_master.Post_Graduate_details = [re.sub('[^A-Za-z]+', '', i) for i in df_master.Post_Graduate_details]
df_master.Post_Graduate_details = [i.upper() for i in df_master.Post_Graduate_details]
df_master.Graduate_details = [re.sub('[^A-Za-z]+', '', i) for i in df_master.Graduate_details]
df_master.Graduate_details = [i.upper() for i in df_master.Graduate_details]
df_master.PG_percentage = [re.sub('[^0-9.]+', '', i) for i in df_master.PG_percentage]	
df_master.Graduate_percentage = [re.sub('[^0-9.]+', '', i) for i in df_master.Graduate_percentage]

##cleaning numbers 
df_master["Graduate_percentage"] = df_master["Graduate_percentage"].convert_objects(convert_numeric=True)
df_master["PG_percentage"] = df_master["PG_percentage"].convert_objects(convert_numeric=True)
df_master.loc[df_master["Graduate_percentage"]<1,["Graduate_percentage"]] = df_master.loc[df_master["Graduate_percentage"]<1,["Graduate_percentage"]]*100
df_master.loc[df_master["PG_percentage"]<1,["PG_percentage"]] = df_master.loc[df_master["PG_percentage"]<1,["PG_percentage"]]*100

#calculating new fields like age,marks average etc
df_master["YOB"] = df_master["YOB"].convert_objects(convert_numeric=True)
df_master["Graduate_percentage"] = df_master["Graduate_percentage"].convert_objects(convert_numeric=True)
df_master["PG_percentage"] = df_master["PG_percentage"].convert_objects(convert_numeric=True)

df_master["Age"] = int(time.strftime("%Y")) - df_master["YOB"]
df_master["Age"] = np.where(df_master["Age"]>60,float('nan'),df_master["Age"])

df_master["Marks_Category"] = "Less than 50%"
df_master["Marks_Category"][df_master["Avg_marks"]>50] = "Equal & Greater than 50%"

##calculating experience 
df_master["Years_Experience"] = np.where(df_master["Years_Experience"]<0,0,df_master["Years_Experience"])
df_master["Years_Experience_bucket"] = np.where(df_master["Years_Experience"]>2,"Above 2 Years",np.where(df_master["Years_Experience"]==0,"Fresher ", "0 - 2 Years"))


#writing the file
df_master.to_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\' + date + '_Output.csv')