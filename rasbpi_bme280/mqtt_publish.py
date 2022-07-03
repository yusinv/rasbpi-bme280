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
        temperature_sensor_conf = {
            'name': '{} Temperature'.format(discovery_conf.get("name", "BME 280")),
            'device_class': 'temperature',
            'state_topic': config.get('temperature_topic', 'temp'),
            'unit_of_measurement': '°C'
        }
        pressure_sensor_conf = {
            'name': '{} Pressure'.format(discovery_conf.get("name", "BME 280")),
            'device_class': 'pressure',
            'state_topic': config.get('pressure_topic', 'pressure'),
            'unit_of_measurement': 'mmHg'
        }
        humidity_sensor_conf = {
            'name': '{} Humidity'.format(discovery_conf.get("name", "BME 280")),
            'device_class': 'humidity',
            'state_topic': config.get('humidity_topic', 'humidity'),
            'unit_of_measurement': '%'
        }
        msgs = [('{}/sensor/{}_t/config'.format(discovery_conf['prefix'], discovery_conf['id']),
                 json.dumps(temperature_sensor_conf), 0, False),
                ('{}/sensor/{}_p/config'.format(discovery_conf['prefix'], discovery_conf['id']),
                 json.dumps(pressure_sensor_conf), 0, False),
                ('{}/sensor/{}_h/config'.format(discovery_conf['prefix'], discovery_conf['id']),
                 json.dumps(humidity_sensor_conf), 0, False)]
        publish.multiple(msgs, hostname=config['mqtt_broker_host'])

    while True:
        temperature, pressure, humidity = bme280.readBME280All()
        msgs = [(config.get('temperature_topic', 'temp'), '{:.2f}'.format(temperature), 0, False),
                (config.get('pressure_topic', 'pressure'), '{:.2f}'.format(pressure * 0.75006375541921), 0, False),
                (config.get('humidity_topic', 'humidity'), '{:.2f}'.format(humidity), 0, False)]

        publish.multiple(msgs, hostname=config['mqtt_broker_host'])
        time.sleep(1 * 60)


if __name__ == "__main__":
    main()
