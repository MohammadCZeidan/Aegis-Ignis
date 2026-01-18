# Edge Processor

Edge computing component for running detection models on-premise.

## Features

- Lightweight detection models (quantized ONNX)
- MQTT communication with cloud backend
- Real-time frame processing
- Low latency detection

## Setup

1. Install dependencies:
```bash
pip install opencv-python numpy paho-mqtt onnxruntime
```

2. Configure MQTT broker in `processor.py`

3. Run edge processor:
```bash
python processor.py
```

## Model Quantization

Models should be quantized to INT8 for edge deployment:

```python
# Example quantization script
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    'model_fp32.onnx',
    'model_int8.onnx',
    weight_type=QuantType.QUInt8
)
```

