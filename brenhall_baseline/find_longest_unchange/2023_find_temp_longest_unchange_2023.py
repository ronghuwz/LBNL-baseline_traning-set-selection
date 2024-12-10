import pandas as pd

# Load the new CSV file for temperature data
file_path_temp = './brenhall_baseline/find_longest_unchange/data/skyspark_raw_data/pre_temp_2023.csv'
data_temp = pd.read_csv(file_path_temp)


# Step 1: Preprocess the Timestamp column in the temperature data to remove the timezone name
data_temp['Timestamp'] = data_temp['Timestamp'].str.extract(r'(^.+?)(?=\s)')[0]



# Step 2: Convert the Timestamp column to datetime
data_temp['Timestamp'] = pd.to_datetime(data_temp['Timestamp'], utc=True)

# Set the Timestamp as the index for the temperature data
data_temp.set_index('Timestamp', inplace=True)



# Step 3: Clean the temperature column by removing the "°F" suffix and converting to numeric
data_temp['Irvine, CA Temp'] = (
    data_temp['Irvine, CA Temp']
    .str.replace('°F', '', regex=False)  # Remove '°F' unit
    .astype(float)                        # Convert to numeric
)



# Step 4: Interpolate the temperature data to 15-minute intervals
data_temp_resampled = data_temp.resample('15min').interpolate(method='linear')

# Load the previously saved interpolated electic load data (15-min intervals)
file_path_interpolated = './brenhall_baseline/find_longest_unchange/data/interpolated_load_2023_cleaned.csv'
data_interpolated = pd.read_csv(file_path_interpolated)



# Step 5: Ensure the 'Timestamp' column is in datetime format for the interpolated data
data_interpolated['Timestamp'] = pd.to_datetime(data_interpolated['Timestamp'])

# Set the Timestamp as the index for the interpolated data
data_interpolated.set_index('Timestamp', inplace=True)



# Step 6: Reindex the resampled temperature data to match the timestamp of the interpolated data
# This will align the temperature data with the interpolated data's timestamps.
aligned_temp_data = data_temp_resampled.reindex(data_interpolated.index, method='nearest')



# Step 7: Convert the index (Timestamp) to UNIX timestamp in milliseconds
aligned_temp_data.index = aligned_temp_data.index.view('int64') // 10**6  # Convert to UNIX timestamp (ms)



# Step 8: Save the aligned temperature data with UNIX timestamps to a new file without the column name
output_path_temp_unix = './brenhall_baseline/find_longest_unchange/data/aligned_temp_2023_unix.csv'
aligned_temp_data.to_csv(output_path_temp_unix, index=True, header=False)  # header=False to avoid saving column names

print(f"The aligned temperature data with UNIX timestamps has been saved to: {output_path_temp_unix}")
