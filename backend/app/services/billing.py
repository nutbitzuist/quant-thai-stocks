
import logging
from typing import Optional, Dict, Any
import stripe
from app.config import settings

logger = logging.getLogger(__name__)

class StripeService:
    """Service for handling Stripe payments and subscriptions"""
    
    def __init__(self):
        self.api_key = settings.stripe_secret_key
        stripe.api_key = self.api_key
        
        if not self.api_key:
            logger.warning("Stripe API key not set")
            
    async def create_checkout_session(
        self, 
        price_id: str, 
        user_email: str,
        success_url: str,
        cancel_url: str,
        user_id: str
    ) -> Optional[str]:
        """
        Create a Stripe Checkout Session for a specific price ID.
        """
        if not self.api_key:
             return None
        
        try:
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer_email=user_email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user_id
                }
            )
            return checkout_session.url
                    
        except Exception as e:
            logger.error(f"Stripe error: {str(e)}")
            return None
            
_billing_service = None

def get_billing_service() -> StripeService:
    global _billing_service
    if _billing_service is None:
        _billing_service = StripeService()
    return _billing_service
