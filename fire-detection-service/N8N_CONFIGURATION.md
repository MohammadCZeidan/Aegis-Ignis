# N8N Webhook Configuration Guide

## Current Status

✅ **Twilio WhatsApp**: Working (alerts are being sent successfully)  
⚠️ **N8N Webhook**: Not configured (needs webhook URL)

## To Enable N8N Webhook Alerts

### Step 1: Get Your N8N Webhook URL

1. Open your N8N instance
2. Create a new workflow or open existing one
3. Add a **Webhook** trigger node
4. Configure it:
   - Method: POST
   - Path: `/webhook/fire-alert` (or your custom path)
   - Response Mode: "When Last Node Finishes"
5. **Copy the webhook URL** (e.g., `http://localhost:5678/webhook/fire-alert`)

### Step 2: Add to .env File

Open `fire-detection-service/.env` and add:

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/fire-alert
```

Or if your N8N is on a remote server:

```env
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/fire-alert
```

### Step 3: Restart the Service

Restart your Fire Detection service to load the new configuration.

### Step 4: Verify

When you restart, you should see in the logs:

```
✓ N8N webhook configured: http://localhost:5678/webhook/fire-alert
```

Instead of:

```
⚠ N8N_WEBHOOK_URL not configured. N8N alerts will be disabled.
```

## What Gets Sent to N8N

When fire is detected, the service sends a JSON payload like this:

```json
{
  "alert_type": "FIRE_EMERGENCY",
  "floor_id": 3,
  "camera_id": 1,
  "camera_name": "Camera 1",
  "room": "Office",
  "fire_type": "fire",
  "severity": "critical",
  "confidence": 0.9335,
  "timestamp": "2026-01-24T01:28:03",
  "people_count": 0,
  "people_details": [],
  "message": "🔥 FIRE ALERT - Floor 3\nLocation: Office\n...",
  "priority": "CRITICAL",
  "screenshot_path": "storage/alerts/fire_cam1_floor3_20260124_012803.jpg",
  "requires_evacuation": false,
  "action_required": true
}
```

## N8N Workflow Example

Your N8N workflow should:

1. **Webhook Trigger** - Receives the alert
2. **Switch Node** - Check `alert_type`:
   - `FIRE_EMERGENCY` → Send WhatsApp message
   - `CRITICAL_EVACUATION` → Send WhatsApp + Voice Call + SMS
3. **WhatsApp Node** - Send formatted message
4. **Voice Call Node** (if critical) - Make emergency call
5. **Response Node** - Return success

## Fixed Issues

✅ Fixed `floor_id=None` issue - now defaults to Floor 3 if not set  
✅ Added N8N webhook URL configuration to `.env`  
✅ Improved logging to show N8N status  
✅ Both `/detect-fire` endpoint and live monitoring now send alerts

## Current Behavior

- **Twilio WhatsApp**: ✅ Sending alerts successfully
- **N8N Webhook**: ⚠️ Waiting for webhook URL configuration
- **Backend Logging**: ✅ Working

Once you add `N8N_WEBHOOK_URL` to your `.env` file and restart, both Twilio and N8N alerts will work!
