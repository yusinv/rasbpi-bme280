import json
import sys
import time
import yaml

import paho.mqtt.publish as publish

import rasbpi_bme280.bme280 as bme280

# when connecting to mqtt do this;
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))


config = {}


def load_conf_file(config_file: str) -> None:
    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    global config
    config = cfg['config']


def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = '/etc/bme280_mqtt_conf.yaml'

    load_conf_file(config_path)



    if 'discovery' in config:
        discovery_conf = config['discovery']

        device = {
            "identifiers": [
                f'{discovery_conf["id"]}'
            ],
            "name": f'{discovery_conf["name"]}'
        }

        temperature_sensor_conf = {
            'name': f'{discovery_conf.get("name", "BME 280")} Temperature',
            'device_class': 'temperature',
            'state_topic': config.get('temperature_topic', 'temp'),
            "unique_id": f'{discovery_conf["id"]}_t',
            'unit_of_measurement': '°C',
            "device": device
        }
        pressure_sensor_conf = {
            'name': f'{discovery_conf.get("name", "BME 280")} Pressure',
            'device_class': 'pressure',
            'state_topic': config.get('pressure_topic', 'pressure'),
            "unique_id": f'{discovery_conf["id"]}_p',
            'unit_of_measurement': 'mmHg',
            "device": device
        }
        humidity_sensor_conf = {
            'name': f'{discovery_conf.get("name", "BME 280")} Humidity',
            'device_class': 'humidity',
            'state_topic': config.get('humidity_topic', 'humidity'),
            "unique_id": f'{discovery_conf["id"]}_h',
            'unit_of_measurement': '%',
            "device": device
        }
        msgs = [(f'{discovery_conf["prefix"]}/sensor/{discovery_conf["id"]}_t/config',
                 json.dumps(temperature_sensor_conf), 0, True),
                (f'{discovery_conf["prefix"]}/sensor/{discovery_conf["id"]}_p/config',
                 json.dumps(pressure_sensor_conf), 0, True),
                (f'{discovery_conf["prefix"]}/sensor/{discovery_conf["id"]}_h/config',
                 json.dumps(humidity_sensor_conf), 0, True)]
        publish.multiple(msgs, hostname=config['mqtt_broker_host'])

    while True:
        temperature, pressure, humidity = bme280.read_bme280_all()
        msgs = [(config.get('temperature_topic', 'temp'), f'{temperature:.2f}', 0, False),
                (config.get('pressure_topic', 'pressure'), f'{pressure * 0.75006375541921:.2f}', 0, False),
                (config.get('humidity_topic', 'humidity'), f'{humidity:.2f}', 0, False)]

        publish.multiple(msgs, hostname=config['mqtt_broker_host'])
        time.sleep(1 * 60)


if __name__ == "__main__":
    main()
