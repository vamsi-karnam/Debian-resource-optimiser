# config.py

# How often to run the monitoring/decision loop (in seconds)
LOOP_INTERVAL = 30

# Enable or disable power monitoring via INA219
ENABLE_POWER_MONITORING = True

# I2C settings for INA219 (used by Waveshare Power HAT)
INA219_I2C_BUS = 1         # Usually 1 for Raspberry Pi
INA219_I2C_ADDRESS = 0x43  # Default for many INA219 chips (adjust if needed)


# === Service Control Policy ===

# Services that are allowed to be stopped by the agent if memory/power is tight
LOW_PRIORITY_SERVICES = [
    "bluetooth.service",
    "avahi-daemon.service",
    "cups.service",
    "cron.service"
]

# Services that must never be stopped or modified
PROTECTED_SERVICES = [
    "systemd",
    "systemd-journald.service",
    "dbus.service",
    "networking.service",
    "wpa_supplicant.service",
    "ssh.service"  # If you're using remote access!
]