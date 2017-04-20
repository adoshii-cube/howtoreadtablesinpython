"""
Function to read PDF
"""
def convert_pdf_to_txt(input_pdf_path):
    try:
        logging.debug('Converting pdf to txt: ' + str(input_pdf_path))
        # Setup pdf reader
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        # Iterate through pages
        path_open = file(input_pdf_path, 'rb')
        for page in PDFPage.get_pages(path_open, pagenos, maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            interpreter.process_page(page)
        path_open.close()
        device.close()

        # Get full string from PDF
        full_string = retstr.getvalue()
        retstr.close()

        # Normalize a bit, removing line breaks
        full_string = full_string.replace("\r", "\n")
        full_string = full_string.replace("\n", " ")

        # Remove awkward LaTeX bullet characters
        full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)

        return full_string.encode('ascii', errors='ignore')

    except Exception, exception_instance:
        logging.error('Error in file: ' + input_pdf_path + str(exception_instance))
        return ''


"""
Returns phone number oof the candidate
"""
def check_phone_number(string_to_search):
    """
    Find first phone number in the string_to_search
    :param string_to_search: A string to check for a phone number in
    :type string_to_search: str
    :return: A string containing the first phone number, or None if no phone number is found.
    :rtype: str
    """
    try:
		regular_expression = re.compile(r"\+?"	#plus sign
									r"(\d{2})?"	#91 digit
									r"\-?"	 # - between numbers
									r"(\d{10,12})", # 10 digit mobile number
									re.IGNORECASE
									)
		result = re.search(regular_expression, string_to_search)
		if result:
			result = result.group()
			result = result[-10:]
		return result
    except Exception, exception_instance:
        logging.error('Issue parsing phone number: ' + string_to_search + str(exception_instance))
        return None

"""
Function to check email ID
"""
def check_email(string_to_search):
    """
       Find first email address in the string_to_search
       :param string_to_search: A string to check for an email address in
       :type string_to_search: str
       :return: A string containing the first email address, or None if no email address is found.
       :rtype: str
       """
    try:
        regular_expression = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}", re.IGNORECASE)
        result = re.search(regular_expression, string_to_search)
        if result:
            result = result.group()
        return result
    except Exception, exception_instance:
        logging.error('Issue parsing email number: ' + string_to_search + str(exception_instance))
        return None


"""
Create master for PIN code
"""
def pin_code_master():
	df = Pin_code_list
	list1 = df[["Taluk","pincode","Districtname","statename","Circle"]]
	list1["Type"] = "Taluk"
	list1.columns = ['location','pincode',"Districtname","statename","Circle","Type"]

	list2 = df[["Districtname","pincode","Districtname","statename","Circle"]]
	list2["Type"] ="District"
	list2.columns = ['location','pincode',"Districtname","statename","Circle","Type"]
	
	list3 = df[["statename","pincode","Districtname","statename","Circle"]]
	list3["Type"] ="State"
	list3.columns = ['location','pincode',"Districtname","statename","Circle","Type"]
	
	frames = [list2, list1, list3]
	
	list_master = pd.concat(frames)
	list_master["location"] = list_master["location"].str.lower()

	return list_master


"""
Function for calculating area pin number
First check for PIN code
"""
def check_area_pin(string_to_search):
    try:
		regular_expression = re.compile(r"\D(\d{6})\D", # 6 digit pin
									re.IGNORECASE
									)
		result = re.search(regular_expression, string_to_search)
		if result:
			result = result.group()
			result = re.sub("[^0-9]", "", result) #replace special characters
		else:
			regular_expression = re.compile(r"\D(\d{3})"
											r"\s"
											r"(\d{3})\D", # 6 digit pin
									re.IGNORECASE
									)
			result = re.search(regular_expression, string_to_search)
			if result:
				result = result.group()
				result = re.sub("[^0-9]", "", result) #replace special characters

		return result
    except Exception, exception_instance:
        logging.error('Issue parsing area pin: ' + string_to_search + str(exception_instance))
        return None


