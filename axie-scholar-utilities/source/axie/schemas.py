payments_schema = {
    "type": "object",
    "required": [
        "Manager",
        "Scholars"
    ],
    "properties": {
        "Manager": {
            "type": "string"
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
                        "type": "string"
                    },
                    "ScholarPayoutAddress": {
                        "type": "string"
                    },
                    "ScholarPayout": {
                        "type": "number",
                        "minimum": 1
                    },
                    "TrainerPayoutAddress": {
                        "type": "string"
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
                        "type": "string"
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
