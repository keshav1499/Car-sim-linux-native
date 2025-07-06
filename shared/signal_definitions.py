# CAN signal metadata (for a single ECU frame, e.g., ID = 0x100)
SIGNAL_DEFS = {
    'rpm': {
        'start_bit': 0,
        'bit_length': 16,
        'scale': 1,
        'offset': 0,
        'unit': 'rpm',
    },
    'speed': {
        'start_bit': 16,
        'bit_length': 8,
        'scale': 1,
        'offset': 0,
        'unit': 'km/h',
    },
    'coolant_temp': {
        'start_bit': 24,
        'bit_length': 8,
        'scale': 1,
        'offset': -40,
        'unit': '°C',
    },
    'oil_pressure': {
        'start_bit': 32,
        'bit_length': 8,
        'scale': 0.1,
        'offset': 0,
        'unit': 'bar',
    },
    'throttle_position': {
        'start_bit': 40,
        'bit_length': 8,
        'scale': 0.5,
        'offset': 0,
        'unit': '%',
    }
}

