import hmac, hashlib, json
from ..core.config import settings

def verify_stripe_signature(payload: bytes, signature: str) -> bool:
    if not settings.stripe_webhook_secret:
        return False
    try:
        import stripe
        stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
        return True
    except Exception:
        return False

def verify_razorpay_signature(payload: bytes, signature: str) -> bool:
    if not settings.razorpay_webhook_secret:
        return False
    digest = hmac.new(settings.razorpay_webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature or "")

def normalize_provider_event(provider: str, payload: dict):
    if provider == "stripe":
        obj = payload.get("data", {}).get("object", {})
        return {"event_id": payload.get("id"), "status": payload.get("type"), "amount": (obj.get("amount_total") or obj.get("amount_paid") or 0)/100, "currency": (obj.get("currency") or "INR").upper(), "invoice_id": obj.get("metadata", {}).get("invoice_id"), "payment_id": obj.get("payment_intent") or obj.get("id")}
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    return {"event_id": payload.get("event") + ":" + str(entity.get("id")), "status": payload.get("event"), "amount": (entity.get("amount") or 0)/100, "currency": entity.get("currency") or "INR", "invoice_id": entity.get("notes", {}).get("invoice_id"), "payment_id": entity.get("id"), "order_id": entity.get("order_id")}
