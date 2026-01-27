"""
Test to verify fire detection sensitivity settings
Tests if the detection logic can identify bright flames/lighters
"""
import cv2
import numpy as np

print("=" * 60)
print("   FIRE DETECTION SENSITIVITY TEST")
print("=" * 60)
print()

# Simulate a bright flame (like in your images)
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

# Create a bright spot (simulating lighter flame)
# Your images show a very bright white-yellow center
cv2.circle(test_frame, (320, 240), 30, (255, 255, 255), -1)  # Bright white center
cv2.circle(test_frame, (320, 240), 40, (100, 200, 255), -1)  # Yellow-orange glow
cv2.circle(test_frame, (320, 240), 25, (150, 220, 255), -1)  # Bright yellow

# Convert to HSV
hsv = cv2.cvtColor(test_frame, cv2.COLOR_BGR2HSV)

print("Testing color ranges...")
print()

# Test bright white detection (NEW - for lighters)
lower_white = np.array([0, 0, 170])
upper_white = np.array([180, 90, 255])
mask_white = cv2.inRange(hsv, lower_white, upper_white)
white_pixels = np.sum(mask_white > 0)
print(f"✓ Bright White Detection: {white_pixels} pixels")

# Test orange
lower_orange = np.array([3, 30, 80])
upper_orange = np.array([30, 255, 255])
mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
orange_pixels = np.sum(mask_orange > 0)
print(f"✓ Orange Detection: {orange_pixels} pixels")

# Test red
lower_red = np.array([0, 30, 80])
upper_red = np.array([12, 255, 255])
mask_red = cv2.inRange(hsv, lower_red, upper_red)
red_pixels = np.sum(mask_red > 0)
print(f"✓ Red Detection: {red_pixels} pixels")

# Test yellow
lower_yellow = np.array([12, 30, 80])
upper_yellow = np.array([40, 255, 255])
mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
yellow_pixels = np.sum(mask_yellow > 0)
print(f"✓ Yellow Detection: {yellow_pixels} pixels")

# Combined mask
mask = cv2.bitwise_or(mask_white, cv2.bitwise_or(mask_orange, cv2.bitwise_or(mask_red, mask_yellow)))
total_pixels = np.sum(mask > 0)

print()
print("-" * 60)
print(f"TOTAL DETECTED PIXELS: {total_pixels}")
print()

# Check if it meets minimum area threshold
MIN_AREA = 30  # New ultra-sensitive threshold
if total_pixels >= MIN_AREA:
    print(f"[OK] DETECTION SUCCESSFUL!")
    print(f"   Detected {total_pixels} pixels (threshold: {MIN_AREA})")
    
    # Calculate confidence
    frame_area = 480 * 640
    percentage = (total_pixels / frame_area) * 100
    confidence = min(max(percentage / 1.5, 0.4), 1.0)
    
    print(f"   Area: {percentage:.2f}% of frame")
    print(f"   Confidence: {confidence * 100:.1f}%")
    print()
    print("FIRE DETECTED! System would trigger alert.")
else:
    print(f"[ERROR] NOT DETECTED")
    print(f"   Only {total_pixels} pixels (need {MIN_AREA})")

print()
print("=" * 60)
print("   TEST COMPLETE")
print("=" * 60)
print()
print("Based on your images showing bright flames,")
print("the system should now detect them!")
print()
print("Next steps:")
print("1. Connect camera to your system")
print("2. Run: python main.py")
print("3. Test with lighter or bright light")
print("4. Check dashboard for alerts")