"""
Then check for Address , Add:
Then check identify location names and their pin code
"""
def check_keywork_address_pin(string_to_search):
	try:
		pos1 = re.search(r"(Place: |Address | Add:| ADDRESS: |Place )", string_to_search,re.IGNORECASE)
		pos1 = pos1.span()[1]
		string_to_search1 = string_to_search[pos1: pos1+300] ##need to take care of wide space and special characters
	except:
		string_to_search1 = string_to_search

	##create pin code list
	Location_list = pin_code_master()
	Location_list1 = Location_list["location"].tolist()

	##convert string to search to a list
	string_to_search1 = re.sub("[^^A-Za-z0-9]", " ", string_to_search1)
	listof_string_to_search = string_to_search1.split()
	listof_string_to_search = [x.lower() for x in listof_string_to_search]
	##match the string
	try:
		loc_type = ["District","Taluk","State"]
		for k in range(0,len(loc_type)):
			Location_list2 = Location_list[Location_list["Type"]==loc_type[k]]
			Location_list2 = Location_list2['location']
			list3 = set(listof_string_to_search)&set(Location_list2)
			if list3:
				list3 = list(list3)[0]
				Location_list2 = Location_list[Location_list['location'] == list3].reset_index(drop=True)
				pin_number = Location_list2.iloc[0]["pincode"]
				location = Location_list2.iloc[0]["location"]

			continue
		return pin_number
		#return pin_number
	except Exception, exception_instance:
		logging.error('Issue parsing area pin: ' + string_to_search + str(exception_instance))
		#return None

"""
Function to return final PINCODE &LOCATION
"""
def return_pin_location(string_to_search):
	Location_list = pin_code_master()
	pin_number = check_area_pin(string_to_search)
	check = 1
	if pin_number:
		pin_number = pin_number
	else:
		pin_number = check_keywork_address_pin(string_to_search)
		check = 2
	try:
		Location_list2 = Location_list[Location_list['pincode'] == int(pin_number)].reset_index(drop=True)
		State = Location_list2.iloc[0]["statename"]
		District = Location_list2.iloc[0]["Districtname"]
		Circle = Location_list2.iloc[0]["Circle"]
		list_of_values = [pin_number,District,State,check,Circle]
		return list_of_values
	except Exception, exception_instance:
		logging.error('Issue parsing area pin: ' + string_to_search + str(exception_instance))
		return None

"""
Function for calculating date of birth through new method
"""
def check_date_of_birth(string_to_search):
	try:
		pos1 = re.search(r"(Birth | birth| BIRTH | DOB | D.O.B)", string_to_search,re.IGNORECASE)
		pos1 = pos1.span()[1]
		string_to_search = string_to_search[pos1: pos1+500]
	except:
		string_to_search = string_to_search
	try:
		regular_expression = re.compile(r'(\d{4})')
		result = re.search(regular_expression, string_to_search)
		if result:
			result = result.group()
			if (int(result)<2000):
				result = result
			else:
				result = ""

		return result

	except Exception, exception_instance:
		logging.error('Issue parsing DOB: ' + string_to_search + str(exception_instance))
		return None


"""
Function for return year of birth irrespective of where date of birth is givencalculating
Logic check for check_date_of_birth function first
if result available then pass result
else check for any 4 digit number . Check wheather its more that 2000 . consider it as date for experience and then estimate DOB
"""
def return_year_of_birth(string_to_search):
	yob = check_date_of_birth(string_to_search)
	if yob == "":
		try:
			regular_expression= re.compile('\\b'+'(\d{4})'+'\\b',re.M|re.I)
			result = regular_expression.findall(string_to_search)
			result = map(int, result)
			result = list(filter(lambda x: x>2000, result))
			result = min(result)
			yop = result
			yob = yop-20
		except:
			yob=""
	return yob


"""
Function to check for a term pattern for education
"""
def term_match(string_to_search, term):
    try:
		regular_expression = re.compile('[^a-zA-Z]'+ term +'[^a-zA-Z]', re.IGNORECASE)
		result = re.findall(regular_expression, string_to_search)
		# result = re.findall('[^a-zA-Z]'+term+'[^a-zA-Z]', string_to_search)
		return result
    except Exception, exception_instance:
        logging.error('Issue parsing term: ' + str(term) + ' from string: ' +
                      str(string_to_search) + ': ' + str(exception_instance))
        return None

