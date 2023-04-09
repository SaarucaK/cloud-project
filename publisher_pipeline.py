import apache_beam as beam
import csv
import json
import os
from google.cloud import pubsub_v1
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

credentials_path = "C:/Users/saaru/cloudproject/iron-tea-382913-d9ed42776f0f.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


publisher = pubsub_v1.PublisherClient()
project_id = "iron-tea-382913"
topic_id = "round_dataset"
topic_path = publisher.topic_path(project_id, topic_id)


def process_data(row):
    #Vehicle Density: Check how many cars are on the road at a given time.
    vehicle_density = row['vehicle_density']

    #Driver Awareness: Check for cars stopped for an extended period of time.(velocity 0 and acceleration 0)
    if row['totalVelocity']==0 and row['totalAcceleration']==0:
        driver_awareness="low awareness"
    else:
        driver_awareness="high awareness"

    #Speed Limit Compliance: Check for cars traveling at speeds higher than the speed limit.
    if float(row['totalVelocity']) >float(row['speedLimit']):
        compliance = False
    else:
        compliance = True

    #Collision Safety: Predict whether or not a car will collide with another car. (same xCenter and yCenter at same time)
    if int(row['num_collision_vehicles'])>1:
        potential_collision = True
    else:
        potential_collision = False

    #Pedestrian Safety: Check to see if there are pedestrians regularly crossing the road.
    if row['class']=="pedestrian":
        pedestrian_presence = True
    else:
        pedestrian_presence=False

    #Vulnerable Road User Safety: (pedestrian, bicycle, motorcycle)Check to see if there are pedestrians regularly crossing the road.
    if row['class']=="pedestrian" or row['class']=="bicycle" or row['class']=="motorcycle":
        vulnerable_user = True
    else:
        vulnerable_user=False

    #Slip Angle: the angle between the direction in which a wheel is pointing and the direction in which it is actually traveling
    if abs(float(row['slipangle']))>=0 and abs(float(row['slipangle'])) < 20:
        slip = "safe slip angle"
    else:
        slip = "unsafe slip angle"
        
    # Construct output message
    msg = {"track id": row['trackId'], 
           "recording id": row['recordingId_x'], 
           "safe slip angle": slip,
           "speed safety compliance":compliance, 
           "potential collision":potential_collision, 
           "pedestrian presence":pedestrian_presence, 
           "vulnerable user presence":vulnerable_user, 
           "vehicle density":vehicle_density}
    return str(msg)

def publish_message(message):
    data = message.encode('utf-8')
    future = publisher.publish(topic_path, data)
    print(f'published message id {future.result()}')
    time.sleep(1)

def run():
    with beam.Pipeline() as pipeline:
        header = ['recordingId_x', 'trackId', 'frame', 'trackLifetime', 'xCenter',
       'yCenter', 'heading', 'width_x', 'length_x', 'xVelocity', 'yVelocity',
       'xAcceleration', 'yAcceleration', 'lonVelocity', 'latVelocity',
       'lonAcceleration', 'latAcceleration', 'recordingId_y', 'initialFrame',
       'finalFrame', 'numFrames', 'width_y', 'length_y', 'class', 'frameRate',
       'current_time', 'vehicle_density', 'slipangle', 'speedLimit',
       'duration', 'numTracks', 'numVehicles', 'numVRUs', 'totalVelocity',
       'totalAcceleration', 'xCenterRound', 'yCenterRound',
       'num_collision_vehicles']
        # Read CSV file
        csv_lines = (pipeline 
                     | 'Read CSV' >> beam.io.ReadFromText('combined_dataset.csv', skip_header_lines=1) 
                     | 'Parse CSV' >> beam.Map(lambda line: next(csv.reader([line]))))

        # Process each row
        output = (csv_lines
                  | 'Process Data' >> beam.Map(lambda fields: process_data({k: v for k, v in zip(header, fields)}))
                  | 'Publish Message' >> beam.Map(publish_message))

if __name__ == '__main__':
    # Set up Google Cloud Pub/Sub client
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Run the pipeline
    run()