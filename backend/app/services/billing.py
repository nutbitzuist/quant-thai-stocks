
import logging
from typing import Optional, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class LemonSqueezyService:
    """Service for handling LemonSqueezy payments and subscriptions"""
    
    BASE_URL = "https://api.lemonsqueezy.com/v1"
    
    def __init__(self):
        self.api_key = settings.lemonsqueezy_api_key
        self.store_id = settings.lemonsqueezy_store_id
        
        if not self.api_key:
            logger.warning("LemonSqueezy API key not set")
            
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def create_checkout_link(
        self, 
        variant_id: str, 
        user_email: str,
        user_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a checkout link for a specific product variant.
        Pre-fills user email and name for better UX.
        """
        if not self.api_key:
             return None
             
        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": user_email,
                        "name": user_name,
                        "custom": {
                            "user_id": user_email # Mapping via email for now
                        }
                    }
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": self.store_id
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": variant_id
                        }
                    }
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/checkouts",
                    headers=self._get_headers(),
                    json=checkout_data
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return data.get("data", {}).get("attributes", {}).get("url")
                else:
                    logger.error(f"Failed to create checkout: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"LemonSqueezy error: {str(e)}")
            return None
            
_billing_service = None

def get_billing_service() -> LemonSqueezyService:
    global _billing_service
    if _billing_service is None:
        _billing_service = LemonSqueezyService()
    return _billing_service