"""
Function to check presence of a table
"""
def fun_istable(cv_text):
    # get all percentage in cv
    percentage = re.findall(r'[0-9\.]{0,3}\d{1,2}[\s\.]{0,1}%', cv_text)

    #check count of percentage
    if(len(percentage)>=2):
        percentage_dis = cv_text.find(percentage[1])-cv_text.find(percentage[0])-len(percentage[0])
        #check distance between perc
        if(percentage_dis>5):
            istable = 0
        else:
            istable = 1
    else:
        istable = 0
    #check distance between perc

    return istable

"""
Function to check presence of PG related credentials
"""

def fun_isPG(cv_text):
	# loop to match bag of words
	for j in range(0,len(KeywordsPG['Post Graduation'])):
		curr_key = KeywordsPG['Post Graduation'][j]
		result = term_match(cv_text,curr_key)
		#check if match found
		if len(result)>0:
			# checking for persuing appear
			regular_expression = re.compile('[^a-zA-Z]'+ curr_key +'[^a-zA-Z]', re.IGNORECASE)
			# result = re.findall(regular_expression, string_to_search)
			m = re.search(regular_expression, cv_text)
			pg_pos = m.end()
			curr_cv_pg = cv_text[max((pg_pos -50),1):min(len(cv_text),pg_pos+300)]
			regular_expression = re.compile(r'(?:pursuing|appear|results awaited|pending)', re.M|re.I)
			result1 = re.findall(regular_expression, curr_cv_pg)
			if len(result1)>0:
				return ['No','']
				# print(result)
			else:
				return ['Yes',curr_key]
				# print(result)
			break
	# if none of words match
	if j==len(KeywordsPG['Post Graduation'])-1:
		return ['No','']

"""
Function to check presence of PG related credentials
"""
def fun_isGrad(cv_text):
	# loop to match bag of words
	for j in range(0,len(KeywordsGrad['Graduation'])):
		curr_key=KeywordsGrad['Graduation'][j]
		result=term_match(cv_text,curr_key)
		#check if match found
		if len(result)>0:
			return ['Yes',result[0]]
			break
	# if none of words match
	if j==len(KeywordsGrad['Graduation'])-1:
		return ['No','']

"""
Function to check percentage values
"""
def fun_get_percentage(cv_text,key):
	# get all %
	perc=re.findall(r'[0-9\.]{0,3}\d{1,2}[\s\.]{0,1}%', cv_text)
	if((len(perc)>0)):
		degree_pos=cv_text.find(key)
		perc_pos=len(cv_text)
		nth_perc=0
		# loop for each percantage and match distance
		for j in range(0,len(perc)):
			temp=cv_text.find(perc[j])
			if (degree_pos<temp & temp<perc_pos):
				perc_pos=temp
				nth_perc=j
		return perc[nth_perc]

	else:
		return ''

# TO get percentage for table	and grad only

def fun_get_percentage_table(cv_text,Is_Post_Graduate):
	# get all %
	perc=re.findall(r'[0-9\.]{0,3}\d{1,2}[\s\.]{0,1}%', cv_text)
	if((len(perc)>0)):
		# degree_pos=cv_text.find(key)
		# perc_pos=len(cv_text)
		# nth_perc=0
		# loop for each percantage and match distance

		if((len(perc)>=2) and Is_Post_Graduate=="Yes"):
			return perc[1]
		else:
			return perc[0]
	else:
		return ''


"""
Functions for SK education
"""
#education qualification
#identify cell for education
def education_cell(sheet,flag):
	ed= re.compile("Education|Qualification|Academic|ACADEMIC",re.M|re.I)
	for row in range(sheet.nrows):
		for column in range(sheet.ncols):
			try:
				education= str(sheet.cell(row,column).value)
				if  ed.search(education):
					ed_row= row
					ed_col=column
					if flag==1:
						return ed_row
					if flag==2:
						return ed_col

			except:
				education=""

