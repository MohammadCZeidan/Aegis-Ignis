@echo off
REM Quick Start Script for Fire Detection Model Training
REM This script guides you through the complete training process

echo.
echo ============================================================================
echo    FIRE DETECTION MODEL TRAINING - QUICK START
echo ============================================================================
echo.

REM Check if we're in the right directory
if not exist "fire_detection_train.py" (
    echo Error: Please run this script from ml_models/train/ directory
    echo.
    echo Current directory: %CD%
    echo Expected: ...\Aegis-IgnisGit\ml_models\train
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo OK - Python found
echo.

echo [2/5] Installing dependencies...
echo This may take a few minutes...
pip install ultralytics opencv-python numpy pyyaml --quiet
if errorlevel 1 (
    echo Warning: Some packages may have failed to install
    echo Try manually: pip install ultralytics opencv-python numpy pyyaml
)
echo OK - Dependencies installed
echo.

echo [3/5] Dataset Setup
echo.
echo You need a fire detection dataset to train the model.
echo.
echo Choose an option:
echo   1. I have downloaded a dataset from Roboflow (RECOMMENDED)
echo   2. Create empty structure (I'll add my own images)
echo   3. Show me how to download from Roboflow
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    set /p dataset_path="Enter path to your dataset folder (or press Enter for 'fire_dataset'): "
    if "%dataset_path%"=="" set dataset_path=fire_dataset
    
    echo Validating dataset...
    python prepare_dataset.py --output "%dataset_path%" --validate
    
    if errorlevel 1 (
        echo.
        echo Dataset validation failed. Please check the structure.
        pause
        exit /b 1
    )
    
    goto train
)

if "%choice%"=="2" (
    echo.
    set /p dataset_path="Enter folder name for dataset (default: fire_dataset): "
    if "%dataset_path%"=="" set dataset_path=fire_dataset
    
    echo Creating dataset structure...
    python prepare_dataset.py --output "%dataset_path%" --create-structure
    
    echo.
    echo Dataset structure created!
    echo.
    echo Next steps:
    echo 1. Add images to %dataset_path%\images\train\
    echo 2. Add labels to %dataset_path%\labels\train\
    echo 3. Add images to %dataset_path%\images\val\
    echo 4. Add labels to %dataset_path%\labels\val\
    echo 5. Run this script again and choose option 1
    echo.
    pause
    exit /b 0
)

if "%choice%"=="3" (
    echo.
    python prepare_dataset.py --roboflow
    echo.
    echo After downloading, extract the dataset and run this script again.
    pause
    exit /b 0
)

echo Invalid choice
pause
exit /b 1

:train
echo.
echo [4/5] Training Configuration
echo.
echo Choose training mode:
echo   1. Quick Test (10 epochs, ~5 minutes) - Test everything works
echo   2. Standard Training (100 epochs, ~30-60 mins) - Good quality
echo   3. Production Training (200 epochs, ~1-2 hours) - Best quality
echo   4. Custom settings
echo.
set /p train_choice="Enter choice (1-4): "

if "%train_choice%"=="1" (
    set epochs=10
    set batch=8
    set model=yolov8n.pt
    echo Quick test mode selected
    goto start_training
)

if "%train_choice%"=="2" (
    set epochs=100
    set batch=16
    set model=yolov8n.pt
    echo Standard training mode selected
    goto start_training
)

if "%train_choice%"=="3" (
    set epochs=200
    set batch=16
    set model=yolov8s.pt
    echo Production training mode selected
    goto start_training
)

if "%train_choice%"=="4" (
    echo.
    set /p epochs="Number of epochs (default: 100): "
    if "%epochs%"=="" set epochs=100
    
    set /p batch="Batch size (default: 16, reduce if GPU memory issues): "
    if "%batch%"=="" set batch=16
    
    echo.
    echo Choose model size:
    echo   1. yolov8n.pt - Nano (fastest, smallest)
    echo   2. yolov8s.pt - Small (recommended)
    echo   3. yolov8m.pt - Medium (best accuracy)
    set /p model_choice="Enter choice (1-3): "
    
    if "%model_choice%"=="1" set model=yolov8n.pt
    if "%model_choice%"=="2" set model=yolov8s.pt
    if "%model_choice%"=="3" set model=yolov8m.pt
    
    goto start_training
)

echo Invalid choice
pause
exit /b 1

:start_training
echo.
echo [5/5] Starting Training...
echo.
echo Configuration:
echo   Dataset: %dataset_path%\data.yaml
echo   Epochs: %epochs%
echo   Batch size: %batch%
echo   Model: %model%
echo.
echo Training will start in 3 seconds...
timeout /t 3 /nobreak >nul

python fire_detection_train.py --data "%dataset_path%\data.yaml" --epochs %epochs% --batch %batch% --model %model%

if errorlevel 1 (
    echo.
    echo Training failed! Check the errors above.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo    TRAINING COMPLETE!
echo ============================================================================
echo.
echo Your trained model is saved to:
echo   ..\weights\fire_detection.pt
echo.
echo Next steps:
echo   1. Review training results in runs\train\fire_detection\
echo   2. Test your model: python test_model.py --model ..\weights\fire_detection.pt --image test.jpg
echo   3. Deploy to production: Update .env file with ML_MODEL_PATH
echo.
echo Press any key to exit...
pause >nul
