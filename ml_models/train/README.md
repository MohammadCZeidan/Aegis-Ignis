# 🔥 Fire Detection Model Training

Train your own custom YOLOv8 fire detection model for the Aegis-Ignis system.

## 🚀 Quick Start (3 Steps)

### Windows Users (Easiest)
```bash
# Just run the batch script and follow the prompts
train.bat
```

### All Platforms
```bash
# 1. Get dataset from Roboflow
python prepare_dataset.py --roboflow

# 2. Validate dataset
python prepare_dataset.py --output fire_dataset --validate

# 3. Train model
python fire_detection_train.py --data fire_dataset/data.yaml
```

**Done! Model saved to:** `../weights/fire_detection.pt`

---

## 📁 Files in This Directory

| File | Purpose |
|------|---------|
| **fire_detection_train.py** | Main training script |
| **prepare_dataset.py** | Dataset preparation and validation |
| **test_model.py** | Test and validate trained models |
| **train.bat** | Windows quick start script |
| **TRAINING_GUIDE.md** | Complete training guide |

---

## 📖 Documentation

**New to model training?** Read the complete guide:
- [**TRAINING_GUIDE.md**](TRAINING_GUIDE.md) - Step-by-step instructions

---

## ⚡ Common Commands

### Prepare Dataset
```bash
# Show download instructions
python prepare_dataset.py --roboflow

# Create empty structure
python prepare_dataset.py --output fire_dataset --create-structure

# Validate existing dataset
python prepare_dataset.py --output fire_dataset --validate
```

### Train Model
```bash
# Quick test (10 epochs)
python fire_detection_train.py --data fire_dataset/data.yaml --epochs 10

# Standard training (100 epochs)
python fire_detection_train.py --data fire_dataset/data.yaml

# Production training (best quality)
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 200 \
    --model yolov8s.pt \
    --batch 32

# With export
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --export onnx torchscript
```

### Test Model
```bash
# Test on image
python test_model.py --model ../weights/fire_detection.pt --image test_fire.jpg

# Validate on dataset
python test_model.py --model ../weights/fire_detection.pt --data fire_dataset/data.yaml

# Benchmark speed
python test_model.py --model ../weights/fire_detection.pt --benchmark

# Full test suite
python test_model.py \
    --model ../weights/fire_detection.pt \
    --image test_fire.jpg \
    --data fire_dataset/data.yaml \
    --benchmark
```

---

## 📊 Recommended Datasets

### Roboflow Universe (Recommended)
1. Visit: https://universe.roboflow.com/
2. Search: "fire detection" or "smoke detection"
3. Choose dataset with 500+ images
4. Download format: **YOLOv8**
5. Extract to `fire_dataset/`

### Popular Datasets
- **Fire and Smoke Detection** (1000+ images)
- **Wildfire Detection Dataset** (500+ images)  
- **Fire Detection Computer Vision Project**

---

## 🎯 Model Recommendations

| Scenario | Model | Epochs | Batch | Time (GPU) |
|----------|-------|--------|-------|------------|
| **Quick Test** | yolov8n.pt | 10 | 8 | 5 mins |
| **Development** | yolov8n.pt | 100 | 16 | 30 mins |
| **Production** | yolov8s.pt | 100-150 | 16 | 45-60 mins |
| **Best Quality** | yolov8m.pt | 200 | 16 | 1.5-2 hrs |
| **Edge Device** | yolov8n.pt | 150 | 16 | 40 mins |

---

## 📈 Expected Results

Good training results:
- **mAP50**: 0.75-0.90 (detection accuracy)
- **Precision**: 0.80-0.95 (fewer false alarms)
- **Recall**: 0.75-0.90 (catches fires)
- **Speed**: 10-30ms per frame (on GPU)

---

## 🐛 Troubleshooting

### Common Issues

**"CUDA out of memory"**
```bash
python fire_detection_train.py --data fire_dataset/data.yaml --batch 8
```

