"""WhatsApp Live Connection Manager."""

import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

from src.bot.whatsapp.qr_auth import get_qr_auth, QRCodeSession

logger = logging.getLogger(__name__)


class ConnectionStatus(str, Enum):
    """Connection status enum."""
    DISCONNECTED = "disconnected"
    WAITING_QR = "waiting_qr"
    QR_READY = "qr_ready"
    SCANNED = "scanned"
    AUTHENTICATED = "authenticated"
    ERROR = "error"


class WhatsAppConnection:
    """Represents a WhatsApp connection."""
    
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.status = ConnectionStatus.DISCONNECTED
        self.phone_number: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.authenticated_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.session_id: Optional[str] = None
        self.is_active = False


class WhatsAppConnectionManager:
    """Manages live WhatsApp connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.connections: Dict[str, WhatsAppConnection] = {}
        self.qr_auth = None
        logger.info("✅ WhatsApp Connection Manager initialized")
    
    async def initialize(self):
        """Initialize the connection manager."""
        self.qr_auth = await get_qr_auth()
        logger.info("🔗 Connection manager ready")
    
    async def start_connection(self, connection_id: str) -> Dict:
        """Start a new WhatsApp connection."""
        try:
            logger.info(f"🚀 Starting WhatsApp connection {connection_id}...")
            
            # Create connection object
            connection = WhatsAppConnection(connection_id)
            self.connections[connection_id] = connection
            
            # Set status to waiting for QR
            connection.status = ConnectionStatus.WAITING_QR
            
            # Generate QR code
            connection.session_id = connection_id
            qr_data = await self.qr_auth.generate_qr_code(connection_id)
            
            if qr_data:
                connection.status = ConnectionStatus.QR_READY
                logger.info(f"✅ QR code ready for connection {connection_id}")
            else:
                connection.status = ConnectionStatus.ERROR
                connection.error_message = "Failed to generate QR code"
                logger.error(f"❌ Failed to generate QR code for {connection_id}")
            
            return self._format_connection(connection)
        
        except Exception as e:
            logger.error(f"❌ Error starting connection: {e}")
            if connection_id in self.connections:
                self.connections[connection_id].status = ConnectionStatus.ERROR
                self.connections[connection_id].error_message = str(e)
            raise

    async def wait_for_authentication(self, connection_id: str, timeout: int = 60) -> bool:
        """Wait for user to authenticate via QR code."""
        if connection_id not in self.connections:
            logger.error(f"❌ Connection {connection_id} not found")
            return False
        
        connection = self.connections[connection_id]
        
        try:
            logger.info(f"⏳ Waiting for authentication on {connection_id}...")
            
            # Wait for authentication
            authenticated = await self.qr_auth.wait_for_authentication(connection_id, timeout)
            
            if authenticated:
                session = self.qr_auth.get_session_status(connection_id)
                connection.status = ConnectionStatus.AUTHENTICATED
                connection.authenticated_at = datetime.utcnow()
                connection.phone_number = session.get("phone_number") if session else None
                connection.is_active = True
                logger.info(f"✅ Authenticated: {connection.phone_number}")
                return True
            else:
                connection.status = ConnectionStatus.ERROR
                session_status = self.qr_auth.get_session_status(connection_id)
                connection.error_message = session_status.get("error_message") if session_status else "Authentication failed"
                logger.error(f"❌ Authentication failed: {connection.error_message}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error during authentication: {e}")
            connection.status = ConnectionStatus.ERROR
            connection.error_message = str(e)
            return False

    def get_connection_status(self, connection_id: str) -> Optional[Dict]:
        """Get current connection status."""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            "connection_id": connection.connection_id,
            "status": connection.status.value,
            "phone_number": connection.phone_number,
            "is_active": connection.is_active,
            "created_at": connection.created_at.isoformat(),
            "authenticated_at": connection.authenticated_at.isoformat() if connection.authenticated_at else None,
            "error_message": connection.error_message,
        }

    def get_qr_code(self, connection_id: str) -> Optional[str]:
        """Get QR code for connection."""
        if not self.qr_auth:
            return None
        
        session_status = self.qr_auth.get_session_status(connection_id)
        if session_status and "qr_code_data" in session_status:
            return session_status["qr_code_data"]
        
        return None

    def disconnect(self, connection_id: str):
        """Disconnect a WhatsApp connection."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.is_active = False
            connection.status = ConnectionStatus.DISCONNECTED
            logger.info(f"🔌 Disconnected: {connection_id}")
            
            # Cleanup
            self.qr_auth.cleanup_session(connection_id)

    def get_all_connections(self) -> List[Dict]:
        """Get all active connections."""
        return [self._format_connection(conn) for conn in self.connections.values()]

    def _format_connection(self, connection: WhatsAppConnection) -> Dict:
        """Format connection for response."""
        return {
            "connection_id": connection.connection_id,
            "status": connection.status.value,
            "phone_number": connection.phone_number,
            "is_active": connection.is_active,
            "created_at": connection.created_at.isoformat(),
            "authenticated_at": connection.authenticated_at.isoformat() if connection.authenticated_at else None,
            "error_message": connection.error_message,
        }


# Global connection manager instance
connection_manager: Optional[WhatsAppConnectionManager] = None


async def get_connection_manager() -> WhatsAppConnectionManager:
    """Get connection manager instance."""
    global connection_manager
    if connection_manager is None:
        connection_manager = WhatsAppConnectionManager()
        await connection_manager.initialize()
    return connection_manager
