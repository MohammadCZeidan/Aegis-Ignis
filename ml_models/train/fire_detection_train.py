"""
Training script for fire detection model using YOLOv8.
"""
from ultralytics import YOLO
import argparse


def train_fire_detection(
    data_yaml: str,
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    model: str = 'yolov8n.pt'
):
    """
    Train YOLOv8 model for fire detection.
    
    Args:
        data_yaml: Path to dataset YAML file
        epochs: Number of training epochs
        imgsz: Image size
        batch: Batch size
        model: Base model to use
    """
    # Load model
    model = YOLO(model)
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name='fire_detection'
    )
    
    # Export to ONNX for edge deployment
    model.export(format='onnx')
    
    print(f"Training completed. Model saved to: {results.save_dir}")
    print(f"ONNX model exported for edge deployment")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train fire detection model')
    parser.add_argument('--data', type=str, required=True, help='Path to dataset YAML')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Base model')
    
    args = parser.parse_args()
    
    train_fire_detection(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        model=args.model
    )

