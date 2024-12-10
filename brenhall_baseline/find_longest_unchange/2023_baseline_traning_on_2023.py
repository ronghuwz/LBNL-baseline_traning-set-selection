
import json
import datetime
from os import path
from loadshape.loadshape import Loadshape, utils

# ----- config constants ----- #
BUILDING_NAME = "My Building"
BUILDING_SQ_FT = 5367

# ------ change the file name that you want to use for predition -------- #
EXAMPLES_DIR    = path.dirname(path.abspath(__file__))
LOAD_DATA       = path.join(EXAMPLES_DIR, "data",  "interpolated_load_2023_cleaned_unix.csv")
TEMP_DATA       = path.join(EXAMPLES_DIR, "data",  "aligned_temp_2023_unix.csv")
TEMP_FORECAST   = path.join(EXAMPLES_DIR, "data",  "temp_after_processing_2023.csv")
TARIFF          = path.join(EXAMPLES_DIR, "data",  "tariff.json")

BASELINE_NAME   = "2023 Baseline Training"

PREDICTION_START      = "2023-07-01"  
PREDICTION_END        = "2023-12-31"  

# ----- write JSON output file ----- #
def write_json(data, file_name='output.json'):
    print(f"writing file: {file_name}")
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

# ----- build loadshape object ----- #
my_load_shape = Loadshape(load_data=LOAD_DATA, temp_data=TEMP_DATA, 
                          forecast_temp_data = TEMP_FORECAST,
                          # tariff_schedule=tariff_schedule
                          timezone='America/Los_Angeles',
                          temp_units="F", sq_ft=BUILDING_SQ_FT)

# ----- add exclusions as necessary ----- #
# my_load_shape.add_exclusion("2013-09-23 00:00:00", "2013-09-24 00:00:00")
# my_load_shape.add_exclusion("2013-09-27 00:00:00", "2013-09-28 00:00:00")
# my_load_shape.add_named_exclusion("US_HOLIDAYS")

# ----- generate a  baseline ----- #
yearly_baseline 	= my_load_shape.baseline(start_at=PREDICTION_START,
                                             end_at=PREDICTION_END,
                                             weighting_days=14,
                                             modeling_interval=900,
                                             step_size=900)

# ----- assemble a payload summarizng the seven day baseline ----- #
out = { "power_data": {} }
out["building"]                  = BUILDING_NAME
out["baseline_start_at"]         = PREDICTION_START
out["baseline_end_at"]           = PREDICTION_END
out["error_stats"]               = my_load_shape.error_stats
out["power_data"]["actual"]      = my_load_shape.actual_data(PREDICTION_START, PREDICTION_END)
out["power_data"]["baseline"]    = my_load_shape.baseline_data(PREDICTION_START, PREDICTION_END)

# ----- write output to file ----- #
file_name = path.join(EXAMPLES_DIR, "output", "baseline_training_on_2023-prediction_on_2023.json")
write_json(data=out, file_name=file_name )

print ("BASELINE EXAMPLE COMPLETE")
