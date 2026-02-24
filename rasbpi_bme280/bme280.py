import time
from ctypes import c_short

import smbus

DEVICE = 0x76  # Default device I2C address

# Register Addresses
REG_DATA = 0xF7
REG_CONTROL = 0xF4
REG_CONFIG = 0xF5

REG_CONTROL_HUM = 0xF2
REG_HUM_MSB = 0xFD
REG_HUM_LSB = 0xFE

# Oversample setting - page 27
OVERSAMPLE_TEMP = 2
OVERSAMPLE_PRES = 2
MODE = 1

# Oversample setting for humidity register - page 26
OVERSAMPLE_HUM = 2

# Chip ID Register Address
REG_ID = 0xD0

bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1


# Rev 1 Pi uses bus 0

def get_short(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index + 1] << 8) + data[index]).value


def get_u_short(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index + 1] << 8) + data[index]


def get_char(data, index):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result


def get_u_char(data, index):
    # return one byte from data as an unsigned char
    result = data[index] & 0xFF
    return result


def read_bme280_id(addr=DEVICE):

    (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
    return chip_id, chip_version


def read_bme280_all(addr=DEVICE):

    bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

    control = OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE
    bus.write_byte_data(addr, REG_CONTROL, control)

    # Read blocks of calibration data from EEPROM
    # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
    cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
    cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

    # Convert byte data to word values
    dig_t1 = get_u_short(cal1, 0)
    dig_t2 = get_short(cal1, 2)
    dig_t3 = get_short(cal1, 4)

    dig_p1 = get_u_short(cal1, 6)
    dig_p2 = get_short(cal1, 8)
    dig_p3 = get_short(cal1, 10)
    dig_p4 = get_short(cal1, 12)
    dig_p5 = get_short(cal1, 14)
    dig_p6 = get_short(cal1, 16)
    dig_p7 = get_short(cal1, 18)
    dig_p8 = get_short(cal1, 20)
    dig_p9 = get_short(cal1, 22)

    dig_h1 = get_u_char(cal2, 0)
    dig_h2 = get_short(cal3, 0)
    dig_h3 = get_u_char(cal3, 2)

    dig_h4 = get_char(cal3, 3)
    dig_h4 = (dig_h4 << 24) >> 20
    dig_h4 = dig_h4 | (get_char(cal3, 4) & 0x0F)

    dig_h5 = get_char(cal3, 5)
    dig_h5 = (dig_h5 << 24) >> 20
    dig_h5 = dig_h5 | (get_u_char(cal3, 4) >> 4 & 0x0F)

    dig_h6 = get_char(cal3, 6)

    # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM) + 0.575)
    time.sleep(wait_time / 1000)  # Wait the required time

    # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(addr, REG_DATA, 8)
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    # Refine temperature
    var1 = ((((temp_raw >> 3) - (dig_t1 << 1))) * (dig_t2)) >> 11
    var2 = (((((temp_raw >> 4) - (dig_t1)) * ((temp_raw >> 4) - (dig_t1))) >> 12) * (dig_t3)) >> 14

    t_fine = var1 + var2
    temperature = float(((t_fine * 5) + 128) >> 8)

    # Refine pressure and adjust for temperature
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_p6 / 32768.0
    var2 = var2 + var1 * dig_p5 * 2.0
    var2 = var2 / 4.0 + dig_p4 * 65536.0
    var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_p1
    if var1 == 0:
        pressure = 0
    else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_p9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_p8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_p7) / 16.0

    # Refine humidity
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_h4 * 64.0 + dig_h5 / 16384.0 * humidity)) * (
                dig_h2 / 65536.0 * (1.0 + dig_h6 / 67108864.0 * humidity * (1.0 + dig_h3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_h1 * humidity / 524288.0)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature / 100.0, pressure / 100.0, humidity


def main():
    (chip_id, chip_version) = read_bme280_id()
    print("Chip ID     :", chip_id)
    print("Version     :", chip_version)

    temperature, pressure, humidity = read_bme280_all()

    print("Temperature : ", temperature, "C")
    print("Pressure : ", pressure, "hPa")
    print("Humidity : ", humidity, "%")


if __name__ == "__main__":
    main()
