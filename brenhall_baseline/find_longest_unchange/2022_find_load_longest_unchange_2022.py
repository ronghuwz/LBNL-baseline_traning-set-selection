import pandas as pd
import ruptures as rpt  # Ensure you have the ruptures library installed
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Load the new CSV file
file_path_new = './brenhall_baseline/find_longest_unchange/data/skyspark_raw_data/pre_load_2022.csv'
data_new = pd.read_csv(file_path_new)

# Step 1: Preprocess the Timestamp column to remove the timezone name
data_new['Timestamp'] = data_new['Timestamp'].str.extract(r'(^.+?)(?=\s)')[0]



# Step 2: Convert the Timestamp column to datetime
data_new['Timestamp'] = pd.to_datetime(data_new['Timestamp'], errors='coerce', utc=True)  # Convert to datetime and set UTC=True

# Remove rows with invalid date
data_new = data_new.dropna(subset=['Timestamp'])  # Drop rows with NaT in Timestamp



# Step 3: Set the Timestamp as the index to enable resampling
data_new.set_index('Timestamp', inplace=True)



# Step 4: Clean the power column by removing the "kW" suffix and converting to numeric
data_new['Bren Hall HVAC Elec Meter hvac elec power'] = (
    data_new['Bren Hall HVAC Elec Meter hvac elec power']
    .str.replace('kW', '', regex=False)  # Remove 'kW'
    .astype(float)                        # Convert to numeric
)

#*******************************************************************************************************************************
#*************************************************** Important *****************************************************************
# Engineers can input the available time period for baseline training:
available_data = data_new['2022-01-01':'2022-12-31']
#*******************************************************************************************************************************

# Step 6: Apply rolling smoothing to the power data
window_size = 24  # Example: Rolling window size of 48 data points
available_data['Smoothed Power'] = available_data['Bren Hall HVAC Elec Meter hvac elec power'].rolling(window=window_size, min_periods=1).mean()



# Step 7: Define the KernelCPD function using ruptures
def apply_kernel_cpd(data, penalty=1000):
    algo = rpt.KernelCPD(kernel="linear").fit(data)
    result = algo.predict(pen=penalty)
    return result



# Step 8: Define Isolation Forest for Anomaly Detection
def apply_isolation_forest(data, contamination=0.01):
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    anomalies = iso_forest.fit_predict(data.values.reshape(-1, 1))
    return pd.Series(anomalies, index=data.index)

# Parameters
penalty = 10000  # Adjust penalty for change point detection
contamination = 0.01  # Adjust contamination for anomaly detection



# Step 9: Detect anomalies using Isolation Forest
anomalies = apply_isolation_forest(available_data['Smoothed Power'], contamination=contamination)

# Remove detected anomalies (-1) from the data
available_data['Anomaly'] = anomalies
available_data_clean = available_data[available_data['Anomaly'] != -1]



# Step 10: Apply Kernel Change Point Detection on cleaned data
change_points = apply_kernel_cpd(available_data_clean['Smoothed Power'].values.reshape(-1, 1), penalty = penalty)

print("Detected change points (after removing anomalies):", len(change_points))



# Step 11: Find the longest unchanged period between two change points
max_gap = 0
start_idx = 0
end_idx = 0

# Iterate through change points to find the longest gap
for i in range(1, len(change_points)):
    gap = change_points[i] - change_points[i - 1]
    if gap > max_gap:
        max_gap = gap
        start_idx = change_points[i - 1]
        end_idx = change_points[i]

# Extract the longest unchanged period
longest_unchanged_period = available_data_clean.iloc[start_idx:end_idx]



# Step 12: Interpolated data to 15 min interval
longest_unchanged_period_interpolated = longest_unchanged_period.resample('15min').interpolate(method='linear')

#Save the interpolated data
output_path = './brenhall_baseline/find_longest_unchange/data/interpolated_load_2022_cleaned.csv'
longest_unchanged_period_interpolated[['Bren Hall HVAC Elec Meter hvac elec power']].to_csv(output_path, index=True, header=True)  



# Step 13: Convert the index to UNIX timestamp (in milliseconds)
longest_unchanged_period_interpolated.index = longest_unchanged_period_interpolated.index.view('int64') // 10**6  # Convert to UNIX timestamp (ms)



# Step 14: Save the interpolated data with UNIX timestamps to a file without column names
output_path_unix = './brenhall_baseline/find_longest_unchange/data/interpolated_load_2022_cleaned_unix.csv'
longest_unchanged_period_interpolated[['Bren Hall HVAC Elec Meter hvac elec power']].to_csv(output_path_unix, index=True, header=False)  # header=False to avoid saving column names

print(f"The interpolated data with UNIX timestamps has been saved to: {output_path_unix}")



# Step 15: Plot the data with change points
plt.figure(figsize=(10, 6))

# Plot the power data
plt.plot(available_data.index, available_data['Bren Hall HVAC Elec Meter hvac elec power'], label='Power Data', color='blue')

# Adjust the change point indices to fit the DataFrame index range
for change in change_points:
    if change < len(available_data_clean):
        plt.axvline(x=available_data_clean.index[change], color='red', linestyle='--', label="Change Point" if change == change_points[0] else "")

# Plot anomalies
anomalies_detected = available_data[available_data['Anomaly'] == -1]
plt.scatter(
    anomalies_detected.index, 
    anomalies_detected['Bren Hall HVAC Elec Meter hvac elec power'], 
    color='orange', 
    label='Anomalies', 
    marker='x', 
    s=100
)

# Add labels and title
plt.title('Power Data with CP & Anomalies')
plt.xlabel('Time')
plt.ylabel('Power (kW)')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()