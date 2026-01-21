# 🔥 Fire Detection Model Training Guide

## Complete Guide to Training Your Custom Fire Detection Model

---

## 📋 Prerequisites

### Install Dependencies
```bash
pip install ultralytics opencv-python numpy pyyaml
```

### Hardware Requirements
- **Minimum**: CPU (slow, 2-4 hours for 100 epochs)
- **Recommended**: NVIDIA GPU with 8GB+ VRAM (30-60 mins)
- **RAM**: 8GB+ recommended
- **Storage**: 5GB+ free space

---

## 🗂️ Step 1: Get a Dataset

### Option A: Download from Roboflow (Recommended - 5 minutes)

1. **Visit Roboflow Universe**
   ```
   https://universe.roboflow.com/
   ```

2. **Search for Fire Detection Datasets**
   - Search: "fire detection" or "smoke detection"
   - Recommended datasets:
     - **Fire and Smoke Detection** (1000+ images)
     - **Wildfire Detection** (500+ images)
     - **Fire Detection Computer Vision Project**

3. **Download Dataset**
   - Click on dataset → "Download"
   - Format: **YOLOv8** (important!)
   - Click "Continue" → Download ZIP

4. **Extract Dataset**
   ```bash
   # Create dataset directory
   cd ml_models/train
   mkdir fire_dataset
   
   # Extract downloaded ZIP to fire_dataset/
   # Folder structure should be:
   # fire_dataset/
   #   ├── images/
   #   │   ├── train/
   #   │   └── val/
   #   ├── labels/
   #   │   ├── train/
   #   │   └── val/
   #   └── data.yaml
   ```

5. **Validate Dataset**
   ```bash
   python prepare_dataset.py --output fire_dataset --validate
   ```

### Option B: Create Your Own Dataset (Manual - 2-3 hours)

1. **Collect Images**
   - Fire images: 500+ (flames, smoke, wildfires)
   - Non-fire images: 200+ (for negative examples)
   - Use Google Images, Pexels, or your own photos

2. **Annotate with Roboflow**
   - Sign up: https://roboflow.com/
   - Create new project
   - Upload images
   - Draw bounding boxes:
     - Class 0: `fire`
     - Class 1: `smoke`
   - Split: 80% train, 15% val, 5% test
   - Export as YOLOv8 format

3. **Download and Extract**
   ```bash
   # Same as Option A, step 4
   ```

### Option C: Use Sample Structure (Testing - 2 minutes)

```bash
cd ml_models/train
python prepare_dataset.py --output fire_dataset --create-structure
```

Then add your own images to:
- `fire_dataset/images/train/` - Training images
- `fire_dataset/labels/train/` - Training labels (YOLO format)
- `fire_dataset/images/val/` - Validation images
- `fire_dataset/labels/val/` - Validation labels

---

## 🚀 Step 2: Train the Model

### Quick Start (Test Training - 5 minutes)

```bash
cd ml_models/train

# Quick test with 10 epochs (just to verify everything works)
python fire_detection_train.py --data fire_dataset/data.yaml --epochs 10 --batch 8
```

### Full Training (Production - 1-2 hours)

```bash
# Standard training with nano model (fast, good accuracy)
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 100 \
    --batch 16 \
    --model yolov8n.pt

# With GPU (faster)
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 100 \
    --batch 32 \
    --model yolov8s.pt \
    --device 0
```

### Advanced Training Options

```bash
# High accuracy (slower, better for production)
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 200 \
    --batch 16 \
    --model yolov8m.pt \
    --patience 100 \
    --device 0 \
    --export onnx torchscript

# Fast training for testing
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 50 \
    --batch 8 \
    --model yolov8n.pt \
    --device cpu
```

### Model Sizes (Choose One)

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| `yolov8n.pt` | ⚡⚡⚡ Fastest | ⭐⭐⭐ Good | 6 MB | Edge devices, real-time |
| `yolov8s.pt` | ⚡⚡ Fast | ⭐⭐⭐⭐ Better | 22 MB | **Recommended** |
| `yolov8m.pt` | ⚡ Medium | ⭐⭐⭐⭐⭐ Best | 52 MB | Production, high accuracy |
| `yolov8l.pt` | 🐌 Slow | ⭐⭐⭐⭐⭐+ Excellent | 88 MB | Server-side only |

