import os
import os.path
import re
import pandas as pd
from tabula import read_pdf
from pyPdf import PdfFileReader

# pathOfPdfFile = "D:\WinPython-64bit-2.7.6.4\PDF to Table\patel.pdf"
# pathOfPdfFile = "D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\Anup  Deb.pdf"

filesname = []
for root, directories, files in os.walk("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF"):
	for filename in files:
		# Join the two strings in order to form the full filepath.
		filepath = os.path.join(root, filename)
		filesname.append(filepath)

		
"""
listOfPdfs (pathOfPdfFile):
Input - filename path
Output - list of tables
Read a pdf, from a given file path. Count the number of pages and search for a table on each page
"""
def listOfPdfs (pathOfPdfFile):
	# Open PDF File to count number of pages
	pdf = PdfFileReader(open(pathOfPdfFile,'rb'))
	pageCount = pdf.getNumPages()
	
	tables = []
	
	for i in range(1, pageCount):
		print "Reading pg" + str(i)
		# Read PDF File
		try:
			df = read_pdf(pathOfPdfFile, pages = str(i))
			print df
			df = cleanDataFrame(df)
			print "cleanDataFrame ==========>>> \n",df
			if(type(df) != "NoneType"):
				tables.extend([df])
		except:
			continue
	
	return tables
	
	"""
	Note :: tables is a list of dataframes
	"""


"""
cleanDataFrame(df):
Input - single table
Output - single table, with cleaned data
Clean data, by merging with previous rows' cells
"""	
def cleanDataFrame(df):
	noOfColumns = df.shape[1]
	counter = 0

	# Check first row for NA, if NA exists in any cell, merge contents of each cell with the column name and drop row 0
	if(df.isnull().values[0].any() == True):
		for column in range(0, noOfColumns):
			if (pd.isnull(df.iloc[0][column]) != True):
				df = df.rename(columns = {df.columns[column]:df.columns[column] + df.iloc[0][column]})
		
		df = df.drop(df.index[[0]])
	
	noOfRows = df.shape[0]
	cleanTable = df[0:0]

	ix = 1	
	# Iterate through each row
	for row in range(0, noOfRows):
		# Check for the first and second rows only. If R1C1 - R1C2 / R2C1 - R2C2 have NaN, then merge the cell contents with the header
		if((row <= ix) & (df.isnull().values[row][0] == True) & (df.isnull().values[row][1] == True)):
			for column in range(0, noOfColumns):
				# Check if not nan value (nan value is always float) for current and previous row cell, then change the previous cell value
				if((type(df.iloc[row][column]) != float) & (type(df.iloc[row-ix][column]) != float)):
					# df = df.rename(columns = {df.columns[column]:df.columns[column] + df.iloc[row][column]})
					df.iloc[row-ix][column] = df.iloc[row-ix][column] + df.iloc[row][column]
					ix = ix + 1
					# cleanTable = cleanTable.append(df.ffill().iloc[[row]])
					# cleanTable.iloc[counter][column] = cleanTable.iloc[counter][column] + df.iloc[row][column]
			cleanTable = df[0:0]
			
		else:
			# Check if the row has any NaN.If it doesn't, then the row can be skipped
			if (df.isnull().values[row].any() == True):
				# Iterate through each column of the row
				for column in range(0, noOfColumns):
					# Check that the existing cell value is not NaN, but a real value
					if (pd.isnull(df.iloc[row][column]) != True):
						# Check if cell type is not float (NaN is float) for current and row-1 cells
						if((type(df.iloc[row - 1][column]) != float) & (type(df.iloc[row][column]) != float)):
							# Previous row cell is equal to previous row cell + existing cell value only if both are not nan (prev line if statement)
							df.iloc[row-1][column] = df.iloc[row-1][column] + df.iloc[row][column]
					else:
						print "Inner IF", row, " ",column
			else:
				print "Outer IF"

	# df = df.dropna()
	return df

	
"""
readData (df):
Input - list of tables
Output - list containing degree that matches, along with respective Marks/% of that degree/row
Match bag of words, with each table and rename the columns that contain "Degree, Year and Marks". Return only this table (with renamed columns)
Match bag of words for Graduate, find row, and from Marks column, return value
"""	
def readData (df):

	"""
	Remember :: DF is a list, not a dataframe, in this function. You must therefore loop through the list, to check each table
	"""
	
	bowEducation = "Exam|Education|Qualification|Academic|ACADEMIC|Degree|Qualifications|Course"
	bowMarks = "Percentage|Marks|Percentile|Percent|Score|%"
	bowYear = "Year|Years|YEAR|YEARS|Year of Passing"

	# Rename columns matching bag of words to identify the columns that are needed
	for table in range(0, len(df)):
		for columnName in range(0, df[table].shape[1]):
			if( re.search(r''+ bowEducation +'', df[table].columns[columnName],re.IGNORECASE) ):
				df[table] = df[table].rename(columns = {df[table].columns[columnName]: "Degree"})
			elif ( re.search(r''+ bowMarks +'', df[table].columns[columnName],re.IGNORECASE) ):
				df[table] = df[table].rename(columns = {df[table].columns[columnName]: "Marks"})
			elif ( re.search(r''+ bowYear +'', df[table].columns[columnName],re.IGNORECASE) ):
				df[table] = df[table].rename(columns = {df[table].columns[columnName]: "Year"})
	
	# flag = 0, means no education table found
	# flag = 1, means education table has been found, by matching the presence of Degree column
	flag = 0
	
	# Iterate through each table in the list of tables
	for table in range(0, len(df)):
		# Iterate through each column of a table
		for columnName in range(0, df[table].shape[1]):
			# If the column name matches the value "Degree", set flag = 1, and store that table into a separate object 'eduTable'
			if (df[table].columns[columnName] == "Degree"):
				# Set flag as 1 to indicate that education Table is available
				# Save the columnNumberDegree which has degree. It will be useful for indexing later
				# Store the df[table] as a separate eduTable, to be used further
				flag = 1
				columnNumberDegree = columnName
				eduTable = df[table]
			elif (df[table].columns[columnName] == "Marks"):
				columnNumberMarks = columnName
	
	# If eduTable exists, then use regex to find value of marks
	if (flag == 1):
		x = findMarks(eduTable, columnNumberDegree, columnNumberMarks)
		return x
	elif (flag == 0):
		return (["", ""])

