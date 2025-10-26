"""OpenAI function definitions for tool calling."""

BOOKING_DETAILS_FUNCTION = {
    "name": "collect_booking_details",
    "description": "Extract booking details from user's message including date, time, and reason for the meeting",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "The date for the meeting in YYYY-MM-DD format"
            },
            "time": {
                "type": "string",
                "description": "The time for the meeting in HH:MM format (24-hour)"
            },
            "reason": {
                "type": "string",
                "description": "The reason or purpose of the meeting"
            },
            "attendee_name": {
                "type": "string",
                "description": "The name of the person booking the meeting"
            },
            "attendee_email": {
                "type": "string",
                "description": "The email address of the person booking the meeting"
            }
        },
        "required": ["date", "time", "attendee_name", "attendee_email"]
    }
}

CONFIRM_BOOKING_FUNCTION = {
    "name": "confirm_booking",
    "description": "Confirm that the user wants to proceed with booking the meeting",
    "parameters": {
        "type": "object",
        "properties": {
            "confirmed": {
                "type": "boolean",
                "description": "Whether the user confirmed the booking"
            }
        },
        "required": ["confirmed"]
    }
}

