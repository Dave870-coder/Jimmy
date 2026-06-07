"""WhatsApp QR Code API Routes."""

import base64
import logging
import uuid
from io import BytesIO
from typing import Optional

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None
    ImageWriter = None

from fastapi import APIRouter, HTTPException, Request, WebSocket
from pydantic import BaseModel

from src.bot.whatsapp.connection_manager import get_connection_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/whatsapp-qr", tags=["WhatsApp QR"])


class StartConnectionRequest(BaseModel):
    """Start connection request."""
    name: str = "WhatsApp Connection"


class ConnectionResponse(BaseModel):
    """Connection response."""
    connection_id: str
    status: str
    phone_number: str = None
    is_active: bool = False
    error_message: str = None


class QRCodeResponse(BaseModel):
    """QR code response."""
    connection_id: str
    qr_code_data: str  # base64 encoded PNG
    barcode_data: Optional[str] = None
    connect_url: Optional[str] = None
    status: str
    expires_in_seconds: int = 300


def _generate_barcode_image(data: str) -> Optional[str]:
    """Generate a barcode PNG as base64 when the dependency is available."""
    if not barcode or not ImageWriter:
        return None

    try:
        buffer = BytesIO()
        barcode_obj = barcode.get("code128", data, writer=ImageWriter())
        barcode_obj.write(buffer, options={"write_text": False})
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logger.warning(f"Barcode generation failed: {e}")
        return None


@router.post("/start-connection")
async def start_connection(request: StartConnectionRequest, http_request: Request) -> dict:
    """
    Start a new WhatsApp connection.
    
    Returns QR code to scan.
    
    ### Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
      -H "Content-Type: application/json" \
      -d '{"name": "My WhatsApp Bot"}'
    ```
    """
    try:
        manager = await get_connection_manager()
        connection_id = str(uuid.uuid4())
        connect_url = str(http_request.base_url).rstrip("/") + f"/api/v1/whatsapp-qr/qr-code/{connection_id}"
        
        connection_info = await manager.start_connection(connection_id)
        qr_code = manager.get_qr_code(connection_id)
        barcode_data = _generate_barcode_image(connect_url)
        
        logger.info(f"🚀 Started connection {connection_id}")
        
        return {
            "status": "success",
            "connection_id": connection_id,
            "connect_url": connect_url,
            "qr_code_data": f"data:image/png;base64,{qr_code}" if qr_code else None,
            "message": "Scan the QR code with WhatsApp to connect",
            "has_qr_code": qr_code is not None,
            "has_barcode": barcode_data is not None,
            "barcode_data": f"data:image/png;base64,{barcode_data}" if barcode_data else None,
            "connection_info": connection_info,
        }
    
    except Exception as e:
        logger.error(f"❌ Error starting connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr-code/{connection_id}")
