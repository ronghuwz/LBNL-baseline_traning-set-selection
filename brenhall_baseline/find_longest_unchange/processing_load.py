import pandas as pd

# Load the new CSV file
file_path_new = './brenhall_baseline/find_longest_unchange/data/skyspark_raw_data/pre_load_2022.csv'
data_new = pd.read_csv(file_path_new)

# Step 1: Preprocess the Timestamp column to remove the timezone name
data_new['Timestamp'] = data_new['Timestamp'].str.extract(r'(^.+?)(?=\s)')[0]

# Step 2: Convert the Timestamp column to datetime
data_new['Timestamp'] = pd.to_datetime(data_new['Timestamp'], utc=True)

# Set the Timestamp as the index
data_new.set_index('Timestamp', inplace=True)

# Step 3: Clean the power column by removing the "kW" suffix and converting to numeric
data_new['Bren Hall HVAC Elec Meter hvac elec power'] = (
    data_new['Bren Hall HVAC Elec Meter hvac elec power']
    .str.replace('kW', '', regex=False)  # Remove 'kW'
    .astype(float)                        # Convert to numeric
)

# Step 4: Resample the data to 15-minute intervals and interpolate
data_new = data_new.resample('15min').interpolate(method='linear')

# Convert the index back to Unix timestamp in milliseconds
data_new.index = data_new.index.astype('int64') // 10**6

# Step 5: Format the data
data_new.index = data_new.index.map('{:.1f}'.format)  # Format timestamp with one decimal
data_new['Bren Hall HVAC Elec Meter hvac elec power'] = data_new['Bren Hall HVAC Elec Meter hvac elec power'].map('{:.3f}'.format)  # Format power with three decimals

# Step 6: Remove the column names
data_new.columns = [None]  # Adjust to match the number of columns

# Save the cleaned data to a new CSV for verification
output_path = './brenhall_baseline/find_longest_unchange/data/load_after_processing_2022.csv'
data_new.to_csv(output_path, index=True, header=False)


print("finish processing original skyspark temp data, and save the file as load_after_processing_2022.csv")