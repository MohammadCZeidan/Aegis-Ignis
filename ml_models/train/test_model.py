"""
Test trained fire detection model
Validates model performance and runs inference on test images
"""
from ultralytics import YOLO
import cv2
import argparse
from pathlib import Path
import numpy as np


def test_model_inference(model_path: str, test_image: str = None, conf_threshold: float = 0.5):
    """Test model inference on an image"""
    print("\n" + "="*80)
    print(" Testing Model Inference")
    print("="*80)
    
    # Load model
    print(f"Loading model: {model_path}")
    try:
        model = YOLO(model_path)
        print(f" Model loaded successfully")
        print(f"   Classes: {model.names}")
        print(f"   Number of classes: {len(model.names)}")
    except Exception as e:
        print(f" Error loading model: {e}")
        return False
    
    if test_image:
        print(f"\nTesting on image: {test_image}")
        
        if not Path(test_image).exists():
            print(f" Image not found: {test_image}")
            return False
        
        # Run inference
        results = model(test_image, conf=conf_threshold)
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            if len(boxes) == 0:
                print("  No detections found")
            else:
                print(f"\n Found {len(boxes)} detections:")
                
                for i, box in enumerate(boxes):
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    coords = box.xyxy[0].cpu().numpy()
                    
                    class_name = model.names[class_id]
                    
                    print(f"   Detection {i+1}:")
                    print(f"      Class: {class_name}")
                    print(f"      Confidence: {confidence*100:.1f}%")
                    print(f"      Bbox: [{int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])}]")
            
            # Save annotated image
            annotated = result.plot()
            output_path = Path(test_image).parent / f"{Path(test_image).stem}_detected.jpg"
            cv2.imwrite(str(output_path), annotated)
            print(f"\n Saved annotated image: {output_path}")
    
    else:
        # Create test image
        print("\nNo test image provided - creating sample test image...")
        test_img = np.zeros((640, 640, 3), dtype=np.uint8)
        # Add orange/red region (simulated fire)
        cv2.rectangle(test_img, (200, 200), (400, 400), (0, 100, 255), -1)
        
        test_path = "test_fire_sample.jpg"
        cv2.imwrite(test_path, test_img)
        print(f"Created test image: {test_path}")
        
        # Test inference
        results = model(test_path, conf=conf_threshold)
        print(f"\nModel inference completed")
        print(f"Detections: {len(results[0].boxes) if results else 0}")
    
    return True


def validate_model(model_path: str, data_yaml: str = None):
    """Validate model on validation set"""
    print("\n" + "="*80)
    print(" Validating Model Performance")
    print("="*80)
    
    model = YOLO(model_path)
    
    if data_yaml and Path(data_yaml).exists():
        print(f"Running validation on dataset: {data_yaml}")
        metrics = model.val(data=data_yaml)
        
        print(f"\n Validation Results:")
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        print(f"   Precision: {metrics.box.mp:.3f}")
        print(f"   Recall: {metrics.box.mr:.3f}")
    else:
        print("  No validation dataset provided")
        print("   Provide --data argument to run validation")


def benchmark_speed(model_path: str, imgsz: int = 640):
    """Benchmark model inference speed"""
    print("\n" + "="*80)
    print(" Benchmarking Inference Speed")
    print("="*80)
    
    model = YOLO(model_path)
    
    # Create dummy image
    dummy_img = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype=np.uint8)
    
    # Warmup
    print("Warming up...")
    for _ in range(5):
        model(dummy_img, verbose=False)
    
    # Benchmark
    import time
    num_runs = 50
    print(f"Running {num_runs} inferences...")
    
    start = time.time()
    for _ in range(num_runs):
        model(dummy_img, verbose=False)
    end = time.time()
    
    avg_time = (end - start) / num_runs * 1000  # milliseconds
    fps = 1000 / avg_time
    
    print(f"\n Performance Results:")
    print(f"   Average inference time: {avg_time:.1f} ms")
    print(f"   FPS: {fps:.1f}")
    print(f"   Image size: {imgsz}x{imgsz}")


def main():
    parser = argparse.ArgumentParser(
        description='Test trained fire detection model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test model on image
  python test_model.py --model ../weights/fire_detection.pt --image test_fire.jpg
  
  # Validate model on dataset
  python test_model.py --model ../weights/fire_detection.pt --data fire_dataset/data.yaml
  
  # Benchmark speed
  python test_model.py --model ../weights/fire_detection.pt --benchmark
  
  # Full test suite
  python test_model.py --model ../weights/fire_detection.pt --image test.jpg --data data.yaml --benchmark
        """
    )
    
    parser.add_argument('--model', type=str, required=True,
                       help='Path to trained model (.pt file)')
    parser.add_argument('--image', type=str, default=None,
                       help='Path to test image')
    parser.add_argument('--data', type=str, default=None,
                       help='Path to dataset YAML for validation')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run speed benchmark')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Image size for benchmark (default: 640)')
    
    args = parser.parse_args()
    
    print("\n"*40)
    print(" FIRE DETECTION MODEL TESTING")
    print(""*40)
    
    # Check model exists
    if not Path(args.model).exists():
        print(f"\n Model not found: {args.model}")
        print("\nAvailable models in weights/:")
        weights_dir = Path(__file__).parent.parent / 'weights'
        if weights_dir.exists():
            models = list(weights_dir.glob('*.pt'))
            for model in models:
                print(f"   {model}")
        return
    
    # Test inference
    test_model_inference(args.model, args.image, args.conf)
    
    # Validate on dataset
    if args.data:
        validate_model(args.model, args.data)
    
    # Benchmark
    if args.benchmark:
        benchmark_speed(args.model, args.imgsz)
    
    print("\n" + "="*80)
    print(" Testing Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
