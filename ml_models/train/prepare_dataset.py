"""
Download and prepare fire detection dataset from Roboflow
Automatically creates dataset structure for YOLOv8 training
"""
import os
import sys
import argparse
from pathlib import Path
import urllib.request
import zipfile
import shutil


def print_header(text):
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)


def create_dataset_yaml(dataset_dir: Path, class_names: list):
    """Create YAML configuration file for YOLOv8"""
    yaml_content = f"""# Fire Detection Dataset Configuration
# Dataset path (relative to this YAML file)
path: {dataset_dir.absolute()}

# Train/Val/Test splits
train: images/train
val: images/val
test: images/test  # optional

# Classes
nc: {len(class_names)}  # number of classes
names: {class_names}  # class names

# Example usage:
# python fire_detection_train.py --data {dataset_dir / 'data.yaml'}
"""
    
    yaml_path = dataset_dir / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Created dataset configuration: {yaml_path}")
    return yaml_path


def download_roboflow_dataset(api_key: str, workspace: str, project: str, version: int, dataset_dir: Path):
    """Download dataset from Roboflow"""
    print_header("Downloading Dataset from Roboflow")
    
    # Roboflow URL format
    download_url = f"https://app.roboflow.com/{workspace}/{project}/{version}/download/yolov8"
    
    print(f"📥 Downloading from Roboflow...")
    print(f"   Workspace: {workspace}")
    print(f"   Project: {project}")
    print(f"   Version: {version}")
    
    print("\n💡 Manual Download Instructions:")
    print("1. Visit: https://universe.roboflow.com/")
    print("2. Search for 'fire detection' or 'smoke detection'")
    print("3. Choose a dataset (recommended: 1000+ images)")
    print("4. Click 'Download' → Select 'YOLOv8' format")
    print("5. Extract to:", dataset_dir.absolute())
    print("\n   The folder should contain:")
    print("   - images/train/")
    print("   - images/val/")
    print("   - labels/train/")
    print("   - labels/val/")
    print("   - data.yaml")
    
    return False  # Manual download required


