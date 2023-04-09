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
df = pd.read_csv('final_dataset.csv')
df

while (True):
    
    try:
        for index, row in df.iterrows():
            if row['lonAcceleration']>0:
                slipangle = math.degrees(math.atan(row['latVelocity']/row['lonAcceleration']))
            else:
                slipangle=0
            if abs(slipangle)>=0 and abs(slipangle) < 20:
                slip = "safe slip angle"
            else:
                slip = "unsafe slip angle"
            velocity = math.sqrt(row['xVelocity']**2+row['yVelocity']**2)
            acceleration = math.sqrt(row['xAcceleration']**2+row['yAcceleration']**2)
            #print(acceleration)
            low_thres = ['truck', 'bus', 'trailer']
            high_thres = ['pedestrian', 'bicycle', 'motorcycle', 'car', 'van',]
            max_velocity =  velocity + acceleration*row['time']
            if row['class'] in low_thres:
                if max_velocity>row['speedLimit']*1.1:
                    safe_velocity = "not safe"
                else:
                    safe_velocity = "safe"
            if row['class'] in high_thres:
                if max_velocity>row['speedLimit']*1.2:
                    safe_velocity = "not safe"
                else:
                    safe_velocity = "safe"
            #print(max_velocity,safe_velocity,row['class'],index)


 
            # get random values within a normal distribution of the value

            msg={"track id": row['trackId'], "recording id": row['recordingId'], "slip angle": slipangle,"safe slip angle": slip,"velocity":velocity,"acceleration":acceleration, "maximum velocity":max_velocity, "safe velocity":safe_velocity, "class":row['class']};
            msg_format = str(msg)
            data = msg_format.encode('utf-8')
            future = publisher.publish(topic_path, data)
            print(f'published message id {future.result()}')
            time.sleep(.5)
    except KeyboardInterrupt:
        break;
