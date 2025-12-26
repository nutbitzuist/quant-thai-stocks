
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.services.billing import get_billing_service
from app.middleware.auth import require_user_id

router = APIRouter()

class CheckoutRequest(BaseModel):
    price_id: str
    user_email: str
    success_url: str
    cancel_url: str

@router.post("/checkout")
async def create_checkout_link(
    req: CheckoutRequest,
    user_id: str = Depends(require_user_id)
):
    """Generate a Stripe checkout link"""
    billing = get_billing_service()
    
    url = await billing.create_checkout_session(
        price_id=req.price_id,
        user_email=req.user_email,
        success_url=req.success_url,
        cancel_url=req.cancel_url,
        user_id=user_id
    )
    
    if not url:
        raise HTTPException(status_code=500, detail="Failed to create checkout link")
        
    return {"url": url}

class PortalRequest(BaseModel):
    user_email: str
    return_url: str

@router.post("/portal")
async def create_portal_link(
    req: PortalRequest,
    user_id: str = Depends(require_user_id)
):
    """Generate a Stripe Customer Portal link"""
    billing = get_billing_service()
    
    url = await billing.create_portal_session(
        user_email=req.user_email,
        return_url=req.return_url
    )
    
    if not url:
        raise HTTPException(status_code=404, detail="Customer not found or failed to create portal")
        
    return {"url": url}
