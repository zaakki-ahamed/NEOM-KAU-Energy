import pandas as pd
import numpy as np
import math
import csv #Debug
from tqdm import tqdm

def print_info(df):
    print("Print info of {}",format(df))
    print(df.info())
    print("")

def air_density(air_temp,dew_point,pressure):
    
    #dew_point = dew_point + 273.15 #Kelvin = Celsius + 273.15
    dew_point = 6.1078 * (math.pow(10, (7.5 * dew_point) / (237.3 + dew_point)))

    #p₁ = 6.1078 * 10^[7.5*T /(T + 237.3)]          #T is the air temperature in Kelvins 
    #pv = p₁ * RH                                   #pv is the water vapor pressure in Pa
    #pd = p - pv                                    #pd is the pressure of dry air in Pa
    #ρ = (pd / (Rd * T)) + (pv / (Rv * T))

    #Rd is the specific gas constant for dry air equal to 287.058 J/(kg·K)
    #Rv is the specific gas constant for water vapor equal to 461.495 J/(kg·K)

    Rv=461.4964
    Rd=287.0531

    tk = air_temp + 273.15 #Convert to Kelvins
    #RH = 100*(math.exp((17.625*dew_point)/(243.04+dew_point))/math.exp((17.625*tk)/(243.04+tk)))
    pv = dew_point * 100 #RH
    pd = (pressure - dew_point)*100 #pressure - pv
    d = (pv/(Rv*tk)) + (pd/(Rd*tk))
    return d

maindf = pd.read_csv("final_combined_dataset.csv", sep=',',low_memory=False)

maindf['observation_date'] =  pd.to_datetime(maindf['observation_date'], format="%Y:%m:%d:%H:%M:%S")
print("Date conversion done")

maindf = maindf.sort_values(by='observation_date',ascending=True)
print("Sorting done")

for idx in maindf.index:
    x = maindf.at[idx,'latitude']
    number_dec = str(x-int(x))[1:]
    if len(number_dec) > 7:
        maindf.at[idx,'latitude'] = maindf.at[idx,'latitude'].round(decimals=6)

print("Latitude rounded up")

#maindf["power_out_kw"] = np.nan

#P = π/2 * r² * v³ * ρ * η
#minus_vals = [] #Debug
#minus_vals_pos = [] #Debug

print("Modify invalid data")
#for idx in maindf.index:
for idx, row in tqdm(maindf.iterrows(), total=maindf.shape[0]):
    a = 1011.15
    b = 4.72
    c = 22.42
    d = 9779.31
    e = 19545.52
    f = 3.47
    g = 234.51

    if maindf.at[idx,'atmospheric_sea_level_pressure'] > 9990:
        maindf.at[idx,'atmospheric_sea_level_pressure'] = a

    if maindf.at[idx,'air_temperature_dew_point'] > 990:
        maindf.at[idx,'air_temperature_dew_point'] = b

    if maindf.at[idx,'air_temperature'] > 990:
        maindf.at[idx,'air_temperature'] = c

    if maindf.at[idx,'visibility_distance'] > 49000:
        maindf.at[idx,'visibility_distance'] = d

    if maindf.at[idx,'sky_ceiling_height'] > 99990:
        maindf.at[idx,'sky_ceiling_height'] = e

    if maindf.at[idx,'wind_speed_rate'] > 999:
        maindf.at[idx,'wind_speed_rate'] = f

    if maindf.at[idx,'wind_direction_angle'] > 370:
        maindf.at[idx,'wind_direction_angle'] = g

print("Invalid data modified")

with pd.option_context('display.max_columns', 40):
    print(maindf.describe(include = [np.number]))

zero_vals = [] #Debug
zero_vals_pos = [] #Debug

count_n = 0

print("Calculate power output")
pi=3.141 
r=50
e=40/100 
for idx, row in tqdm(maindf.iterrows(), total=maindf.shape[0]):
    v=maindf.at[idx,'wind_speed_rate'] 
    ad=air_density(maindf.at[idx,'air_temperature'],maindf.at[idx,'air_temperature_dew_point'],maindf.at[idx,'atmospheric_sea_level_pressure'])
    
    maindf.at[idx,'air_density'] = ad
    maindf.at[idx,'air_density'] = maindf.at[idx,'air_density'].round(decimals=3)

    P = ((pi/2) * (r*r) * (v*v*v) * ad * e) / 1000

    maindf.at[idx,'power_out_kw'] = P
    maindf.at[idx,'power_out_kw'] = maindf.at[idx,'power_out_kw'].round(decimals=3)

    if P < 0.0 or maindf.at[idx,'air_density'] < 0.0 or maindf.at[idx,'wind_speed_rate'] > 50  : #Debug
        maindf.drop(idx, inplace=True)
        count_n = count_n + 1 
        #minus_vals.append(P) #Debug
        #minus_vals_pos.append(idx) #Debug
    elif P == 0.0:
        zero_vals.append(P) #Debug
        zero_vals_pos.append(idx) #Debug

print("Number of rows dropped due to negative/false values : ", count_n)
print("Power output calculated")

###############################################Debug ########################################

""" with open(..., 'w', newline='') as myfile:
     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
     wr.writerow(mylist) """

""" with open('Minus_list.csv', 'w') as f:
    writer = csv.writer(f,quoting=csv.QUOTE_ALL)
    writer.writerows(zip(minus_vals, minus_vals_pos))
 """
with open('Zero_list.csv', 'w') as f:
    writer = csv.writer(f,quoting=csv.QUOTE_ALL)
    writer.writerows(zip(zero_vals, zero_vals_pos))

###############################################Debug ########################################

print_info(maindf)

with pd.option_context('display.max_columns', 40):
    print(maindf.describe(include = [np.number]))

print("Output merged and calculated df as CSV")
maindf.to_csv (r'calculated_dataset_modified_invalid.csv', index = False, header=True)
print("")
