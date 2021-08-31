import numpy as np
import pandas as pd
from tqdm import tqdm

comb_data = pd.read_csv("Solar All Combined.csv",low_memory=False)

drop_cols = ['Air Temperature Uncertainty (C°)','Wind Direction at 3m (°N)','Wind Direction at 3m Uncertainty (°N)',
'Wind Speed at 3m Uncertainty (m/s)', 'Wind Speed at 3m (std dev) (m/s)', 
'Wind Speed at 3m (std dev) Uncertainty (m/s)','Peak Wind Speed at 3m (m/s)','Peak Wind Speed at 3m Uncertainty (m/s)','Standard Deviation DHI (Wh/m2)',
'Standard Deviation DNI (Wh/m2)','Standard Deviation GHI (Wh/m2)']

comb_data.drop(drop_cols, axis = 1, inplace=True) 

comb_data['Date'] =  pd.to_datetime(comb_data['Date'], format="%d/%m/%Y %H:%M")

#comb_data.set_index('Date', drop=False, inplace=True)

print("Comb data info")
print(comb_data.info())
print("")

print("Null Info Before Fixing")
print(comb_data.isnull().sum())
print("")

comb_data['Air Temperature (C°)'] = comb_data['Air Temperature (C°)'].replace(np.nan, comb_data['Air Temperature (C°)'].mean())
comb_data['DHI (Wh/m2)'] = comb_data['DHI (Wh/m2)'].replace(np.nan, comb_data['DHI (Wh/m2)'].mean())
comb_data['DHI Uncertainty (Wh/m2)'] = comb_data['DHI Uncertainty (Wh/m2)'].replace(np.nan, comb_data['DHI Uncertainty (Wh/m2)'].mean())
comb_data['DNI (Wh/m2)'] = comb_data['DNI (Wh/m2)'].replace(np.nan, comb_data['DNI (Wh/m2)'].mean())
comb_data['DNI Uncertainty (Wh/m2)'] = comb_data['DNI Uncertainty (Wh/m2)'].replace(np.nan, comb_data['DNI Uncertainty (Wh/m2)'].mean())
comb_data['GHI (Wh/m2)'] = comb_data['GHI (Wh/m2)'].replace(np.nan, comb_data['GHI (Wh/m2)'].mean())
comb_data['GHI Uncertainty (Wh/m2)'] = comb_data['GHI Uncertainty (Wh/m2)'].replace(np.nan, comb_data['GHI Uncertainty (Wh/m2)'].mean())
comb_data['Relative Humidity (%)'] = comb_data['Relative Humidity (%)'].replace(np.nan, comb_data['Relative Humidity (%)'].mean())
comb_data['Relative Humidity Uncertainty (%)'] = comb_data['Relative Humidity Uncertainty (%)'].replace(np.nan, comb_data['Relative Humidity Uncertainty (%)'].mean())
comb_data['Barometric Pressure (mB (hPa equiv))'] = comb_data['Barometric Pressure (mB (hPa equiv))'].replace(np.nan, comb_data['Barometric Pressure (mB (hPa equiv))'].mean())
comb_data['Barometric Pressure Uncertainty (mB (hPa equiv))'] = comb_data['Barometric Pressure Uncertainty (mB (hPa equiv))'].replace(np.nan, comb_data['Barometric Pressure Uncertainty (mB (hPa equiv))'].mean())

#comb_data.fillna(comb_data.mean())

from sklearn.linear_model import LinearRegression
linreg = LinearRegression()

data_without_null = comb_data.dropna()

#All features except wind_speed
train_data_x = data_without_null.drop(['Wind Speed at 3m (m/s)','Site','Date'], axis=1) #data_without_null.iloc[]

#Only wind speed
train_data_y = data_without_null[['Wind Speed at 3m (m/s)']] #data_without_null.iloc[]

#Train with available data
linreg.fit(train_data_x,train_data_y)

#Predict for whole dataset and replace missing values later
test_data = comb_data.drop(['Wind Speed at 3m (m/s)','Site','Date'], axis=1)
wind_predicted = pd.DataFrame(np.random.randn(634, 1), columns = ['Wind Speed at 3m (m/s)'])
#print(wind_predicted)
wind_predicted['Wind Speed at 3m (m/s)'] = pd.DataFrame(linreg.predict(test_data))
#print("")
#print(wind_predicted)

#Replace only missing values
comb_data['Wind Speed at 3m (m/s)'].fillna(wind_predicted['Wind Speed at 3m (m/s)'],inplace=True)

print("Null Info After Fixing")
print(comb_data.isnull().sum())
print("")

#Formula for Energy generation -  E = A x r x H x PR

print("Calculate power output")
A= 1.9625 #Area m2
r= 16.3/100 #Yield
H = 2361 #Annual irradiance kWh/m2 per year
PR = 0.75
std_temp = 25

for idx, row in tqdm(comb_data.iterrows(), total=comb_data.shape[0]):
    
    amb_temp = comb_data.at[idx,'Air Temperature (C°)']
    ghi = comb_data.at[idx,'GHI (Wh/m2)']
    wind_speed = comb_data.at[idx,'Wind Speed at 3m (m/s)']

    temp = amb_temp + (ghi / ((26.9 + 6.20) * wind_speed))

    #print("TEMP")
    #print(temp)
    
    if temp > std_temp:
        r = (16.3 - ((temp - std_temp) * 0.09)) / 100
    else:
        r = (16.3 + ((std_temp - temp) * 0.09)) / 100

    #print("r")
    #print(r)
    #print("")

    energy = A * r * H * PR

    #print("energy")
    #print(energy)

    comb_data.at[idx,'power_out_kwh'] = energy
    comb_data.at[idx,'power_out_kwh'] = comb_data.at[idx,'power_out_kwh'].round(decimals=3)
    
    comb_data.at[idx,'power_out_farm_kwh'] = energy*62000 #Farm
    comb_data.at[idx,'power_out_farm_kwh'] = comb_data.at[idx,'power_out_farm_kwh'].round(decimals=3)

print("Power output calculated")
print("")

print("Output merged and calculated df as CSV")
comb_data.to_csv (r'calculated_dataset_solar.csv', index = False, header=True)
print("")
