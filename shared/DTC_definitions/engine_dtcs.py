DTC_STORE = {
    'P0128': {
        'description': 'Coolant Temperature Below Thermostat Regulating Temperature',
        'trigger': lambda data: data['coolant_temp'] < 70,
    },
    'P0522': {
        'description': 'Engine Oil Pressure Too Low',
        'trigger': lambda data: data['oil_pressure'] < 1.5,
    },
    'P2101': {
        'description': 'Throttle Actuator Control Motor Circuit Range/Performance',
        'trigger': lambda data: data['throttle_position'] > 95,
    },
}

