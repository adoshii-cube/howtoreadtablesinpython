#Today's date for filename
date = time.strftime("%Y%m%d")

Age,Is_Post_Graduate,Is_Graduate,Is_Bank,Is_sales,Years_Experience,Marks_Category="","","","","","",""

df= pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\' + date + '_output.csv')
df["Avg_marks"]= df[['Graduate_percentage', 'PG_percentage']].mean(axis=1)
df["Marks_Category"]= "Less than 60%"
df["Marks_Category"][df["Avg_marks"]>60]="Equal & Greater than 60%"


df.Age[pd.isnull(df.Age)]=0
df[['Age']]=df[['Age']].astype(int)
df[['Age']]=df[['Age']].astype(str)
df["Role"]=""
df["Score"]=""


# To check BE BTECH

df['Is_Btech'] = np.where(df['Graduate_details'].isin(["BE","BTECH"]), 'Yes', 'No',)

# To ME BE MTECH

df['Is_Mtech'] = np.where(df['Post_Graduate_details'].isin(["ME","MTECH"]), 'Yes', 'No',)

# Assume PG to be Grad
df['Is_Graduate'][df['Is_Post_Graduate']=="Yes"]="Yes"




weights= pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Rule_book\\20170207_Weightage.csv')
rules= pd.read_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\Rule_book\\20170316_RulesV2.csv')
rules= rules[rules.columns[0:7]]

desigs= ["BDE","CSO_OFF","CSO_AM","RM-AM"]
category= ["Age","Is_Bank","Is_sales","Marks_Category","Is_Graduate","Is_Post_Graduate","Years_Experience","Is_Btech","Is_Mtech"]

#len(df.axes[0])-1
for k in range(0,len(df.axes[0])-1):
	output = pd.DataFrame()
	df_1= df.loc[k]
	for j in range(0,(len(category))):
		cat = rules[rules["Category"]== category[j]]
		weightage= int(weights[weights["Column"]==category[j]]["Weights"])
		cat= cat[cat["Criterion"]== str(df_1[category[j]])]
		cat[desigs]= cat[desigs]* weightage
		output= output.append(cat)

	output= output[desigs]
	
	# if(df_1[category[5]]=="Yes"): # is post grad
		# output= output[["CSO_AM","RM-AM"]]
	# else:
		# output= output[["BDE","CSO_OFF"]]
	
	output=output.transpose()
	output["Total"]= output.sum(axis=1)
	role1= max(output[["Total"]].idxmax())
	score= max(output["Total"])
	df.Role.loc[k]=role1
	df.Score.loc[k]=score
	
df.Role[df.Age=='0']="Uncategorized"

	
df.to_csv('D:\\WinPython-64bit-2.7.6.4\\PDF to Table\\' + date + '_Output_Final.csv')