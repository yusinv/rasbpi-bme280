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

        discovery_msg = {
            'dev': {
                'ids': f'{discovery_conf["id"]}',
                'name': f'{discovery_conf["name"]}',
                'mf': 'Bla electronics',
                'mdl': 'xya',
                'sw': '1.0',
                'sn': 'ea334450945afc',
                'hw': '1.0rev2'
            },
            'o': {
                'name': 'bla2mqtt',
                'sw': '2.1',
                'url': 'https://bla2mqtt.example.com/support'
            },
            'cmps': {
                f'{discovery_conf["id"]}_t': {
                    'name': f'{discovery_conf.get("name", "BME 280")} Temperature',
                    'p': 'sensor',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C',
                    'value_template': '{{ value_json.temperature }}',
                    'unique_id': f'{discovery_conf["id"]}_t'
                },
                f'{discovery_conf["id"]}_p': {
                    'name': f'{discovery_conf.get("name", "BME 280")} Pressure',
                    'p': 'sensor',
                    'device_class': 'pressure',
                    'unit_of_measurement': 'mmHg',
                    'value_template': '{{ value_json.pressure }}',
                    'unique_id': f'{discovery_conf["id"]}_p'
                },
                f'{discovery_conf["id"]}_h': {
                    'name': f'{discovery_conf.get("name", "BME 280")} Humidity',
                    'p': 'sensor',
                    'device_class': 'humidity',
                    'unit_of_measurement': '%',
                    'value_template': '{{ value_json.humidity }}',
                    'unique_id': f'{discovery_conf["id"]}_h'
                },
            },
            'state_topic': config.get('state_topic', 'home/hall_bme_280/state'),
            'qos': 2
        }

        publish.single(f'{discovery_conf["prefix"]}/device/{discovery_conf["id"]}/config',
                       json.dumps(discovery_msg), 0, True)

    while True:
        temperature, pressure, humidity = bme280.read_bme280_all()
        publish.single(config.get('state_topic', 'home/hall_bme_280/state'),
                       json.dumps({
                           "temperature": temperature,
                           "pressure": pressure,
                           "humidity": humidity
                       }))
        time.sleep(1 * 60)


if __name__ == "__main__":
    main()
