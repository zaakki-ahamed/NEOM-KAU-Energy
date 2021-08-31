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
def movecol(df, cols_to_move=[], ref_col='', place=''):
    
    cols = df.columns.tolist()
    if place == 'After':
        seg1 = cols[:list(cols).index(ref_col) + 1]
        seg2 = cols_to_move
    if place == 'Before':
        seg1 = cols[:list(cols).index(ref_col)]
        seg2 = cols_to_move + [ref_col]
    
    seg1 = [i for i in seg1 if i not in seg2]
    seg3 = [i for i in cols if i not in seg1 + seg2]
    
    return(df[seg1 + seg2 + seg3])

# load dataset
dataframe = pd.read_csv("Saudi_Wind_power_calculatated_data.csv", sep=',',low_memory=False)

drop_cols = ['observation_date','station_id','station_name','station_country','wind_direction_angle_units','wind_speed_rate_units',
'sky_ceiling_height_units','sky_ceiling_determination','visibility_distance_units','visibility_variability','air_temperature_units',
'air_temperature_dew_point_units','atmospheric_sea_level_pressure_units']

dataframe.drop(drop_cols, axis = 1, inplace=True) 

#dataframe['observation_date'] =  pd.to_datetime(dataframe['observation_date'], format="%Y-%m-%d %H:%M:%S")

#dataframe.set_index('observation_date', drop=False, inplace=True)

print(pd.get_dummies(dataframe['wind_type'], prefix='wind_type'))
print("")
print(pd.get_dummies(dataframe['sky_cavok'], prefix='sky_cavok'))
print("")

dataframe = pd.concat([dataframe,pd.get_dummies(dataframe['wind_type'], prefix='wind_type',dummy_na=True)],axis=1).drop(['wind_type'],axis=1)

dataframe = pd.concat([dataframe,pd.get_dummies(dataframe['sky_cavok'], prefix='sky_cavok',dummy_na=True)],axis=1).drop(['sky_cavok'],axis=1)

dataframe = movecol(dataframe, cols_to_move=['power_out_kw'], ref_col='sky_cavok_nan', place='After')

print("")
print("Null Info")
print(dataframe.isnull().sum())
print("")

dataframe = np.round(dataframe)

print(np.any(np.isnan(dataframe)))
print(np.all(np.isfinite(dataframe)))

dataframe.fillna(0, inplace=True)

dataframe.replace([np.inf, -np.inf], 0, inplace=True)

print(dataframe.info())

array = dataframe.values
X = array[:,0:19]
Y = array[:,19]

print(Y)

# prepare configuration for cross validation test harness
seed = 7
# prepare models
models = []
models.append(('LR', LogisticRegression(multi_class='auto',solver='lbfgs')))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))

# evaluate each model in turn
results = []
names = []
scoring = 'accuracy'

for name, model in models:
	kfold = model_selection.KFold(n_splits=10, random_state=seed)
	print(name)
	cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
	results.append(cv_results)
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
