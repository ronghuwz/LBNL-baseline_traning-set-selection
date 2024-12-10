import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Load the JSON data for predictions
with open('brenhall_baseline/find_longest_unchange/output/baseline_training_on_2022-prediction_on_2023.json', 'r') as file:
    json_data = json.load(file)

# Extract predicted baseline data
baseline_data = json_data['power_data']['baseline']
baseline_times = [datetime.datetime.fromtimestamp(point[0]) for point in baseline_data]
baseline_values = [point[1] for point in baseline_data]

# Create a dataframe for the baseline data
baseline_df = pd.DataFrame({'Timestamp': baseline_times, 'Baseline': baseline_values})

# Load the CSV data for actuals
csv_data = pd.read_csv('./brenhall_baseline/find_longest_unchange/data/load_after_processing_2023.csv', header=None, names=['Timestamp', 'Power'])

# Convert the CSV timestamps from milliseconds to datetime objects
csv_data['Timestamp'] = pd.to_datetime(csv_data['Timestamp'], unit='ms')

# Filter both datasets for the date range 7.1 to 12.31
start_date = '2023-01-01'
end_date = '2023-12-31'

baseline_df_filtered = baseline_df[(baseline_df['Timestamp'] >= start_date) & (baseline_df['Timestamp'] <= end_date)]
csv_data_filtered = csv_data[(csv_data['Timestamp'] >= start_date) & (csv_data['Timestamp'] <= end_date)]

# Plot the data
plt.figure(figsize=(14, 7))

# Plot the actual power from the CSV
plt.plot(csv_data_filtered['Timestamp'], csv_data_filtered['Power'], label='Actual Power', color='blue', alpha=0.7)

# Plot the baseline power from the JSON
plt.plot(baseline_df_filtered['Timestamp'], baseline_df_filtered['Baseline'], label='Baseline Power', color='orange', alpha=0.7)

# Add labels, title, and legend
plt.xlabel('Time')
plt.ylabel('Power (kW)')
plt.title('Actual vs Baseline Power Data (2023)')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
