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

    #Speed Limit Compliance: Check for cars traveling at speeds higher than the speed limit.
    compliance = float(total_velocity) <= float(speed_limit)

    #Driver Awareness: Check for cars stopped for an extended period of time.(velocity 0 and acceleration 0)
    if total_velocity == '0' and total_acceleration == '0':
        driver_awareness = "low awareness"
    else:
        driver_awareness = "high awareness"

    #Collision Safety: Predict whether or not a car will collide with another car. (same xCenter and yCenter at same time)
    if int(num_collision_vehicles) > 1:
        potential_collision = True
    else:
        potential_collision = False

    #Pedestrian Safety: Check to see if there are pedestrians regularly crossing the road.
    if class_type == "pedestrian":
        pedestrian_presence = True
    else:
        pedestrian_presence = False

    #Vulnerable Road User Safety: (pedestrian, bicycle, motorcycle)Check to see if there are pedestrians regularly crossing the road.
    if class_type in ["pedestrian", "bicycle", "motorcycle"]:
        vulnerable_user = True
    else:
        vulnerable_user = False

    ##Slip Angle: the angle between the direction in which a wheel is pointing and the direction in which it is actually traveling
    if abs(float(slip_angle)) >= 0 and abs(float(slip_angle)) < 20:
        slip_angle_safety = "safe slip angle"
    else:
        slip_angle_safety = "unsafe slip angle"

    # Construct output message
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

    #process data
    return processed_data

#pipeline input and output
with beam.Pipeline() as pipeline:
    (
        pipeline
        | 'ReadFromText' >> beam.io.ReadFromText('combined_dataset.csv', skip_header_lines=1)
        | 'ProcessData' >> beam.Map(SafetyMeasures)
        | 'WriteToText' >> beam.io.WriteToText('output', file_name_suffix='.txt')
    )
