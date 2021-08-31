The original datasets were taken from three places -

Wind data - https://datasource.kapsarc.org/explore/dataset/saudi-hourly-weather-data

Solar data - https://rratlas.energy.gov.sa/

Consumption data - https://data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data

There were multiple issues with them which was rectified before feeding into the Machine learning algorithms. Such as -

Wind Data
--------------
*Fix the date notations to suit our purpose
*Reduce ambiguity in location coordinates
*Remove columns not directly related to our purpose
*Handle outlier and invalid data
*Calculate Air density with the available columns (Air pressure, Dew point, Air temperature)
*Calculate the power output in Kilowatts of a wind turbine based on the available column values using formula - P = p/2 * r² * v³ * ? * ?


Solar Data
-------------
1. Use data from the source - Renewable Resource Atlas (https://rratlas.energy.gov.sa/)
-A reliable source from Saudi
-I have already uploaded the entire dataset of them here -
https://drive.google.com/drive/folders/1H7eQ8xbjY96TIAMMjdd4_e8PKA3bxGKf?usp=sharing
-Monthly data from 2013 to 2018

2. Find out locations of Solar panel data collection centers from "RRMM Solar Monitor Locations.csv" from here
-I verified each location manually by checking the coordinates on a map to see how close it is to NEOM

3. Filter out and find locations closer to the NEOM area. Create a map detailing levels in terms of closeness to NEOM -
- https://www.google.com/maps/d/edit?mid=1TOFyO26riGGwAS4hzryj_vQuCkuPdHs-&usp=sharing
-In the above link, "Closest" are the stations very close to NEOM. "Level 1" is slightly further away, "Level 2" is even more further. "Level 3" is the max distance between the NEOM
-I have color-coded them accordingly
- Reason for levels of closeness - There are fewer data compared to the wind dataset which we have used.

4. Combined the datasets from the above coordinates (much more detailed info in "Activity Log.txt") while fixing issues in them

5. Calculated solar energy output (research + links + methodology explained in detail in "Activity Log.txt")
-Dropped columns not necessary for calculations
-Based on research, found out formulas on how the data provided will affect the output
-Handled minor column null values with the mean value
-Wind speed is a major factor, so used Linear Regression to predict the missing values

Consumption Data
-----------------------
1. Use data from the source - https://data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data
*Size - 1.5 GB (zipped) / 16.5 GB (unzipped)
*Summary - Electricity consumption data from the smart city for each customer sampled every 30 minutes from 2010 -2014
*Columns - 'Customer_Id','Reading_Datetime',' Calendar_Key',' Event_Key',' General_Supply_Kwh', ' Controlled_Load_Kwh', ' Gross_Generation_Kwh',' Net_Generation_Kwh',' Other_Kwh'
* The most important attributes are -
	*Customer_Id - unique ID per customer
	*Reading_Datetime - Date and time of sampling
	*General_Suuply_Kwh - the amount of consumption within sampled time
*Number of customers in the dataset - 13,735
*Number of rows - 344,518,791
Pros - Massive dataset
          Meticulous sampling - No gaps or irregularities
Cons - Dataset too large. Cannot load into python pandas
           The sampling is 30 minutes. Should aggregate to 1 day

2. Gain knowledge about the dataset
* Use unix commands such as - awk -F"," '{print $1}' CD_INTERVAL_READING_ALL_NO_QUOTE.csv > out.csv to separate only the customer_ID field (resulting file ~2.5GB)
* Tried MySQL, Pandas, Dask for processing - out of memory error. Only line by line reading approach works
* Write script to count the total number of instances per unique ID and the total number of customers  (unique3_out2.csv - contains customer ID + number of rows) - https://drive.google.com/file/d/1VVLWeVSt6iAuZlunwnbvOFrwMbP122Jy/view?usp=sharing

3. Split the dataset (based on number of rows)
*Split the dataset into rows of 2,000,000 rows each resulting in 173 separate CSV files
*Isolated first 20 files for analysis
*Conclusion - Might not be the best approach analysis must be done based on each customer. Arbitrary value of
2,000,000 does not guarantee that

4. Split the dataset (based on customer_ID)
*Split the data into separate files resulting in one CSV file per customer
*Conclusion - Much more manageable file sizes. Can load into pandas

5. Aggregate data from 30 minutes to 1 day
*Problem - Process seems to be really time-consuming ( files per hour - 13,735 files would take approx. ).
  Solution - For now, use the first 100-500 files and see if it's sufficient for prediction
*Load each CSV file into pandas separately
*Access the 'Reading_Datetime' column
*Add all the values of 'General_Suuply_Kwh' together for each data
*Format and output resulting in the smaller dataset 
*Merge all separate datasets together 