**Recommendation**: Start with `yolov8n.pt` for testing, use `yolov8s.pt` for production.

---

## 📊 Step 3: Monitor Training

### Training Output

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss   Instances       Size
  1/100     4.5G      1.234      0.876      1.456         142        640
  2/100     4.5G      1.123      0.765      1.345         142        640
  ...
  
Validation mAP50: 0.85, mAP50-95: 0.67
```

### Key Metrics

- **box_loss**: Lower is better (should decrease over time)
- **cls_loss**: Classification loss (should decrease)
- **mAP50**: Mean Average Precision at 50% IoU (higher is better)
- **mAP50-95**: Average across IoU thresholds (higher is better)

### Good Training Signs ✅
- Losses decrease steadily
- mAP50 > 0.7 (good)
- mAP50 > 0.85 (excellent)
- No overfitting (train/val metrics similar)

### Problems ❌
- Losses not decreasing → lower learning rate, more epochs
- mAP50 < 0.5 → need more/better data
- Val loss increasing → overfitting, reduce epochs

---

## 📁 Step 4: Find Your Trained Model

After training completes:

```
ml_models/
├── weights/
│   ├── fire_detection.pt              ← Current best model
│   └── fire_detection_best_20260121.pt ← Timestamped backup
└── train/
    └── runs/
        └── train/
            └── fire_detection/
                ├── weights/
                │   ├── best.pt         ← Best model
                │   └── last.pt         ← Last epoch
                ├── results.png         ← Training curves
                ├── confusion_matrix.png
                ├── PR_curve.png
                └── F1_curve.png
```

**Main model location**: `ml_models/weights/fire_detection.pt`

---

## 🧪 Step 5: Test Your Model

### Test on Single Image

```bash
cd ml_models/train

python test_model.py \
    --model ../weights/fire_detection.pt \
    --image test_fire.jpg
```

### Validate on Dataset

```bash
python test_model.py \
    --model ../weights/fire_detection.pt \
    --data fire_dataset/data.yaml
```

### Benchmark Speed

```bash
python test_model.py \
    --model ../weights/fire_detection.pt \
    --benchmark
```

### Full Test Suite

```bash
python test_model.py \
    --model ../weights/fire_detection.pt \
    --image test_fire.jpg \
    --data fire_dataset/data.yaml \
    --benchmark
```

---

## 🚀 Step 6: Deploy to Production

### Update .env Configuration

```bash
# In project root
cd ../..
nano .env  # or edit with your editor
```

Set:
```env
USE_ML_DETECTION=true
ML_MODEL_PATH=ml_models/weights/fire_detection.pt
FIRE_CONFIDENCE_THRESHOLD=0.5
USE_COLOR_FALLBACK=true
```

### Restart Services

```bash
# Fire detection service
cd fire-detection-service
python main_v2.py

# Live camera server
cd ..
python live_camera_detection_server.py
```

### Test Live Detection

```bash
# Test API endpoint
curl -X POST "http://localhost:8002/detect-fire-ml" \
  -F "file=@test_fire.jpg" \
  -F "camera_id=1" \
  -F "camera_name=Test Camera" \
  -F "floor_id=1" \
  -F "room_location=Test Room"
