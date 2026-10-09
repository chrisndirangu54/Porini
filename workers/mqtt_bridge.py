"""Live MQTT -> authorized HTTP ingestion. Run only with configured credentials and TLS."""
import os,json,logging
import paho.mqtt.client as mqtt
import requests
logging.basicConfig(level=logging.INFO)
BROKER=os.environ["PORINI_MQTT_HOST"]
TOPIC=os.environ.get("PORINI_MQTT_TOPIC","porini/devices/+/events")
API=os.environ.get("PORINI_API_URL","http://localhost:8000")
KEY=os.environ["PORINI_SENSOR_KEY"]
def on_message(client,userdata,message):
    try:
        if len(message.payload)>65536:raise ValueError("Payload too large")
        payload=json.loads(message.payload)
        if not isinstance(payload,dict):raise ValueError("Expected event JSON")
        response=requests.post(API+"/events",json=payload,headers={"X-API-Key":KEY},timeout=15)
        response.raise_for_status()
        logging.info("Event accepted: %s",response.json().get("id"))
    except (ValueError,requests.RequestException) as exc:
        logging.error("Event rejected: %s",exc)
def main():
    client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(os.environ["PORINI_MQTT_USER"],os.environ["PORINI_MQTT_PASSWORD"])
    client.tls_set()
    client.on_message=on_message
    client.connect(BROKER,int(os.environ.get("PORINI_MQTT_PORT","8883")),60)
    client.subscribe(TOPIC,qos=1)
    client.loop_forever()
if __name__=="__main__":main()