#get the size of column
def education_table_size(ed_row,ed_col,flag):
	ed_table_rows=0
	ed_table_columns=0
	#get number of columns in education table
	for column in range(1,ed_col):
		if sheet.cell(ed_row+1,column).value =="" :
			ed_table_columns=column-1
			break

	if ed_table_columns==0:
		ed_table_columns=sheet.ncols

	#get number of rows in education table
	for row in range(ed_row+1,ed_row+10):
		print row
		if sheet.cell(row,1).value =="" :
			ed_table_rows=row-1
			break
	if flag==1:
		return ed_table_rows
	if flag==2:
		return ed_table_columns


#read the column headers for education
def check_colnames(ed_col,ed_table_columns,ed_row,ed_table_rows,flag):
	degree_col,institute_col,board_col,year_col,marks_col="","","","",""
	##identify the column names
	for column in range(ed_col,ed_table_columns):
		cell_value = str(sheet.cell(ed_row+1,column).value)
		check_degree= re.search(r'(Degree|Course|Qualification|Qualified Exam.)', cell_value,re.IGNORECASE)
		check_institute= re.search(r'(Institute|College|School|Institution)', cell_value,re.IGNORECASE)
		check_board= re.search(r'(University|Board|Exam)', cell_value,re.IGNORECASE)
		check_year= re.search(r'(Year)', cell_value,re.IGNORECASE)
		check_marks= re.search(r'(Percentage|Marks|Percentile|Score|%)', cell_value,re.IGNORECASE)
		if check_degree:
			degree_col=column
		if check_institute:
			institute_col=column
		if check_board:
			board_col=column
		if check_year:
			year_col=column
		if check_marks:
			marks_col=column
	if flag==1:
		return degree_col
	if flag==2:
		return institute_col
	if flag==3:
		return board_col
	if flag==4:
		return year_col
	if flag==5:
		return marks_col


