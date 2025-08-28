DTC_STORE = {
    "U1001": {
        "description": "Bluetooth module error",
        "trigger": lambda data: data.get("bluetooth_status") == "ERROR",
    },
    "U1002": {
        "description": "Speaker circuit fault",
        "trigger": lambda data: data.get("speaker_status") == "FAULT",
    },
    "U1003": {
        "description": "Media decoder failure",
        "trigger": lambda data: data.get("decoder_status") == "FAIL",
    },
}