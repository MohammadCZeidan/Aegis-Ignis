"""
Training script for fire detection model using YOLOv8
Trains a custom fire/smoke detection model with automatic validation and export
"""
from ultralytics import YOLO
import argparse
import os
import yaml
from pathlib import Path
import shutil
from datetime import datetime


def validate_dataset(data_yaml: str) -> bool:
    """Validate dataset structure and configuration"""
    print("\n" + "="*80)
    print(" Validating Dataset Structure")
    print("="*80)
    
    if not os.path.exists(data_yaml):
        print(f" Dataset YAML not found: {data_yaml}")
        return False
    
    with open(data_yaml, 'r') as f:
        data = yaml.safe_load(f)
    
    required_keys = ['train', 'val', 'nc', 'names']
    for key in required_keys:
        if key not in data:
            print(f" Missing required key in YAML: {key}")
            return False
    
    # Check paths exist
    base_path = Path(data_yaml).parent
    
    train_path = base_path / data['train']
    val_path = base_path / data['val']
    
    if not train_path.exists():
        print(f" Training images not found: {train_path}")
        return False
    
    if not val_path.exists():
        print(f" Validation images not found: {val_path}")
        return False
    
    # Count images
    train_images = list(train_path.glob('*.jpg')) + list(train_path.glob('*.png'))
    val_images = list(val_path.glob('*.jpg')) + list(val_path.glob('*.png'))
    
    print(f" Dataset structure valid")
    print(f"   Training images: {len(train_images)}")
    print(f"   Validation images: {len(val_images)}")
    print(f"   Classes: {data['nc']} ({', '.join(data['names'])})")
    
    return True