async def get_qr_code(connection_id: str, http_request: Request) -> dict:
    """
    Get QR code for a connection.
    
    ### Example:
    ```bash
    curl http://localhost:8000/api/v1/whatsapp-qr/qr-code/{connection_id}
    ```
    """
    try:
        manager = await get_connection_manager()
        qr_data = manager.get_qr_code(connection_id)
        connect_url = str(http_request.base_url).rstrip("/") + f"/api/v1/whatsapp-qr/qr-code/{connection_id}"
        barcode_data = _generate_barcode_image(connect_url)
        
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found or expired")
        
        logger.info(f"📱 QR code requested for {connection_id}")
        
        return {
            "connection_id": connection_id,
            "qr_code_data": f"data:image/png;base64,{qr_data}",
            "barcode_data": f"data:image/png;base64,{barcode_data}" if barcode_data else None,
            "connect_url": connect_url,
            "message": "Scan this QR code with WhatsApp to connect",
            "expires_in_seconds": 300,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting QR code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{connection_id}")
async def get_connection_status(connection_id: str) -> dict:
    """
    Get current connection status.
    
    Status values:
    - `disconnected`: Not connected
    - `waiting_qr`: Waiting for QR code generation
    - `qr_ready`: QR code ready to scan
    - `scanned`: QR code has been scanned
    - `authenticated`: Successfully authenticated
    - `error`: Error occurred
    
    ### Example:
    ```bash
    curl http://localhost:8000/api/v1/whatsapp-qr/status/{connection_id}
    ```
    """
    try:
        manager = await get_connection_manager()
        status = manager.get_connection_status(connection_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        logger.info(f"📊 Status check for {connection_id}: {status['status']}")
        
        return {
            "status": "success",
            "connection_status": status,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/authenticate/{connection_id}")
async def authenticate(connection_id: str, timeout: int = 60) -> dict:
    """
    Wait for QR code to be scanned and authenticated.
    
    This endpoint will block until:
    - User scans the QR code and authenticates (success)
    - Timeout is reached (failure)
    - Error occurs (failure)
    
    ### Parameters:
    - `timeout`: Max seconds to wait (default: 60)
    
    ### Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/whatsapp-qr/authenticate/{connection_id}?timeout=120
    ```
    """
    try:
        manager = await get_connection_manager()
        
        logger.info(f"⏳ Starting authentication wait for {connection_id}...")
        authenticated = await manager.wait_for_authentication(connection_id, timeout)
        
        status = manager.get_connection_status(connection_id)
        
        if authenticated:
            logger.info(f"✅ Successfully authenticated: {status['phone_number']}")
            return {
                "status": "success",
                "message": "WhatsApp connection authenticated",
                "phone_number": status["phone_number"],
                "connection_status": status,
            }
        else:
            logger.error(f"❌ Authentication failed: {status['error_message']}")
            return {
                "status": "failed",
                "message": "Authentication failed",
                "error": status["error_message"],
                "connection_status": status,
            }
    
    except Exception as e:
        logger.error(f"❌ Error during authentication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_all_connections() -> dict:
    """
    Get all active WhatsApp connections.
    
    ### Example:
    ```bash
    curl http://localhost:8000/api/v1/whatsapp-qr/connections
    ```
    """
    try:
        manager = await get_connection_manager()
        connections = manager.get_all_connections()
        
        logger.info(f"📊 Retrieved {len(connections)} connections")
        
        return {
            "status": "success",
            "total": len(connections),
            "connections": connections,
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/disconnect/{connection_id}")
async def disconnect(connection_id: str) -> dict:
    """
    Disconnect a WhatsApp connection.
    
    ### Example:
    ```bash
    curl -X DELETE http://localhost:8000/api/v1/whatsapp-qr/disconnect/{connection_id}
    ```
    """
    try:
        manager = await get_connection_manager()
        manager.disconnect(connection_id)
        
        logger.info(f"🔌 Disconnected: {connection_id}")
        
        return {
            "status": "success",
            "message": f"Connection {connection_id} disconnected",
        }
    
    except Exception as e:
        logger.error(f"❌ Error disconnecting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """
    WebSocket endpoint for real-time connection status updates.
    
    Sends status updates whenever connection state changes.
    
    ### Example:
    ```javascript
    const ws = new WebSocket(`ws://localhost:8000/api/v1/whatsapp-qr/ws/${connectionId}`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Status:', data.status);
    };
    ```
    """
    try:
        await websocket.accept()
        logger.info(f"🔗 WebSocket connected: {connection_id}")
        
        manager = await get_connection_manager()
        last_status = None
        
        while True:
            # Check status every 1 second
            import asyncio
            await asyncio.sleep(1)
            
            status = manager.get_connection_status(connection_id)
            
            if not status:
                await websocket.send_json({
                    "type": "error",
                    "message": "Connection not found",
                })
                break
            
            # Only send if status changed
            if status != last_status:
                await websocket.send_json({
                    "type": "status_update",
                    "status": status,
                })
                last_status = status
                logger.info(f"📤 Sent status update: {status['status']}")
                
                # Close if authenticated or error
                if status["status"] in ["authenticated", "error"]:
                    await websocket.send_json({
                        "type": "complete",
                        "message": f"Connection {status['status']}",
                    })
                    break
    
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close(code=1000)
        except:
            pass
