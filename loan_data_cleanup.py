import sys
from csv import reader
from csv import writer
import datetime

monthDict ={
	"Jan":"01",
	"Feb":"02",
	"Mar":"03",
	"Apr":"04",
	"May":"05",
	"Jun":"06",
	"Jul":"07",
	"Aug":"08",
	"Sep":"09",
	"Oct":"10",
	"Nov":"11",
	"Dec":"12"}

columnNames = {
'id':0,
'member_id':1,
'loan_amnt':2,
'funded_amnt':3,
'funded_amnt_inv':4,
'term':5,
'int_rate':6,
'installment':7,
'grade':8,
'sub_grade':9,
'emp_title':10,
'emp_length':11,
'home_ownership':12,
'annual_inc':13,
'is_inc_v':14,
'issue_d':15,
'loan_status':16,
'pymnt_plan':17,
'url':18,
'desc':19,
'purpose':20,
'title':21,
'zip_code':22,
'addr_state':23,
'dti':24,
'delinq_2yrs':25,
'earliest_cr_line':26,
'inq_last_6mths':27,
'mths_since_last_delinq':28,
'mths_since_last_record':29,
'open_acc':30,
'pub_rec':31,
'revol_bal':32,
'revol_util':33,
'total_acc':34,
'initial_list_status':35,
'out_prncp':36,
'out_prncp_inv':37,
'total_pymnt':38,
'total_pymnt_inv':39,
'total_rec_prncp':40,
'total_rec_int':41,
'total_rec_late_fee':42,
'recoveries':43,
'collection_recovery_fee':44,
'last_pymnt_d':45,
'last_pymnt_amnt':46,
'next_pymnt_d':47,
'last_credit_pull_d':48,
'collections_12_mths_ex_med':49,
'mths_since_last_major_derog':50,
'policy_code':51,
}

NotNullableFeaturesList=[
"annual_inc",
"dti",
"delinq_2yrs",
"open_acc",
"pub_rec",
"total_acc"
]

removeColumnsList=[
]

def getCreditHistoryAgeMonths(start, end):
	#if beginning if credit history doesn't exist then age is 0
	if len(start) == 0:
		return 0
	
	tokens = start.split("-")
	startDate = datetime.datetime.strptime(monthDict[tokens[0]] + tokens[1], "%m%Y").date()
	tokens = end.split("-")
        endDate = datetime.datetime.strptime(monthDict[tokens[0]] + tokens[1], "%m%Y").date()
	timeDelta = endDate - startDate
	creditHistoryDays = timeDelta.days
	return creditHistoryDays / 30

def isMissingData(line):
	for column in NotNullableFeaturesList:
 		if len(line[columnNames[column]]) == 0:
			return True
	return False

f = open("./special_chars_removed_loan_stats.csv")
data = []
readerIterable = reader(f)

#get the header and add an additional column which we're appending to the data set
header = next(readerIterable, None)
header.append("credit_history_age_months")

#Remove the column loan_status because we will put that in a separate target file
header.pop(columnNames['loan_status'])

for line in readerIterable:
	if len(line) == 52:

		#Don't include headers.  The file is cated over multiple files so there are multiple headers in the middle
		if line[0] == "id":
			continue

		#check data has all necessary fields
		if isMissingData(line):
			continue

		#not sure if this is "bad" data. seems like the loan_status is just overloaded with prefix.  Remove here but consider removing all data like this
		if "Does not meet the credit policy.  Status:" in line[columnNames["loan_status"]] :
			line[columnNames["loan_status"]] = line[columnNames["loan_status"]][len("Does not meet the credit policy.  Status:"):]

		#convert interest rate percentages to 0 to 1 scale
	        line[columnNames["int_rate"]] = float(line[columnNames["int_rate"]].strip("%")) / 100
		#convert revolving credit utilization to 0 to 1 scale.  if non exists assume it is 100% utilization (typically the revolving balance is 0)
		if len(line[columnNames["revol_util"]]) == 0:
			line[columnNames["revol_util"]] = 1
		else:
			line[columnNames["revol_util"]] = float(line[columnNames["revol_util"]].strip("%")) / 100
	
		#Don't know what to do with missing data for this yet so just making it a binary thing.
		if len(line[columnNames["mths_since_last_delinq"]]) == 0:
			line[columnNames["mths_since_last_delinq"]] = 0 
		else:
			line[columnNames["mths_since_last_delinq"]] = 1

		if len(line[columnNames["mths_since_last_record"]]) == 0:
			line[columnNames["mths_since_last_record"]] = 0
		else:
			line[columnNames["mths_since_last_record"]] = 1

		if len(line[columnNames["mths_since_last_major_derog"]]) == 0:
			line[columnNames["mths_since_last_major_derog"]] = 0
		else:
			line[columnNames["mths_since_last_major_derog"]] = 1

		if len(line[columnNames["inq_last_6mths"]]) == 0:
			line[columnNames["inq_last_6mths"]] = 0
		else:
			line[columnNames["inq_last_6mths"]] = 1

		#Add this new field to the list of features.
		line.append(getCreditHistoryAgeMonths(line[columnNames["earliest_cr_line"]], line[columnNames["issue_d"]]))
		data.append(line)

#CSV for training data 
training = writer(open("./clean_loan_training.csv","wb"))

#CSV for target data
target = writer(open("./clean_loan_target.csv", "wb"))

training.writerow(header)

for datum in data:
	trainingRow = []
	targetRow = []
	for n in range(len(datum)):
		if n != columnNames['loan_status']:
			trainingRow.append(datum[n])
		else:
			targetRow.append(datum[n])
	training.writerow(trainingRow)
	target.writerow(targetRow)
