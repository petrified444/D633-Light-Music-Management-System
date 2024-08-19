# bulb_config.py

BULB_DATABASE = {
    "Light B5": "192.168.1.106",
    "Light C1": "192.168.1.107",
    "Light C2": "192.168.1.108",
    "Light C3": "192.168.1.109",
    "Light D1": "192.168.1.110",
}

# Function to discover and update bulb IPs if needed
async def discover_bulbs():
    from kasa import Discover
    devices = await Discover.discover()
    for ip, dev in devices.items():
        if dev.alias in BULB_DATABASE.keys():
            BULB_DATABASE[dev.alias] = ip
    return BULB_DATABASE

# This function can be called at the start of the application to ensure we have the latest IPs