mport pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier

#load .csv into dataframe
df = pd.read_csv("./clean_loan_training.csv",low_memory=False)

#delete features that are not useful / not possible to encode in one hot encoding
del df['id']
del df['member_id']
del df['emp_title']
del df['issue_d']
del df['url']
del df['desc']
del df['title']
del df['last_pymnt_d']
del df['next_pymnt_d']
del df['last_credit_pull_d']
#below are removed because they are not available in the lending club api
del df['pymnt_plan']
del df['out_prncp']
del df['out_prncp_inv']
del df['total_pymnt']
del df['total_pymnt_inv']
del df['total_rec_prncp']
del df['total_rec_int']
del df['total_rec_late_fee']
del df['recoveries']
del df['collection_recovery_fee']

#load target data
target = list(csv.reader(open('./clean_loan_target.csv', 'rU')))
for n in range(len(target)):
    if target[n][0] == 'Late (31-120 days)':
        target[n][0] = 0
    elif target[n][0] == 'Charged Off':
        target[n][0] = 0
    elif target[n][0] == 'Late (16-30 days)':
        target[n][0] = 0
    else:
        target[n][0] = 1
target = np.array([n[0] for n in target])

#encode training data using one hot encoding for categorical features
vec = DictVectorizer()
loan_training_data = df.T.to_dict().values()
training_data = vec.fit_transform(loan_training_data).toarray()

#For whatever reason, the vectorizor might produce feature vectors with NaN...remove those data.  Only 116 when I counted.
indexOfDataToDelete=[]
for n in range(len(training_data)):
    x = np.sum(training_data[n])
    if np.isnan(x) or np.isinf(x):
        indexOfDataToDelete.append(n)
target = np.delete(target, indexOfDataToDelete)
training_data = np.delete(training_data,indexOfDataToDelete,0)

#Split data into training and test data
training_data, test_data, training_target, test_target = train_test_split(training_data, target)

#train random forest classifier 
n_est = 400
clf = RandomForestClassifier(n_est, n_jobs=7)
clf.fit(training_data, training_target)

def percentage_false_positive(x, y):
    positive_predictions = 0.0
    false_positive_predictions = 0.0
    for n in range(len(x)):
        if x[n] == 1:
            positive_predictions += 1
            if y[n] !=1:
                false_positive_predictions +=1
                
    return false_positive_predictions / positive_predictions

def percentage_false_negative(x, y):
    negative_predictions = 0.0
    false_negative_predictions = 0.0
    for n in range(len(x)):
        if x[n] == 0:
            negative_predictions += 1
            if y[n] !=0:
                false_negative_predictions +=1
                
    return false_negative_predictions / negative_predictions

predicted = clf.predict(test_data)

print(percentage_false_positive(predicted, test_target))
print(percentage_false_negative(predicted, test_target))

