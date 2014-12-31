import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import zero_one_loss

import tfidf

#load raw training data from csv
df = pd.read_csv("./clean_loan_training.csv",low_memory=False)
del df['id']
del df['member_id']
del df['emp_title']
del df['issue_d']
del df['url']
del df['title']
del df['last_pymnt_d']
del df['next_pymnt_d']
del df['last_credit_pull_d']
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

tf_idf, columns = tfidf.tfidf(df['desc'])
del df['desc']

print df.shape
print tf_idf.shape

print type(tf_idf)

load_training_data = df.append(pd.SparseDataFrame(data=tf_idf.toarray(), columns=columns)).T.to_dict().values()

#load target data.  For now we naievely categorize anything late as a default
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

#Vectorize the raw training data -- take String features and encode them with one hot encoding
vec = DictVectorizer()
training_data = vec.fit_transform(loan_training_data).toarray()

#For whatever reason, the vectorizor might produce feature vectors with NaN...remove those data.  Only 116 when I counted.
indexOfDataToDelete=[]
for n in range(len(training_data)):
    x = np.sum(training_data[n])
    if np.isnan(x) or np.isinf(x):
        indexOfDataToDelete.append(n)
target = np.delete(target, indexOfDataToDelete)
training_data = np.delete(training_data,indexOfDataToDelete,0)

#Split the data into training and test sets
training_data, test_data, training_target, test_target = train_test_split(training_data, target)

#Finally train the model
clf = LogisticRegression()
clf.fit(training_data, training_target)

#Predict the using test data
predicted = clf.predict(test_data)

#Print zero one loss score
print(zero_one_loss(predicted, test_target))