"""
findMarks(eduTable):
Input - single table containing education table values
Output - list containing degree that matches, along with respective Marks/% of that degree/row
Match bag of words, with each row in the Degree column. For the row that matches the bag of words, find the value of the same row from the Marks column
"""	
def findMarks(eduTable, columnNumberDegree, columnNumberMarks):
	
	KeywordsGrad = pd.read_csv("D:\WinPython-64bit-2.7.6.4\PDF to Table\BachelorsBOW.csv")
	
	# Iterate through each cell in the Degree column
	for rowNumber in range(0, eduTable.shape[0]):
		# Only if the cell value is not NaN, then proceed
		if(pd.isnull(eduTable.values[rowNumber][columnNumberDegree]) == False):
			# Check which word matches the bowEducation
			degreeCheck = fun_isGrad(" " + eduTable.values[rowNumber][columnNumberDegree]+ " ")
		# if function isGrad returns a yes, save the degree, else declare as empty degree
			if (degreeCheck[0] == "Yes"):
				# Use strip to remove leading and trailing spaces
				degree = degreeCheck[1].strip()
				marks = eduTable.values[rowNumber][columnNumberMarks]
				print "degree :::: ", degree, "marks ::: ", marks
				return [degree, marks]
		
	# If no degree is found, then return empty list and exit the function
	return ["", ""]

	

############################################################
######################## PDF MINER #########################
############################################################	

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator, TextConverter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
from cStringIO import StringIO
import re

def parse_layout(layout):
    """Function to recursively parse the layout tree."""
    for lt_obj in layout:
        print(lt_obj.__class__.__name__)
        print(lt_obj.bbox)
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            print(lt_obj.get_text())
        elif isinstance(lt_obj, LTFigure):
            parse_layout(lt_obj)  # Recursive

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

############################################################
######################## PDF MINER #########################
############################################################	
	
	
	
	

############################################################
################### FROM FUNCTION MASTER ###################
############################################################

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

############################################################
################### FROM FUNCTION MASTER ###################
############################################################
				
				
				

############################################################
#######################  TRIAL CODE  #######################
############################################################

for file in range(0, len(filesname)):
	print file, filesname[file].replace(".pdf", "").replace("D:\WinPython-64bit-2.7.6.4\PDF to Table\CV\\","")
	listOfPdfs(filesname[file])
	
# Iterate through each row
for row in range(0, noOfRows):
# Iterate through each column
    for column in range(0, noOfColumns):
		# Check for NaN in each row
		if(df.isnull().values[row].any() == True):
			print "YES, na exists at ", str(df.iloc[row][column])
			# Check if cell has nan, if yes, then replace it
			# if (math.isnan(df.iloc[row][column])):
				# df1 = df.fillna("")
				
		else:
			# cleanTable = df.bfill().iloc[[row]]
			print "Nopes"

	cleanTable = cleanTable.append(df.bfill().iloc[[row]])

for index in df.itertuples():
    print index

for index, row in df.iterrows():
    print index, row

# If column with name 1.Degree matches with B.o.w ProductionEngineering, then return the third column in the same row, to get marks value
print (a[0].loc[a[0]['1.Degree'] == '(ProductionEngineering)']).iloc[0][3]

# Reuse isGrad function
for i in range(0, eduTable.shape[0]):
    print fun_isGrad(eduTable.values[i][columnNumberDegree])

# Reading with Area and spreadsheet options
df = read_pdf("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\Abhinandan Prakash Mane-7757975453.pdf", pages = "1", area = [135.0,75.0,421.875,538.59], spreadsheet=True)
df = read_pdf("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\Anup  Deb.pdf", pages = "3", guess=True, area = [233.004,31.0,300.324,561.91], spreadsheet=True)
df = read_pdf("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\Bittu  Kumar-9801680800.pdf", pages = "2", guess=True, area = [34.999,71.0,102.319,539.945], spreadsheet=True)
df = read_pdf("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\CMA  Anuj Jain.pdf", pages = "1", guess=True, area = [281.0,71.0,385.04,549.89], spreadsheet=True)
df = read_pdf("D:\WinPython-64bit-2.7.6.4\PDF to Table\Tabular CV PDF\DARSHAK  PATHAK-7383059221.pdf", pages = "1", guess=True, area = [468.0,53.0,743.4,554.075], spreadsheet=True)

http://stackoverflow.com/questions/25248140/how-does-one-obtain-the-location-of-text-in-a-pdf-with-pdfminer
https://euske.github.io/pdfminer/programming.html

for pageNumber, page in enumerate(PDFPage.create_pages(doc)):
    interpreter.process_page(page)
	# receive the LTPage object for the page.
    layout = device.get_result()

    for lt_obj in layout:
        try:
			# Remove leading/lagging spaces of PDFMiner and match with degreeCheck (remove first and last character)
            if (lt_obj.get_text().strip() == degreeCheck[1][1:-1]):
                print lt_obj.get_text(), lt_obj.bbox
        except:
            continue
############################################################
#######################  TRIAL CODE  #######################
############################################################