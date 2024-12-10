import json
import matplotlib.pyplot as plt
import datetime

# Load the JSON data
with open('brenhall_baseline/find_longest_unchange/output/new_2023_baseline-prediction.json', 'r') as file:
    data = json.load(file)

# Extract baseline data
baseline_data = data['power_data']['baseline']

# Convert Unix timestamps to datetime objects for plotting
baseline_times = [datetime.datetime.fromtimestamp(point[0]) for point in baseline_data]
baseline_values = [point[1] for point in baseline_data]

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(baseline_times, baseline_values, label='Baseline', color='red', linestyle='--')

# Add labels and legend
plt.xlabel('Time')
plt.ylabel('Power (kW)')
plt.title('Baseline Power Data Prediction (7.1 to 12.31, 2023)')
plt.legend()

# Show the plot
plt.show()