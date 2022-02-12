payments_schema = {
    "type": "object",
    "required": [
        "scholars"
    ],
    "properties": {
        "scholars": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "name",
                    "ronin",
                    "splits"
                ],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "ronin": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "splits": {
                        "type": "array",
                        "required": [
                            "persona",
                            "ronin",
                            "percentage"
                        ],
                        "properties": {
                            "persona": {
                                "type": "string"
                            },
                            "ronin": {
                                "type": "string",
                                "pattern": "^ronin:"
                            },
                            "percentage": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 99
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        },
        "donations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "name",
                    "ronin",
                    "percentage"
                ],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "ronin": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "percentage": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 99
                    }
                },
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}


legacy_payments_schema = {
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
                    "ScholarPercent"
                ],
                "dependencies": {
                    "TrainerPayoutAddress": ["TrainerPercent"],
                    "TrainerPercent": ["TrainerPayoutAddress"]
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
                    "ScholarPercent": {
                        "type": "number",
                        "minimum": 30,
                        "maximum": 99
                    },
                    "TrainerPayoutAddress": {
                        "type": "string",
                        "pattern": "^ronin:"
                    },
                    "TrainerPayout": {
                        "type": "number",
                        "minimum": 1
                    },
                    "TrainerPercent": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 98
                    }
                },
                "additionalProperties": False
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
                        "minimum": 1,
                        "maximum": 98
                    }
                },
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
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


breeding_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "AccountAddress",
            "Sire",
            "Matron"
        ],
        "properties": {
            "AccountAddress": {
                "type": "string",
                "pattern": "^ronin:"
            },
            "Sire": {
                "type": "number",
                "minimum": 0
            },
            "Matron": {
                "type": "number",
                "minimum": 0
            }
        }
    }
}
