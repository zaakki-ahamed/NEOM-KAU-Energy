import pandas as pd
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import numpy as np

# load dataset
dataframe = pd.read_csv("calculated_dataset_solar.csv", sep=',',low_memory=False)

drop_cols = ['Site','Date','power_out_farm_kwh']

dataframe.drop(drop_cols, axis = 1, inplace=True) 

#dataframe = dataframe.reset_index()

#dataframe['Date'] =  pd.to_datetime(dataframe['Date'], format="%Y-%m-%d %H:%M:%S")

#dataframe.set_index('Date', drop=False, inplace=True)

#print(pd.get_dummies(dataframe['wind_type'], prefix='wind_type'))
#print("")
#print(pd.get_dummies(dataframe['sky_cavok'], prefix='sky_cavok'))
#print("")
#dataframe = pd.concat([dataframe,pd.get_dummies(dataframe['wind_type'], prefix='wind_type',dummy_na=True)],axis=1).drop(['wind_type'],axis=1)

#dataframe = pd.concat([dataframe,pd.get_dummies(dataframe['sky_cavok'], prefix='sky_cavok',dummy_na=True)],axis=1).drop(['sky_cavok'],axis=1) """

print(dataframe.info())

print("")
print("Null Info")
print(dataframe.isnull().sum())
print("")

dataframe = np.round(dataframe)

print(np.any(np.isnan(dataframe)))
print(np.all(np.isfinite(dataframe)))

dataframe.fillna(0, inplace=True)

dataframe.replace([np.inf, -np.inf], 0, inplace=True)

#for idx, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0]):
#    dataframe.at[idx,'power_out_kw'] = dataframe.at[idx,'power_out_kw'].round()

array = dataframe.values
X = array[:,0:14]
Y = array[:,14]

print(Y)

# prepare configuration for cross validation test harness
seed = 7
# prepare models
from sklearn import linear_model
from sklearn import svm

models = []
models.append(('LR', LogisticRegression(multi_class='auto',solver='lbfgs')))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))

#models.append(('SVM',svm.SVR()))
#models.append(('SGDRegressor',linear_model.SGDRegressor()))
#models.append(('BayesianRidge',linear_model.BayesianRidge()))
#models.append(('LassoLars',linear_model.LassoLars()))
#models.append(('ARDRegression',linear_model.ARDRegression()))
#models.append(('PassiveAggressiveRegressor',linear_model.PassiveAggressiveRegressor()))
#models.append(('TheilSenRegressor',linear_model.TheilSenRegressor()))
#models.append(('LinearRegression',linear_model.LinearRegression()))

#models.append(('SVM', SVC))

# evaluate each model in turn
results = []
names = []
scoring = 'accuracy'

for name, model in models:
	kfold = model_selection.KFold(n_splits=10, random_state=seed)
	print(name)
	cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
	results.append(cv_results)
	print(cv_results)
	names.append(name)
	msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
	print(msg)

# boxplot algorithm comparison
fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
plt.show()
