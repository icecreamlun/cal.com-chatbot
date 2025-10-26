import httpx
import logging
from typing import Dict, List, Any, Optional
from calcom_chatbot.utils.config import (
    get_calcom_api_key,
    get_calcom_base_url,
    get_calcom_event_type_id
)

# logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_available_slots(date: str) -> List[Dict[str, Any]]:
    """
    Get available time slots for a specific date.
    
    Args:
        date: Date string in ISO format (YYYY-MM-DD)
        
    Returns:
        List of available slots
    """
    api_key = get_calcom_api_key()
    base_url = get_calcom_base_url()
    event_type_id = get_calcom_event_type_id()
    
    url = f"{base_url}/slots"
    
    headers = {
        "cal-api-version": "2024-08-13"
    }
    
    params = {
        "eventTypeId": event_type_id,
        "startTime": f"{date}T00:00:00Z",
        "endTime": f"{date}T23:59:59Z"
    }
    
    async with httpx.AsyncClient() as client:
        logger.info(f"📤 GET {url} | Params: {params}")
        response = await client.get(url, headers=headers, params=params)
        logger.info(f"📥 {response.status_code} | {response.text[:200]}...")
        
        response.raise_for_status()
        return response.json()


async def create_booking(
    start_time: str,
    attendee_email: str,
    attendee_name: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new booking.
    
    Args:
        start_time: Start time in ISO format (e.g., "2024-12-15T14:00:00Z")
        attendee_email: Email of the attendee
        attendee_name: Name of the attendee
        notes: Optional notes/reason for the meeting
        
    Returns:
        Booking details
    """
    api_key = get_calcom_api_key()
    base_url = get_calcom_base_url()
    event_type_id = get_calcom_event_type_id()
    
    url = f"{base_url}/bookings"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13"
    }
    
    payload = {
        "start": start_time,
        "eventTypeId": event_type_id,
        "attendee": {
            "name": attendee_name,
            "email": attendee_email,
            "timeZone": "UTC"
        },
        "metadata": {}
    }
    
    if notes:
        payload["bookingFieldsResponses"] = {
            "notes": notes
        }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"📤 POST {url} | Payload: {payload}")
            response = await client.post(url, headers=headers, json=payload)
            logger.info(f"📥 {response.status_code} | {response.text}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # 提供更详细的错误信息
            error_detail = e.response.text
            logger.error(f"❌ Cal.com API Error: {e.response.status_code}")
            logger.error(f"Error Detail: {error_detail}")
            raise Exception(f"Cal.com API error: {e.response.status_code} - {error_detail}")


async def reschedule_booking(
    booking_uid: str,
    new_start_time: str,
    rescheduling_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reschedule a booking to a new time.
    
    Args:
        booking_uid: UID of the booking to reschedule
        new_start_time: New start time in ISO format (e.g., "2024-12-20T14:00:00Z")
        rescheduling_reason: Optional reason for rescheduling
        
    Returns:
        Rescheduled booking details
    """
    api_key = get_calcom_api_key()
    base_url = get_calcom_base_url()
    
    # Cal.com V2 API: POST /v2/bookings/{uid}/reschedule
    url = f"{base_url}/bookings/{booking_uid}/reschedule"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13"
    }
    
    # Construct payload
    payload = {
        "start": new_start_time
    }
    if rescheduling_reason:
        payload["reschedulingReason"] = rescheduling_reason
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"📤 POST {url} | Payload: {payload}")
            response = await client.post(url, headers=headers, json=payload)
            logger.info(f"📥 {response.status_code} | {response.text}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"❌ Cal.com API Error: {e.response.status_code}")
            logger.error(f"Error Detail: {error_detail}")
            raise Exception(f"Cal.com API error: {e.response.status_code} - {error_detail}")


async def list_bookings(user_email: str) -> List[Dict[str, Any]]:
    """
    List all bookings for a user.
    
    Args:
        user_email: Email of the user (not used, queries all bookings for the authenticated user)
        
    Returns:
        List of bookings
    """
    api_key = get_calcom_api_key()
    base_url = get_calcom_base_url()
    
    url = f"{base_url}/bookings"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-08-13"
    }
    
    params = {
        "status": "upcoming"
    }
    
    async with httpx.AsyncClient() as client:
        logger.info(f"📤 GET {url} | Params: {params}")
        response = await client.get(url, headers=headers, params=params)
        logger.info(f"📥 {response.status_code} | {response.text}")
        
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


async def cancel_booking(booking_uid: str, cancellation_reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Cancel a booking.
    
    Args:
        booking_uid: UID of the booking to cancel
        cancellation_reason: Optional reason for cancellation
        
    Returns:
        Cancellation response
    """
    api_key = get_calcom_api_key()
    base_url = get_calcom_base_url()
    
    # Cal.com V2 API: POST /v2/bookings/{uid}/cancel
    url = f"{base_url}/bookings/{booking_uid}/cancel"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13"
    }
    
    payload = {
        "cancelSubsequentBookings": False
    }
    if cancellation_reason:
        payload["cancellationReason"] = cancellation_reason
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"📤 POST {url} | Payload: {payload}")
            response = await client.post(url, headers=headers, json=payload)
            logger.info(f"📥 {response.status_code} | {response.text}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"❌ Cal.com API Error: {e.response.status_code}")
            logger.error(f"Error Detail: {error_detail}")
            raise Exception(f"Cal.com API error: {e.response.status_code} - {error_detail}")