#read the column headers for education
def create_datatable (ed_col,ed_table_columns,ed_row,ed_table_rows)	:
	i=0
	list_master= KeywordsPG_SK
	list_master=list_master.reset_index()['Bag of words'].values.tolist()
	re_master1= '|'.join(list_master)
	list_master= re.compile('\\b'+'('+(re_master1)+')'+'\\b',re.M|re.I)

	list_graduate= KeywordsGrad_SK
	list_graduate=list_graduate.reset_index()['Bag of words'].values.tolist()
	re_master1='|'.join(list_graduate)
	list_graduate= re.compile('\\b'+'('+(re_master1)+')'+'\\b',re.M|re.I)

	list_SSC= KeywordsSSC
	list_SSC=list_SSC.reset_index()['Bag of words'].values.tolist()
	re_master1='|'.join(list_SSC)
	list_SSC= re.compile('\\b'+'('+(re_master1)+')'+'\\b',re.M|re.I)

	list_HSC= KeywordsHSC
	list_HSC=list_HSC.reset_index()['Bag of words'].values.tolist()
	re_master1='|'.join(list_HSC)
	list_HSC= re.compile('\\b'+'('+(re_master1)+')'+'\\b',re.M|re.I)


	df_column=["SSC","SSC_detail", "SSC_School","SSC_Board","SSC_Marks","SSC_Year","HSC","HSC_detail","HSC_School"
	,"HSC_Board","HSC_Marks","HSC_Year","Graduate","Graduate_detail","Graduate_School","Graduate_Board","Graduate_Marks","Graduate_Year","Post_Graduate","Post_Graduate_detail","Post_Graduate_School","Post_Graduate_Board","Post_Graduate_Marks","Post_Graduate_Year"]
	df= pd.DataFrame(columns= df_column)
	##check for content rowwise
	SSC,SSC_detail, SSC_School,SSC_Board,SSC_Marks,SSC_Year,HSC,HSC_detail,HSC_School,HSC_Board,HSC_Marks,HSC_Year,Graduate,Graduate_detail,Graduate_School,Graduate_Board,Graduate_Marks,Graduate_Year,Post_Graduate,Post_Graduate_detail,Post_Graduate_School,Post_Graduate_Board,Post_Graduate_Marks,Post_Graduate_Year="","","","","","","","","","","","","","","","","","","","","","","",""
	for row in range(ed_row+2, ed_table_rows):
		content_degree =str(sheet.cell(row,degree_col).value)
		content_degree= re.sub(r'['+'('+')'+'-'+']', ' ',content_degree)
		content_degree_master = list_master.search(content_degree)
		content_degree_graduate = list_graduate.search(content_degree)
		content_degree_hsc = list_HSC.search(content_degree)
		content_degree_ssc = list_SSC.search(content_degree)
		content_degree_master,content_degree_graduate,content_degree_hsc,content_degree_ssc
		if content_degree_master:
			Post_Graduate="Yes"
			Post_Graduate_detail= content_degree_master.group()
			if institute_col!="":
				Post_Graduate_School= str(sheet.cell(row,institute_col).value)
			if board_col!="":
				Post_Graduate_Board = str(sheet.cell(row,board_col).value)
			if marks_col!="":
				Post_Graduate_Marks = str(sheet.cell(row,marks_col).value)
			if year_col!="":
				Post_Graduate_Year = str(sheet.cell(row,year_col).value)


		if content_degree_graduate:
			Graduate="Yes"
			Graduate_detail= content_degree_graduate.group()
			if institute_col!="":
				Graduate_School= str(sheet.cell(row,institute_col).value)
			if board_col!="":
				Graduate_Board = str(sheet.cell(row,board_col).value)
			if marks_col!="":
				Graduate_Marks = str(sheet.cell(row,marks_col).value)
			if year_col!="":
				Graduate_Year = str(sheet.cell(row,year_col).value)

		if content_degree_ssc:
			SSC="Yes"
			SSC_detail= content_degree_ssc.group()
			if institute_col!="":
				SSC_School= str(sheet.cell(row,institute_col).value)
			if board_col!="":
				SSC_Board = str(sheet.cell(row,board_col).value)
			if marks_col!="":
				SSC_Marks = str(sheet.cell(row,marks_col).value)
			if year_col!="":
				SSC_Year = str(sheet.cell(row,year_col).value)

		if content_degree_hsc:
			HSC="Yes"
			HSC_detail= content_degree_hsc.group()
			if institute_col!="":
				HSC_School= str(sheet.cell(row,institute_col).value)
			if board_col!="":
				HSC_Board = str(sheet.cell(row,board_col).value)
			if marks_col!="":
				HSC_Marks = str(sheet.cell(row,marks_col).value)
			if year_col!="":
				HSC_Year = str(sheet.cell(row,year_col).value)

	row_detail = [SSC,SSC_detail, SSC_School,SSC_Board,SSC_Marks,SSC_Year,HSC,HSC_detail,HSC_School,HSC_Board,HSC_Marks,HSC_Year,Graduate,Graduate_detail,Graduate_School,Graduate_Board,Graduate_Marks,Graduate_Year,Post_Graduate,Post_Graduate_detail,Post_Graduate_School,Post_Graduate_Board,Post_Graduate_Marks,Post_Graduate_Year]
	df.loc[1]=row_detail
	#i=1+1
	return(df)


##fuzzy wuzzy used currently
def fuzzywuzzy_check2(string_to_search,degree,term):
	if (degree=="Yes"):
		curr_cv= string_to_search
		degree_pos=curr_cv.find(term)
		curr_cv_degree=curr_cv[max(0,degree_pos-200):min(len(curr_cv),degree_pos+200)]
		Univ_list['Score']=""
		for j in range(0,len(Univ_list['Univ_Lower'])):
			Univ_list['Score'][j]=fuzz.partial_ratio(curr_cv_degree.lower(),Univ_list['Univ_Lower'][j].lower())
		match_grad_univ_score= max(Univ_list['Score'])
		max_id= Univ_list["Score"].idxmax()
		match_grad_univ=Univ_list["Univ_Lower"].loc[max_id]
		output=[match_grad_univ_score,match_grad_univ,curr_cv_degree.lower()]
		return output
	else:
		return None


##Banking non- banking function
def banking(string_to_search):
	keywords= ["bank","banking"]
	for i in range(0,len(keywords)-1):
		try:
			result = re.findall(keywords[i], string_to_search,re.IGNORECASE)
			if result:
				return "Yes"
				continue
			else:
				None
		except:
			None



