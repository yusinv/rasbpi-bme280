from setuptools import setup

setup(
    name='rasbpi_bme280',
    version='0.0.1',
    url='',
    license='',
    author='valentin',
    author_email='',
    description='', install_requires=['paho-mqtt', 'pyyaml'],
    packages=['rasbpi_bme280'],
    entry_points={
        'console_scripts': [
            'bme280_mqtt=rasbpi_bme280.mqtt_publish:main',
        ],
    },
    data_files=[('/etc/systemd/system/', ['extra/bme280_mqtt.service']),
                ('/etc', ['extra/bme280_mqtt_conf.yaml'])],
)