def create_sample_dataset(dataset_dir: Path):
    """Create a sample dataset structure for testing"""
    print_header("Creating Sample Dataset Structure")
    
    # Create directory structure
    dirs = [
        dataset_dir / 'images' / 'train',
        dataset_dir / 'images' / 'val',
        dataset_dir / 'labels' / 'train',
        dataset_dir / 'labels' / 'val'
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Created directory structure:")
    for dir_path in dirs:
        print(f"   {dir_path}")
    
    # Create data.yaml
    yaml_path = create_dataset_yaml(dataset_dir, ['fire', 'smoke'])
    
    print("\n📝 Next steps:")
    print("1. Add your images to images/train/ and images/val/")
    print("2. Add corresponding labels to labels/train/ and labels/val/")
    print("3. Labels should be YOLO format (.txt files):")
    print("   <class_id> <x_center> <y_center> <width> <height>")
    print("   (All values normalized 0-1)")
    print(f"\n4. Then train: python fire_detection_train.py --data {yaml_path}")
    
    return yaml_path


def validate_dataset_structure(dataset_dir: Path):
    """Validate that dataset has correct structure"""
    print_header("Validating Dataset Structure")
    
    required_dirs = [
        dataset_dir / 'images' / 'train',
        dataset_dir / 'images' / 'val',
        dataset_dir / 'labels' / 'train',
        dataset_dir / 'labels' / 'val'
    ]
    
    all_valid = True
    for dir_path in required_dirs:
        if dir_path.exists():
            file_count = len(list(dir_path.glob('*')))
            print(f"✅ {dir_path.relative_to(dataset_dir)}: {file_count} files")
        else:
            print(f"❌ Missing: {dir_path.relative_to(dataset_dir)}")
            all_valid = False
    
    if all_valid:
        # Check for data.yaml
        yaml_path = dataset_dir / 'data.yaml'
        if yaml_path.exists():
            print(f"✅ Configuration file: {yaml_path}")
        else:
            print(f"⚠️  Missing data.yaml - creating one...")
            create_dataset_yaml(dataset_dir, ['fire', 'smoke'])
        
        # Count images
        train_images = list((dataset_dir / 'images' / 'train').glob('*.jpg')) + \
                      list((dataset_dir / 'images' / 'train').glob('*.png'))
        val_images = list((dataset_dir / 'images' / 'val').glob('*.jpg')) + \
                    list((dataset_dir / 'images' / 'val').glob('*.png'))
        
        print("\n📊 Dataset Summary:")
        print(f"   Training images: {len(train_images)}")
        print(f"   Validation images: {len(val_images)}")
        print(f"   Total: {len(train_images) + len(val_images)}")
        
        if len(train_images) == 0:
            print("\n⚠️  No training images found!")
            print("   Add images to: images/train/")
            print("   Add labels to: labels/train/")
            return False
        
        return True
    else:
        print("\n❌ Dataset structure is incomplete")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Prepare fire detection dataset for training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create sample dataset structure
  python prepare_dataset.py --output fire_dataset --create-structure
  
  # Validate existing dataset
  python prepare_dataset.py --output fire_dataset --validate
  
  # Download from Roboflow (manual step required)
  python prepare_dataset.py --output fire_dataset --roboflow

Recommended Datasets (Roboflow Universe):
  - Fire and Smoke Detection (1000+ images)
  - Fire Detection Computer Vision Project
  - Wildfire Smoke Detection Dataset
        """
    )
    
    parser.add_argument('--output', type=str, default='fire_dataset',
                       help='Output directory for dataset (default: fire_dataset)')
    parser.add_argument('--create-structure', action='store_true',
                       help='Create empty dataset structure')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing dataset structure')
    parser.add_argument('--roboflow', action='store_true',
                       help='Show Roboflow download instructions')
    
    args = parser.parse_args()
    
    dataset_dir = Path(args.output)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n🔥"*40)
    print(" FIRE DETECTION DATASET PREPARATION")
    print("🔥"*40)
    
    if args.roboflow:
        print_header("Roboflow Dataset Download Instructions")
        print("\n📚 Recommended Fire Detection Datasets:")
        print("\n1. Fire and Smoke Detection")
        print("   URL: https://universe.roboflow.com/fire-detection/fire-and-smoke-detection")
        print("   Images: 1000+")
        print("   Classes: fire, smoke")
        
        print("\n2. Fire Detection Dataset")
        print("   URL: https://universe.roboflow.com/search?q=fire%20detection")
        print("   Multiple options available")
        
        print("\n📥 Download Steps:")
        print("1. Go to Roboflow Universe")
        print("2. Find a fire detection dataset")
        print("3. Click 'Download'")
        print("4. Select format: YOLOv8")
        print("5. Download ZIP file")
        print("6. Extract to:", dataset_dir.absolute())
        print("\n7. Run validation:")
        print(f"   python prepare_dataset.py --output {args.output} --validate")
        
    elif args.create_structure:
        create_sample_dataset(dataset_dir)
        
    elif args.validate:
        if validate_dataset_structure(dataset_dir):
            print("\n✅ Dataset is ready for training!")
            yaml_path = dataset_dir / 'data.yaml'
            print(f"\n🚀 Start training with:")
            print(f"   python fire_detection_train.py --data {yaml_path}")
            print(f"\n   Or quick test:")
            print(f"   python fire_detection_train.py --data {yaml_path} --epochs 10")
        else:
            print("\n❌ Please fix dataset issues above")
    
    else:
        print("Please specify an action:")
        print("  --create-structure  : Create empty dataset structure")
        print("  --validate          : Validate existing dataset")
        print("  --roboflow          : Show Roboflow download instructions")
        print("\nExample: python prepare_dataset.py --output fire_dataset --create-structure")


if __name__ == "__main__":
    main()