##Sales/non- Sales function
def Sales(string_to_search):
	keywords= ["sale","sales","selling"]
	for i in range(0,len(keywords)-1):
		try:
			result = re.findall(keywords[i], string_to_search,re.IGNORECASE)
			if result:
				return "Yes"
				continue
			else:
				None
		except:
			None




##Parttime
def Partime(string_to_search,type):
	keywords = ["Part","Distance"]
	result = []
	parttime_pos = 0
	if(type ==" PG" and Is_Post_Graduate == "Yes"):
		parttime_pos = string_to_search.find(Post_Graduate_details_key)
	else:
		None
	if(type == "G" and Is_Graduate == "Yes"):
		parttime_pos = string_to_search.find(Graduate_details_key)
	else:
		None
	curr_cv = string_to_search
	curr_cv_parttime=curr_cv[max(0,parttime_pos-100):max(len(curr_cv),parttime_pos+100)]
	parttime="No"
	if parttime_pos>0:
		try:
			# search for bank
			for k in range(0,len(keywords)-1):
				pos_keyword=curr_cv_exp.find(keywords[i])
				if pos_keyword>0:
					parttime="Yes"
			return parttime
		except:
			return parttime
	else:
		return parttime



def Experience(string_to_search, Is_Post_Graduate, YOB):

	keywords=["Employment detail","Occupation","working with","worked with","Work at","Worked as","Work Exposure","Employed with","Work profile","Company profile","Employment History","Experience"]
	exp = 0
	for i in range(0,len(keywords)):
		exp_pos = 0
		try:
			# m=re.search(keywords[i], string_to_search,re.IGNORECASE)
			for m in re.finditer(keywords[i], string_to_search,re.IGNORECASE):
				exp_pos = m.end()

				if exp_pos>0:
					if(i==11): # only for experience keyword
						curr_cv=string_to_search
						curr_cv_exp_before=curr_cv[(exp_pos-150):(exp_pos+10)]
						regular_expression = re.compile(r'(?:objective)', re.M|re.I)
						result = re.findall(regular_expression, curr_cv_exp_before)

						curr_cv_exp_before=curr_cv[(exp_pos-20):(exp_pos+10)]
						regular_expression = re.compile(r'(?:technical|education|project)', re.M|re.I)
						result1 = re.findall(regular_expression, curr_cv_exp_before)

						curr_cv_exp_after=curr_cv[exp_pos:(exp_pos+100)]
						regular_expression = re.compile(r'(?:articleship|internship|apprentice)', re.M|re.I)
						result2 = re.findall(regular_expression, curr_cv_exp_after)


						if (len(result)>0 or len(result1)>0 or len(result2)>0):
							exp_pos=0
							continue
						else:
							break
							break
					else:
						break
						break
				else:
					None
		except:
			exp=0



	if exp_pos>0 and YOB:
		regular_expression = re.compile(r'(?:till date|till-date|Present)', re.M|re.I)
		curr_cv = string_to_search
		curr_cv_exp=curr_cv[exp_pos:min(len(curr_cv),exp_pos+200)]
		result = re.findall(regular_expression, curr_cv_exp)
		if result:
			max_year = int(time.strftime("%Y"))
		try:
			regular_expression = re.compile(r'(\d{4})', re.M|re.I)
			result = re.findall(regular_expression, curr_cv_exp)
			if max_year != int(time.strftime("%Y")):
				max_year = max(result)

			min_year= int(min(result))

			if(max_year)<int(time.strftime("%Y"))-2:
				max_year = int(time.strftime("%Y"))-2
			if(Is_Post_Graduate == "Yes" and (min_year-YOB)<24):
				min_year = YOB + 24
			if(Is_Post_Graduate == "No" and (min_year-YOB)<22):
				min_year = YOB + 22

			exp = max_year - min_year + 1
		except:
			if Is_Post_Graduate == "Yes":
				exp = int(time.strftime("%Y")) - YOB - 24
			else:
				exp = int(time.strftime("%Y")) - YOB - 22
		if(exp <= 0):
			exp = 1
		try:
			m = re.search('fresher', curr_cv_exp, re.IGNORECASE)
			fresher = m.end()
		except:
			fresher = 0
		if(fresher > 0):
			exp = 0
	else:
		exp = 0
	
	if exp > 30:
		exp = 0
	
	return exp


