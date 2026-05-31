"""WhatsApp QR Code Authentication using Selenium & WhatsApp Web."""

import asyncio
import base64
import json
import logging
import qrcode
import time
from io import BytesIO
from typing import Optional, Dict, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    webdriver = None
    By = None
    WebDriverWait = None
    EC = None

logger = logging.getLogger(__name__)


@dataclass
class QRCodeSession:
    """QR Code session data."""
    session_id: str
    qr_code_data: Optional[str] = None  # base64 encoded PNG
    status: str = "waiting"  # waiting, scanned, authenticated, failed
    created_at: datetime = None
    expires_at: datetime = None
    phone_number: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    def is_expired(self) -> bool:
        """Check if QR code session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "error_message": self.error_message,
            "has_qr": self.qr_code_data is not None,
        }


class WhatsAppQRCodeAuth:
    """WhatsApp authentication using QR code (WhatsApp Web method)."""

    def __init__(self):
        """Initialize QR code authenticator."""
        self.sessions: Dict[str, QRCodeSession] = {}
        self.driver: Optional[webdriver.Chrome] = None
        self.connection_callbacks = []
        logger.info("✅ WhatsApp QR Code authenticator initialized")

    def add_connection_callback(self, callback: Callable):
        """Add callback for when connection is established."""
        self.connection_callbacks.append(callback)

    async def generate_qr_code(self, session_id: str) -> str:
        """Generate QR code for WhatsApp Web connection."""
        try:
            logger.info(f"🔐 Generating QR code for session {session_id}...")
            
            # Create or get session
            if session_id not in self.sessions:
                self.sessions[session_id] = QRCodeSession(session_id=session_id)
            
            session = self.sessions[session_id]
            
            # Initialize Selenium WebDriver with headless Chrome
            if webdriver is None:
                session.error_message = "Selenium not installed. Install with: pip install selenium"
                session.status = "failed"
                logger.error(f"❌ Selenium not installed for session {session_id}")
                return None
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-gpu")
            # Use headless mode for server environment
            chrome_options.add_argument("--headless=new")
            
            # Initialize WebDriver
            logger.info(f"📱 Starting Chrome for WhatsApp Web session {session_id}...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to WhatsApp Web
            self.driver.get("https://web.whatsapp.com")
            
            session.status = "waiting"
            logger.info(f"🌐 WhatsApp Web loaded, waiting for QR code...")
            
            # Wait for QR code to appear
            qr_wait_time = 30  # 30 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < qr_wait_time:
                try:
                    # Find QR code image element
                    qr_elements = self.driver.find_elements(By.CSS_SELECTOR, "canvas")
                    
                    if qr_elements:
                        # Extract QR code from canvas
                        qr_code_image = qr_elements[0].screenshot_as_png
                        qr_code_base64 = base64.b64encode(qr_code_image).decode('utf-8')
                        
                        session.qr_code_data = qr_code_base64
                        session.status = "ready"
                        
                        logger.info(f"✅ QR code generated for session {session_id}")
                        return qr_code_base64
                    
                except Exception as e:
                    logger.debug(f"Waiting for QR code: {e}")
                    await asyncio.sleep(1)
            
            session.error_message = "QR code generation timeout"
            session.status = "failed"
            logger.error(f"❌ QR code timeout for session {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generating QR code: {e}")
            if session_id in self.sessions:
                self.sessions[session_id].error_message = str(e)
                self.sessions[session_id].status = "failed"
            return None

    async def wait_for_authentication(self, session_id: str, timeout: int = 60) -> bool:
        """Wait for user to scan QR code and authenticate."""
        if session_id not in self.sessions:
            logger.error(f"❌ Session {session_id} not found")
            return False
        
        session = self.sessions[session_id]
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    # Check if authenticated (main chat page loaded)
                    main_chat = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='chat-list']")
                    
                    if main_chat:
                        # Authenticated! Extract phone number
                        try:
                            profile_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='wds-drawer-header-button']")
                            # Phone number is in title or data attribute
                            phone = profile_element.get_attribute("aria-label") or "connected"
                            session.phone_number = phone
                        except:
                            session.phone_number = "connected"
                        
                        session.status = "authenticated"
                        logger.info(f"✅ WhatsApp authenticated for session {session_id}: {session.phone_number}")
                        
                        # Call connection callbacks
                        for callback in self.connection_callbacks:
                            try:
                                await callback(session) if asyncio.iscoroutinefunction(callback) else callback(session)
                            except Exception as cb_error:
                                logger.error(f"Error in connection callback: {cb_error}")
                        
                        return True
                    
                    # Check if scanned
                    if session.status == "waiting":
                        session.status = "scanned"
                        logger.info(f"📱 QR code scanned for session {session_id}")
                
                except Exception as e:
                    logger.debug(f"Waiting for authentication: {e}")
                
                await asyncio.sleep(2)
            
            session.error_message = "Authentication timeout"
            session.status = "failed"
            logger.error(f"❌ Authentication timeout for session {session_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for authentication: {e}")
            session.error_message = str(e)
            session.status = "failed"
            return False
        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass

    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current session status."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if session.is_expired():
            del self.sessions[session_id]
            return None
        
        data = session.to_dict()
        if session.qr_code_data:
            data["qr_code_data"] = session.qr_code_data
        
        return data

    def cleanup_session(self, session_id: str):
        """Cleanup session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass

    def generate_static_qr_code(self, data: str) -> str:
        """Generate a static QR code from data."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return qr_base64
        except Exception as e:
            logger.error(f"❌ Error generating static QR code: {e}")
            return None


# Global QR code authenticator instance
qr_auth: Optional[WhatsAppQRCodeAuth] = None


async def get_qr_auth() -> WhatsAppQRCodeAuth:
    """Get QR code authenticator instance."""
    global qr_auth
    if qr_auth is None:
        qr_auth = WhatsAppQRCodeAuth()
    return qr_auth
