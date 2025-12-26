
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.services.billing import get_billing_service
from app.middleware.auth import require_user_id

router = APIRouter()

class CheckoutRequest(BaseModel):
    variant_id: str
    user_email: str
    user_name: Optional[str] = None

@router.post("/checkout")
async def create_checkout_link(
    req: CheckoutRequest,
    user_id: str = Depends(require_user_id)
):
    """Generate a LemonSqueezy checkout link"""
    billing = get_billing_service()
    
    url = await billing.create_checkout_link(
        variant_id=req.variant_id,
        user_email=req.user_email,
        user_name=req.user_name
    )
    
    if not url:
        raise HTTPException(status_code=500, detail="Failed to create checkout link")
        
    return {"url": url}
