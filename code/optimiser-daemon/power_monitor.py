# power_monitor.py

import smbus
from config import INA219_I2C_BUS, INA219_I2C_ADDRESS
import time

# INA219 register constants
_REG_CALIBRATION = 0x05
_REG_CONFIG = 0x00
_REG_SHUNTVOLTAGE = 0x01
_REG_BUSVOLTAGE = 0x02
_REG_POWER = 0x03
_REG_CURRENT = 0x04

class PowerMonitor:
    def __init__(self, bus=INA219_I2C_BUS, address=INA219_I2C_ADDRESS):
        self.bus = smbus.SMBus(bus)
        self.addr = address
        self._current_lsb = 0.1524  # mA per bit
        self._power_lsb = 0.003048  # W per bit
        self._cal_value = 26868
        self._configure()

    def _write_register(self, reg, value):
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.bus.write_i2c_block_data(self.addr, reg, data)

    def _read_register(self, reg):
        data = self.bus.read_i2c_block_data(self.addr, reg, 2)
        return (data[0] << 8) | data[1]

    def _configure(self):
        self._write_register(_REG_CALIBRATION, self._cal_value)
        config = (0x01 << 13) | (0x01 << 11) | (0x0D << 7) | (0x0D << 3) | 0x07
        self._write_register(_REG_CONFIG, config)

    def get_power_state(self):
        try:
            self._write_register(_REG_CALIBRATION, self._cal_value)

            bus_voltage = (self._read_register(_REG_BUSVOLTAGE) >> 3) * 0.004  # Volts
            shunt_voltage = self._read_register(_REG_SHUNTVOLTAGE) * 0.01 / 1000  # V
            current_mA = self._read_register(_REG_CURRENT) * self._current_lsb  # mA
            power_W = self._read_register(_REG_POWER) * self._power_lsb  # W

            return {
                "voltage": round(bus_voltage, 3),
                "shunt_voltage": round(shunt_voltage, 6),
                "current": round(current_mA / 1000, 3),  # Convert to A
                "power": round(power_W, 3)
            }

        except Exception as e:
            print(f"[PowerMonitor] Error reading INA219: {e}")
            return {
                "voltage": None,
                "shunt_voltage": None,
                "current": None,
                "power": None
            }
