payments_schema = {
    "type": "object",
    "required": [
        "Manager",
        "Scholars"
    ],
    "properties": {
        "Manager": {
            "type": "string",
            "pattern": "^ronin:"
        },
        "Scholars": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "Name",
                    "AccountAddress",
                    "ScholarPayoutAddress",
                    "ScholarPayout",
                    "ManagerPayout"
                ],
                "dependencies": {
                    "TrainerPayoutAddress": ["TrainerPayout"],
                    "TrainerPayout": ["TrainerPayoutAddress"]
                },
                "properties": {
                    "Name": {
                        "type": "string"
                    },
                    "AccountAddress": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "ScholarPayoutAddress": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "ScholarPayout": {
                        "type": "number",
                        "minimum": 1
                    },
                    "TrainerPayoutAddress": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "TrainerPayout": {
                        "type": "number",
                        "minimum": 1
                    },
                    "ManagerPayout": {
                        "type": "number",
                        "minimum": 1
                    }
                }
            }
        },
        "Donations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "Name",
                    "AccountAddress",
                    "Percent"
                ],
                "properties": {
                    "Name": {
                        "type": "string"
                    },
                    "AccountAddress": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "Percent": {
                        "type": "number",
                        "minimum": 0.01,
                        "maximum": 1
                    }
                }
            }
        }
    }
}

transfers_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "AccountAddress",
            "Transfers"
        ],
        "properties": {
            "AccountAddress": {
                "type": "string",
                "pattern": "^ronin:"
            },
            "Transfers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "AxieId",
                        "ReceiverAddress"
                    ],
                    "properties": {
                        "AxieId": {
                            "type": "number"
                        },
                        "ReceiverAddress": {
                            "type": "string",
                            "pattern": "^ronin:"
                        }
                    }
                }
            }
        }
    }
}