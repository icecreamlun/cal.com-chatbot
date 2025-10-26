import httpx
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from calcom_chatbot.utils.config import (
    get_calcom_api_key,
    get_calcom_base_url,
    get_calcom_event_type_id
)

# 配置日志
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
    
    # 根据官方文档：GET /v2/slots
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
        # 打印请求详情
        logger.info("=" * 60)
        logger.info("📤 Cal.com API Request - GET SLOTS")
        logger.info("=" * 60)
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Params: {json.dumps(params, indent=2)}")
        logger.info("=" * 60)
        
        response = await client.get(url, headers=headers, params=params)
        
        # 打印响应详情
        logger.info("📥 Cal.com API Response")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text[:500]}...")  # 只打印前500字符
        logger.info("=" * 60)
        
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
    
    # Cal.com V2 API官方格式（根据官方文档）
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
    
    # 添加notes到bookingFieldsResponses中
    if notes:
        payload["bookingFieldsResponses"] = {
            "notes": notes
        }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 打印请求详情
            logger.info("=" * 60)
            logger.info("📤 Cal.com API Request - CREATE BOOKING")
            logger.info("=" * 60)
            logger.info(f"URL: {url}")
            logger.info(f"Headers: {json.dumps(headers, indent=2)}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            logger.info("=" * 60)
            
            response = await client.post(url, headers=headers, json=payload)
            
            # 打印响应详情
            logger.info("📥 Cal.com API Response")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
            logger.info("=" * 60)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # 提供更详细的错误信息
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
    
    # 根据官方文档：GET /v2/bookings
    url = f"{base_url}/bookings"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "cal-api-version": "2024-08-13"
    }
    
    # 只使用status参数，不指定attendeeEmail
    # 这样会返回所有你作为主机(host)的bookings
    params = {
        "status": "upcoming"
    }
    
    async with httpx.AsyncClient() as client:
        # 打印请求详情
        logger.info("=" * 60)
        logger.info("📤 Cal.com API Request - LIST BOOKINGS")
        logger.info("=" * 60)
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Params: {json.dumps(params, indent=2)}")
        logger.info("=" * 60)
        
        response = await client.get(url, headers=headers, params=params)
        
        # 打印响应详情
        logger.info("📥 Cal.com API Response")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text}")
        logger.info("=" * 60)
        
        response.raise_for_status()
        data = response.json()
        # V2 API返回格式：{"status": "success", "data": [...]}
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
    
    # 构建payload（根据官方文档）
    payload = {
        "cancelSubsequentBookings": False
    }
    if cancellation_reason:
        payload["cancellationReason"] = cancellation_reason
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 打印请求详情
            logger.info("=" * 60)
            logger.info("📤 Cal.com API Request - CANCEL BOOKING")
            logger.info("=" * 60)
            logger.info(f"URL: {url}")
            logger.info(f"Headers: {json.dumps(headers, indent=2)}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            logger.info("=" * 60)
            
            # POST request (not DELETE!)
            response = await client.post(url, headers=headers, json=payload)
            
            # 打印响应详情
            logger.info("📥 Cal.com API Response")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
            logger.info("=" * 60)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # 提供更详细的错误信息
            error_detail = e.response.text
            logger.error(f"❌ Cal.com API Error: {e.response.status_code}")
            logger.error(f"Error Detail: {error_detail}")
            raise Exception(f"Cal.com API error: {e.response.status_code} - {error_detail}")

