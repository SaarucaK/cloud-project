import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

credentials_path = "C:/Users/saaru/cloudproject/iron-tea-382913-d9ed42776f0f.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

project_id = "iron-tea-382913"
subscription_id = "round_dataset-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f'Received message: {message}')
    print(f'data: {message.data}')
    for key in message.data:
        if key == 'temp':
            print ("hi")
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    streaming_pull_future.result()
