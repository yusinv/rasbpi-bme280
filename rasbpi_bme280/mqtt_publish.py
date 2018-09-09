import time

import paho.mqtt.publish as publish

import rasbpi_bme280.bme280 as bme280

mqtt_broker_host = "nas"

# sub_topic = "sensor/instructions"    # receive messages on this topic

pub_topic = "home/hall/"  # send messages to this topic


# when connecting to mqtt do this;
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # client.subscribe(sub_topic)


# when receiving a mqtt message do this;
# def on_message(client, userdata, msg):
#     message = str(msg.payload)
#     print(msg.topic+" "+message)
#     display_sensehat(message)

# def publish_mqtt(sensor_data):
#     mqttc = mqtt.Client("python_pub")
#     mqttc.connect(Broker, 1883)
#     mqttc.publish(pub_topic, sensor_data)
# mqttc.loop(2) //timeout = 2s

# def on_publish(mosq, obj, mid):
#     print("mid: " + str(mid))


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(mqtt_broker_host, 1883, 60)

def main():
    while True:
        temperature, pressure, humidity = bme280.readBME280All()
        msgs = [(pub_topic + "temperature", str(temperature), 0, False),
                (pub_topic + "pressure", str(pressure), 0, False),
                (pub_topic + "humidity", str(humidity), 0, False)]

        publish.multiple(msgs, hostname=mqtt_broker_host)
        time.sleep(1 * 60)


if __name__ == "__main__":
    main()