**"No module named 'ultralytics'"**
```bash
pip install ultralytics opencv-python numpy pyyaml
```

**Training very slow**
- Use GPU instead of CPU (10-20x faster)
- Reduce epochs for testing: `--epochs 10`
- Use smaller model: `--model yolov8n.pt`

**Low accuracy (mAP < 0.5)**
- Need more training data (500+ images)
- Train longer (150-200 epochs)
- Use larger model (yolov8s or yolov8m)
- Check annotation quality

---

## 🔧 Advanced Options

### Custom Training Parameters
```bash
python fire_detection_train.py \
    --data fire_dataset/data.yaml \
    --epochs 150 \
    --batch 32 \
    --model yolov8s.pt \
    --patience 100 \
    --save-period 20 \
    --device 0 \
    --export onnx
```

### Available Arguments
- `--data`: Dataset YAML file (required)
- `--epochs`: Number of training epochs (default: 100)
- `--batch`: Batch size (default: 16)
- `--model`: Base model (n/s/m/l/x, default: yolov8n.pt)
- `--patience`: Early stopping patience (default: 50)
- `--save-period`: Save every N epochs (default: 10)
- `--device`: 0 for GPU, cpu for CPU (default: 0)
- `--export`: Export formats (onnx, torchscript, tflite)

---

## 📁 Output Structure

After training:
```
ml_models/
├── weights/
│   ├── fire_detection.pt              ← Use this for production
│   └── fire_detection_best_TIMESTAMP.pt
└── train/
    └── runs/
        └── train/
            └── fire_detection/
                ├── weights/
                │   ├── best.pt        ← Best performing model
                │   └── last.pt        ← Last epoch
                ├── results.png        ← Training curves
                ├── confusion_matrix.png
                ├── PR_curve.png
                └── F1_curve.png
```

---

## 🚀 Deploy Trained Model

### 1. Update Configuration
```bash
# Edit .env in project root
USE_ML_DETECTION=true
ML_MODEL_PATH=ml_models/weights/fire_detection.pt
FIRE_CONFIDENCE_THRESHOLD=0.5
```

### 2. Restart Services
```bash
# Fire detection service
cd ../../fire-detection-service
python main_v2.py

# Live camera server
cd ..
python live_camera_detection_server.py
```

### 3. Test Live
```bash
curl -X POST "http://localhost:8002/detect-fire-ml" \
  -F "file=@test_fire.jpg" \
  -F "camera_id=1" \
  -F "floor_id=1"
```

---

## 💡 Tips for Better Results

### Data Quality
✅ **DO:**
- Use diverse images (day/night, indoor/outdoor)
- Include various fire types (small, large, smoke)
- Balanced classes (equal fire/smoke samples)
- High-quality annotations
- 80/20 train/val split minimum

❌ **DON'T:**
- Use blurry/low-res images
- Copy same image multiple times
- Skip validation set
- Use only one type of fire

### Training
✅ **DO:**
- Start with 100 epochs minimum
- Monitor validation metrics
- Use early stopping (patience)
- Save checkpoints regularly
- Test on new images after training

❌ **DON'T:**
- Stop training too early
- Ignore validation results
- Overtrain on small dataset
- Skip testing phase

---

## 📞 Support

- **Training Guide**: [TRAINING_GUIDE.md](TRAINING_GUIDE.md)
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Roboflow**: https://roboflow.com/
- **Issues**: Check troubleshooting section above

---

## ✅ Quick Checklist

- [ ] Install dependencies
- [ ] Download/prepare dataset
- [ ] Validate dataset structure
- [ ] Choose model size
- [ ] Start training
- [ ] Monitor metrics
- [ ] Review results
- [ ] Test model
- [ ] Deploy to production

---

**Ready to train?** Run `train.bat` (Windows) or follow the Quick Start above!

Good luck! 🔥🚀
