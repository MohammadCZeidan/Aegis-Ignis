@echo off
echo ==========================================
echo   FIRE DETECTION SERVICE - RESTART
echo ==========================================
echo.
echo Changes Applied:
echo   - Confidence threshold: 60%% ^> 30%%
echo   - Cooldown: 30s ^> 15s
echo   - Detection: Now detects lighter flames!
echo.
echo ==========================================
echo.

cd fire-detection-service
echo Starting fire detection service...
echo.
python main.py
