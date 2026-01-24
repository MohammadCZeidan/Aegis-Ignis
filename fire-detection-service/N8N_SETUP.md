# N8N Integration Guide

## Quick Setup

To enable N8N webhook integration for WhatsApp/Voice alerts:

1. **Set N8N_WEBHOOK_URL in your `.env` file:**
   ```env
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/fire-alert
   ```
   Or for remote N8N instance:
   ```env
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/fire-alert
   ```

2. **Create N8N Webhook Workflow:**
   - Open N8N
   - Create a new workflow
   - Add a "Webhook" trigger node
   - Copy the webhook URL
   - Add WhatsApp/SMS/Voice call nodes as needed
   - Activate the workflow

3. **Restart the Fire Detection Service:**
   ```bash
   python main_v2.py
   ```

## Verification

Check the startup logs - you should see:
```
✓ N8N Integration: Enabled
  N8N Webhook URL: http://localhost:5678/webhook/fire-alert
```

If you see:
```
⚠ N8N_WEBHOOK_URL not configured - alerts will be disabled
```
Then N8N is not configured. Check your `.env` file.

## Alert Payload Format

When fire is detected, the service sends this JSON to N8N:

```json
{
  "alert_type": "FIRE_EMERGENCY",
  "floor_id": 3,
  "camera_id": 1,
  "camera_name": "Camera 1",
  "room": "Room 101",
  "fire_type": "fire",
  "severity": "critical",
  "confidence": 0.85,
  "timestamp": "2026-01-24T01:10:10",
  "people_count": 5,
  "people_details": [...],
  "message": "🔥 FIRE ALERT - Floor 3...",
  "priority": "CRITICAL",
  "screenshot_path": "storage/alerts/fire_cam1_floor3_20260124_011010.jpg",
  "requires_evacuation": true,
  "action_required": true
}
```

## Critical Evacuation Alerts

When fire is detected AND people are present, an additional alert is sent:

```json
{
  "alert_type": "CRITICAL_EVACUATION",
  "floor_id": 3,
  "camera_id": 1,
  "people_count": 5,
  "fire_confidence": 0.85,
  "priority": "EMERGENCY",
  "trigger_voice_call": true,
  "trigger_whatsapp": true,
  "trigger_sms": true
}
```