def train_fire_detection(
    data_yaml: str,
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    model: str = 'yolov8n.pt',
    patience: int = 50,
    save_period: int = 10,
    device: str = '0',
    export_formats: list = None
):
    """
    Train YOLOv8 model for fire detection with comprehensive validation
    
    Args:
        data_yaml: Path to dataset YAML file
        epochs: Number of training epochs (default: 100)
        imgsz: Image size (default: 640)
        batch: Batch size (default: 16, reduce if GPU memory issues)
        model: Base model - yolov8n.pt (nano), yolov8s.pt (small), yolov8m.pt (medium)
        patience: Early stopping patience (default: 50)
        save_period: Save checkpoint every N epochs (default: 10)
        device: Device to use - '0' for GPU, 'cpu' for CPU
        export_formats: List of export formats ['onnx', 'torchscript', 'tflite']
    """
    print("\n" + "fire"*40)
    print(" YOLOv8 FIRE DETECTION MODEL TRAINING")
    print("fire"*40 + "\n")
    
    # Validate dataset
    if not validate_dataset(data_yaml):
        print("\n Dataset validation failed. Please fix the issues above.")
        return None
    
    # Setup directories
    weights_dir = Path(__file__).parent.parent / 'weights'
    weights_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print(" Starting Training")
    print("="*80)
    print(f"Base Model: {model}")
    print(f"Epochs: {epochs}")
    print(f"Image Size: {imgsz}")
    print(f"Batch Size: {batch}")
    print(f"Device: {device}")
    print(f"Patience: {patience} epochs")
    print("="*80 + "\n")
    
    # Load base model
    try:
        yolo_model = YOLO(model)
    except Exception as e:
        print(f" Error loading base model: {e}")
        print("Will download YOLOv8 model automatically...")
        yolo_model = YOLO(model)
    
    # Train with comprehensive settings
    results = yolo_model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        save_period=save_period,
        device=device,
        name='fire_detection',
        pretrained=True,
        optimizer='AdamW',
        verbose=True,
        seed=42,
        deterministic=True,
        single_cls=False,
        rect=False,
        cos_lr=True,
        close_mosaic=10,
        amp=True,  # Automatic Mixed Precision
        fraction=1.0,
        project='runs/train',
        exist_ok=True,
        val=True,
        save=True,
        plots=True,
        cache=False
    )
    
    print("\n" + "="*80)
    print(" Training Completed!")
    print("="*80)
    
    # Get best model path
    best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
    last_model_path = Path(results.save_dir) / 'weights' / 'last.pt'
    
    # Copy to weights directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_model_path = weights_dir / f'fire_detection_best_{timestamp}.pt'
    
    if best_model_path.exists():
        shutil.copy(best_model_path, final_model_path)
        shutil.copy(best_model_path, weights_dir / 'fire_detection.pt')
        print(f" Best model saved to: {final_model_path}")
        print(f" Current model updated: {weights_dir / 'fire_detection.pt'}")
    
    # Validation metrics
    print("\n" + "="*80)
    print(" Final Metrics")
    print("="*80)
    print(f"Training directory: {results.save_dir}")
    
    # Export models
    if export_formats:
        print("\n" + "="*80)
        print(" Exporting Models")
        print("="*80)
        
        best_model = YOLO(best_model_path)
        
        for fmt in export_formats:
            try:
                print(f"Exporting to {fmt.upper()}...")
                export_path = best_model.export(format=fmt)
                print(f" {fmt.upper()} export successful: {export_path}")
            except Exception as e:
                print(f" {fmt.upper()} export failed: {e}")
    
    # Test inference
    print("\n" + "="*80)
    print(" Testing Model Inference")
    print("="*80)
    
    test_model = YOLO(final_model_path)
    print(f" Model loaded successfully")
    print(f" Classes: {test_model.names}")
    
    print("\n" + "="*80)
    print(" All Done!")
    print("="*80)
    print("\nNext steps:")
    print("1. Check training results in:", results.save_dir)
    print("2. Review metrics: confusion_matrix.png, results.png, PR_curve.png")
    print("3. Test model: python test_model.py")
    print(f"4. Deploy model: Copy {final_model_path} to production")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Train YOLOv8 fire detection model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training
  python fire_detection_train.py --data fire_dataset/data.yaml
  
  # Custom training with 200 epochs
  python fire_detection_train.py --data fire_dataset/data.yaml --epochs 200 --batch 32
  
  # Train with GPU and export multiple formats
  python fire_detection_train.py --data fire_dataset/data.yaml --device 0 --export onnx torchscript
  
  # Quick test (small model, few epochs)
  python fire_detection_train.py --data fire_dataset/data.yaml --epochs 10 --model yolov8n.pt
        """
    )
    
    parser.add_argument('--data', type=str, required=True, 
                       help='Path to dataset YAML file (required)')
    parser.add_argument('--epochs', type=int, default=100, 
                       help='Number of training epochs (default: 100)')
    parser.add_argument('--imgsz', type=int, default=640, 
                       help='Image size for training (default: 640)')
    parser.add_argument('--batch', type=int, default=16, 
                       help='Batch size (default: 16, reduce if GPU memory issues)')
    parser.add_argument('--model', type=str, default='yolov8n.pt', 
                       choices=['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'],
                       help='Base YOLOv8 model (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--patience', type=int, default=50,
                       help='Early stopping patience in epochs (default: 50)')
    parser.add_argument('--save-period', type=int, default=10,
                       help='Save checkpoint every N epochs (default: 10)')
    parser.add_argument('--device', type=str, default='0',
                       help='Device to use: 0 for GPU, cpu for CPU (default: 0)')
    parser.add_argument('--export', nargs='+', default=[],
                       choices=['onnx', 'torchscript', 'tflite', 'engine'],
                       help='Export formats after training (e.g., --export onnx tflite)')
    
    args = parser.parse_args()
    
    print("\n Fire Detection Model Training")
    print(f"Dataset: {args.data}")
    print(f"Model: {args.model}")
    print(f"Device: {args.device}\n")
    
    train_fire_detection(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        model=args.model,
        patience=args.patience,
        save_period=args.save_period,
        device=args.device,
        export_formats=args.export if args.export else None
    )

