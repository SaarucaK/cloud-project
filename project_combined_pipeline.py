# pytype: skip-file
import numpy as np
import random
import time
from math import sqrt
import pandas as pd
import glob
from numpy import random
import sys
import pathlib
import math
from math import *
import time

import argparse
import logging

import apache_beam as beam
from apache_beam.dataframe.convert import to_dataframe
from apache_beam.dataframe.convert import to_pcollection
from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions

def SafetyMeasures(row):
    # Split the row into columns
    columns = row.split(',')
    
    # Extract the required columns
    track_id = columns[1]
    recording_id = columns[0]
    vehicle_density = columns[28]
    total_velocity = columns[32]
    total_acceleration = columns[33]
    speed_limit = columns[26]
    num_collision_vehicles = columns[37]
    class_type = columns[23]
    slip_angle = columns[27]

    # Convert the compliance value to a float
    compliance = float(total_velocity) <= float(speed_limit)

    # Determine the driver awareness based on the velocity and acceleration values
    if total_velocity == '0' and total_acceleration == '0':
        driver_awareness = "low awareness"
    else:
        driver_awareness = "high awareness"

    # Determine if a potential collision is present
    if int(num_collision_vehicles) > 1:
        potential_collision = True
    else:
        potential_collision = False

    # Determine if a pedestrian is present
    if class_type == "pedestrian":
        pedestrian_presence = True
    else:
        pedestrian_presence = False

    # Determine if a vulnerable user is present
    if class_type in ["pedestrian", "bicycle", "motorcycle"]:
        vulnerable_user = True
    else:
        vulnerable_user = False

    # Determine if the slip angle is safe
    if abs(float(slip_angle)) >= 0 and abs(float(slip_angle)) < 20:
        slip_angle_safety = "safe slip angle"
    else:
        slip_angle_safety = "unsafe slip angle"

    # Create a dictionary with the processed data
    processed_data = {
        "track_id": track_id,
        "recording_id": recording_id,
        "vehicle_density": vehicle_density,
        "driver_awareness": driver_awareness,
        "compliance": compliance,
        "potential_collision": potential_collision,
        "pedestrian_presence": pedestrian_presence,
        "vulnerable_user": vulnerable_user,
        "slip_angle_safety": slip_angle_safety
    }

    # Return the processed data
    return processed_data

with beam.Pipeline() as pipeline:
    (
        pipeline
        | 'ReadFromText' >> beam.io.ReadFromText('combined_dataset.csv', skip_header_lines=1)
        | 'ProcessData' >> beam.Map(SafetyMeasures)
        | 'WriteToText' >> beam.io.WriteToText('output', file_name_suffix='.txt')
    )