```

---

## 📊 Training Tips & Best Practices

### Data Quality > Quantity
- ✅ 500 high-quality, diverse images > 2000 similar images
- ✅ Include day/night, indoor/outdoor, various lighting
- ✅ Different types of fire: small flames, large fires, smoke
- ✅ Include challenging cases: candles, lighters, reflections

### Augmentation (Automatic)
- YOLOv8 automatically applies:
  - Random rotation
  - Random scaling
  - Color jittering
  - Mosaic augmentation

### Avoid Overfitting
- Use early stopping (default: patience=50)
- Train/val split: 80/20 minimum
- Test on completely new images
- Monitor val_loss vs train_loss

### Improve Accuracy
1. **More diverse data** - biggest impact
2. **Longer training** - 150-200 epochs
3. **Larger model** - yolov8s or yolov8m
4. **Better annotations** - precise bounding boxes
5. **Class balancing** - equal fire/smoke samples

### Speed Optimization
1. **Use yolov8n** - fastest model
2. **Lower image size** - `--imgsz 416` (trade accuracy)
3. **Export to ONNX** - `--export onnx`
4. **Use GPU** - 10-20x faster than CPU

---

## 🐛 Troubleshooting

### "CUDA out of memory"
```bash
# Reduce batch size
python fire_detection_train.py --data fire_dataset/data.yaml --batch 8
```

### "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Training very slow on CPU
```bash
# Use smaller model and fewer epochs for testing
python fire_detection_train.py --data fire_dataset/data.yaml --epochs 10 --model yolov8n.pt
```

### Low mAP scores
- Check dataset quality - review annotations
- Need more training data (500+ images minimum)
- Train longer (150-200 epochs)
- Try larger model (yolov8s or yolov8m)

### Model not detecting fire in production
- Lower confidence threshold in .env: `FIRE_CONFIDENCE_THRESHOLD=0.3`
- Check if test images similar to training data
- Retrain with more diverse dataset

---

## 📈 Expected Results

### Typical Performance (with good dataset)

| Metric | Good | Excellent | Notes |
|--------|------|-----------|-------|
| mAP50 | 0.70-0.85 | 0.85-0.95 | Detection accuracy |
| Precision | 0.75-0.85 | 0.85-0.95 | Fewer false positives |
| Recall | 0.70-0.80 | 0.80-0.90 | Catches more fires |
| Inference | 15-30ms | 10-15ms | On GPU (yolov8n) |

### Training Time Estimates

| Dataset Size | Model | Device | Time |
|--------------|-------|--------|------|
| 500 images | yolov8n | CPU | 2-3 hours |
| 500 images | yolov8n | GPU | 20-30 mins |
| 1000 images | yolov8s | CPU | 4-6 hours |
| 1000 images | yolov8s | GPU | 45-60 mins |
| 2000 images | yolov8m | GPU | 1.5-2 hours |

---

## 📚 Additional Resources

### Dataset Sources
- **Roboflow Universe**: https://universe.roboflow.com/ (recommended)
- **Kaggle**: Search "fire detection dataset"
- **Google Dataset Search**: https://datasetsearch.research.google.com/

### YOLOv8 Documentation
- **Ultralytics Docs**: https://docs.ultralytics.com/
- **Training Guide**: https://docs.ultralytics.com/modes/train/
- **Model Export**: https://docs.ultralytics.com/modes/export/

### Tools
- **Roboflow**: Image annotation and augmentation
- **Label Studio**: Open-source annotation tool
- **CVAT**: Computer Vision Annotation Tool

---

## ✅ Quick Checklist

- [ ] Install dependencies (`pip install ultralytics`)
- [ ] Download fire detection dataset from Roboflow
- [ ] Validate dataset structure
- [ ] Start training with small test (10 epochs)
- [ ] Monitor training metrics
- [ ] Full training (100+ epochs)
- [ ] Review results.png and confusion matrix
- [ ] Test model on sample images
- [ ] Validate on dataset (mAP > 0.7)
- [ ] Deploy to production
- [ ] Update .env configuration
- [ ] Test live detection

---

## 🎯 Summary

**Fastest Path (30 minutes):**
1. Download dataset from Roboflow → 5 mins
2. Validate dataset → 1 min
3. Train model (GPU, 50 epochs) → 20 mins
4. Test and deploy → 4 mins

**Production Quality (2 hours):**
1. Download/create quality dataset → 30 mins
2. Train with yolov8s, 100 epochs → 1 hour
3. Validate and fine-tune → 20 mins
4. Deploy and test → 10 mins

**Need Help?**
- Run: `python fire_detection_train.py --help`
- Test: `python test_model.py --help`
- Issues: Check troubleshooting section above

Good luck with training! 🔥🚀
