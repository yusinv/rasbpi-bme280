from setuptools import setup

setup(
    name='rasbpi_bme280',
    version='',
    url='',
    license='',
    author='valentin',
    author_email='',
    description='', install_requires=['paho-mqtt'],
    entry_points={
        'console_scripts': [
            'bme280_mqtt=rasbpi_bme280.mqtt_publish:main',
        ],
    },
    data_files=[('share/doorbot', ['extra/doorbot.conf.template',
                                   'extra/doorbot.systemd-unit-local'])],
)