## Convert PDF to text, without logs (specifically for getMarksForGrad())
def convert_pdf_to_text_no_logs(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

"""
Input: filepath
Output: marks value
Logic: Using PDFMiner and fun is_Grad,
1. find degree and its y0 value
2. all numbers (2 digits, with/without decimals and not years), with their respective y0 value
3. find difference of y0 of each number with y0 of degree
4. the minimum value found, should be returned as the marks
Note: Regex for marks does not pick "Pass/Appear/Distinction". It only works for marks (numbers), effectively discards year values and picks CGPA as well
"""
def getMarksForGrad(filepath):
	# Open a file to parse in PDFMiner
	fp = open(filepath, 'rb')
	# Use custom global function convert_pdf_to_text, to convert entire pdf to string and run bag of words over it
	degreeCheck = fun_isGrad(convert_pdf_to_text_no_logs(filepath).replace("\n", " "))
	# Create a PDF parser object associated with the file object.
	parser = PDFParser(fp)
	# Create a PDF document object that stores the document structure.
	# Not supplying any password for initialization
	doc = PDFDocument(parser)
	# Create a PDF resource manager object that stores shared resources.
	rsrcmgr = PDFResourceManager()
	# Set parameters for analysis
	laparams = LAParams()
	# Create a PDF device object.
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	# Create a PDF interpreter object
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	# Process each page contained in the document.
	# for page in PDFPage.create_pages(doc):

	# Initialize lists, variables (numbers will contain the numbers that are found in CV on same page as regex || yValues will contain their respective y0 values || found is a flag, by default false, that will change to true if the regex matches || marks are initialized at 0)
	numbers = []
	yValues = []
	found = False
	marks = ""

	for pageNumber, page in enumerate(PDFPage.create_pages(doc)):
		interpreter.process_page(page)
		# receive the LTPage object for the page.
		layout = device.get_result()
		# For the degree that matches, find its y0 & y1
		for lt_obj in layout:
			try:
				# Remove leading/lagging spaces of PDFMiner and match with degreeCheck (remove first and last character)
				if(degreeCheck[1][1:-1] in lt_obj.get_text()):
					# Get y0, y1 values if substring exists in string, set flag found = True, break out of inner for loop
					y0 = lt_obj.y0
					y1 = lt_obj.y1
					# Change the flag to True and break from the inner for loop
					found = True
					break
			except:
				continue
		#Only if a value has been found# Find the list of numbers that match regex, as well as their y0 values
		if(found):
			for lt_obj in layout:
				# Check if the PDFMiner Object has any text inside
				try:
					if(lt_obj.get_text()):
						# Regex to find a number with/without decimals. perc will return a list, either empty, or with the regex match value
						# perc = re.findall(r'\d{1,2}[\.]?\d{0,2}', lt_obj.get_text())
						# perc = re.findall(r'[0-9\.]+', lt_obj.get_text())
						perc = re.findall(r'\d+\.{0,1}\d*', lt_obj.get_text())
						# Check that regex is not empty
						if(len(perc)>0):
							for i in range(0, len(perc)):
								# Check that value of regex is not either marks between 30 and 99 or CGPA between 4 and 10 (it will skip years)
								if(((float(perc[i])<=99) & (float(perc[i])>30))|((float(perc[i])<10) & (float(perc[i])>=4))):
									# Append the numbers and their respective y0 Values
									numbers.extend([perc[i]])
									yValues.append(lt_obj.y0)
				except:
					continue
		try:
			for i in range(0, len(numbers)):
				# Find the least difference between each list value and y0
				yValues[i] = abs(yValues[i] - y0)
		except:
			pass
		break
	# If a regex match was found and y0 values are available
	if((found == True) & (len(yValues) > 0)):
		# get the least absolute value from the list of yValues
		minValue = min(map(abs, yValues))
		# Assume a threshold. If the minValue is within the threshold (meaning, it is nearby to the regex matched
		if(minValue <= 50):
			# then, capture its index value (location in the yValues list)
			ind = yValues.index(minValue)
			# save the marks for that index position from the numbers list
			marks = numbers[ind]
		else:
			marks = ""
	
	return marks