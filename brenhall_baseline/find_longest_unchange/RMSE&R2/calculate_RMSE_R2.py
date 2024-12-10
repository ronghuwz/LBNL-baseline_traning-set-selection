import json
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import datetime
import matplotlib.pyplot as plt

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
csv_data = pd.read_csv('./brenhall_baseline/find_longest_unchange/data/filtered_data_2023_with_index.csv')

# Ensure the 'Timestamp' columns are datetime64[ns] in both dataframes
csv_data['Timestamp'] = pd.to_datetime(csv_data['Timestamp'], errors='coerce', utc=True)  # Coerce errors to NaT


# Ensure the baseline dataframe has correct datetime format
baseline_df['Timestamp'] = pd.to_datetime(baseline_df['Timestamp'], utc=True)


# Merge the actual data and predicted data on the 'Timestamp'
merged_df = pd.merge(csv_data, baseline_df, on='Timestamp', how='inner')

import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

# Filter the merged dataframe to only use rows where both actual and predicted values are present
merged_df = merged_df.dropna(subset=['Power', 'Baseline'])  # Drop rows with missing values in either actual or predicted


#***********************************   Important!!! need to shift the prediction value by 8 positions  ********************************#
# Shift the predicted values by 8 time steps (after shifting, the pattern matches with the actual pattern)
shifted_predicted_values = merged_df['Baseline'].shift(periods=8).fillna(0)

# Add the shifted predictions to the dataframe
merged_df['Shifted_Predicted'] = shifted_predicted_values
#**************************************************************************************************************************************


# Extract the actual and predicted values for the filtered data
actual_values = merged_df['Power']
predicted_values = merged_df['Shifted_Predicted']

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))

# Calculate R²
r2 = r2_score(predicted_values, actual_values)

# Print the results
print(f"RMSE: {rmse}")
print(f"R²: {r2}")



#**************************************************************************************************************************************
# Plot the actual vs predicted values
plt.figure(figsize=(10, 6))

# Plot actual values
plt.plot(merged_df['Timestamp'][10:300], merged_df['Power'][10:300], label='Actual', color='blue')

# Plot predicted values
plt.plot(merged_df['Timestamp'][10:300], merged_df['Shifted_Predicted'][10:300], label='Predicted', color='red', linestyle='--')

# Add title and labels
plt.title('Actual vs. Predicted Values (partial plot)')
plt.xlabel('Timestamp')
plt.ylabel('Power')

# Add a legend
plt.legend()

# Rotate x-axis labels for readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()


