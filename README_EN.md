# NAO Museum Guide Robot

English | [中文](README.md)

An intelligent museum guide system based on NAO robot, integrating computer vision, speech recognition, natural language processing, and emotion detection capabilities.

## Project Structure

```
nao-museum-guide-robot/
├── src/                          # Source code directory
│   ├── core/                     # Core functionality modules
│   │   ├── __init__.py
│   │   ├── robot_controller.py   # Main robot controller (formerly nao_test.py)
│   │   └── museum_guide.py       # Museum guide core class (formerly final.py)
│   ├── services/                 # Service layer modules
│   │   ├── __init__.py
│   │   ├── llm_service.py        # LLM service (formerly callLLM.py)
│   │   ├── speech_service.py     # Speech recognition service (formerly speechReco_python3.py)
│   │   └── detection_service.py  # Detection service (formerly python3main.py)
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── exhibit.py            # Exhibit data model
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   └── config.py            # Configuration management
│   └── choregraphe/             # Choregraphe scripts
│       ├── llm_integration.py   # LLM integration (formerly callLLaMAfromCoregraphe)
│       └── navigation_script.py # Navigation script (formerly choregraphe python script)
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_tts.py              # TTS test (formerly test_say.py)
│   ├── test_landmark_detection.py  # Landmark detection test (formerly test.py)
│   └── test_emotion_tracking.py # Emotion tracking test
├── datasets/                     # Datasets
├── exhibit_detection/           # Exhibit detection images
├── runs/                        # Training results
├── yolo11n.pt                   # YOLO model weights
├── main.py                      # Main entry file (run robot controller)
├── run_detection_service.py     # Detection service entry file
├── README.md                    # README (Chinese version)
└── README_EN.md                 # This file (English version)
```

## Core Module Description

### 1. Core Modules (src/core/)

#### `robot_controller.py`
Main controller for NAO robot, responsible for:
- NAOMark detection and navigation
- Exhibit interaction management
- Visitor emotion and attention monitoring
- Communication with detection and speech services

#### `museum_guide.py`
Core class of the museum guide system, providing:
- Exhibit management
- Environment learning
- Navigation functionality
- Tour data recording

### 2. Service Modules (src/services/)

#### `llm_service.py`
LLM service wrapper, providing:
- Communication with LLaMA model
- Conversation history management
- Exhibit-specific prompt generation

#### `speech_service.py`
Speech recognition service using Whisper model:
- Audio recording
- Speech-to-text conversion
- Lazy model loading

#### `detection_service.py`
Exhibit occupancy detection service:
- ZED camera image capture
- YOLO model person detection
- Socket servers (detection and audio)

### 3. Data Models (src/models/)

#### `exhibit.py`
Defines exhibit data structures and emotion state enumerations

### 4. Utility Modules (src/utils/)

#### `config.py`
Unified configuration management:
- Robot connection configuration
- LLM service configuration
- Network service configuration
- Detection service configuration
- Speech recognition configuration
- Exhibit configuration

## Usage

### 1. Start Detection Service

Run from the project root directory:

```bash
python run_detection_service.py
```

Or:

```bash
cd src/services
python detection_service.py
```

This will start two servers:
- Port 5001: Exhibit occupancy detection service
- Port 5002: Speech recognition service

### 2. Run Robot Controller

Run from the project root directory:

```bash
python main.py
```

Or:

```bash
cd src/core
python robot_controller.py
```

### 3. Run Tests

```bash
# TTS test
python tests/test_tts.py

# Landmark detection test
python tests/test_landmark_detection.py

# Emotion tracking test
python tests/test_emotion_tracking.py
```

## Configuration

All configurations are managed in `src/utils/config.py`. Main configuration items include:

- **Robot Configuration**: IP address, port, recording path
- **LLM Configuration**: Service URL, generation parameters
- **Network Configuration**: Host address, port numbers
- **Detection Configuration**: YOLO model path, confidence threshold
- **Speech Configuration**: Sample rate, Whisper model
- **Exhibit Configuration**: Exhibit ID list, message templates

## Dependencies

Main dependencies:
- `naoqi` - NAO robot SDK
- `ultralytics` - YOLO model
- `whisper` - Speech recognition
- `pyzed` - ZED camera SDK
- `requests` - HTTP requests
- `sounddevice` - Audio recording
- `opencv-python` - Image processing

## Features

1. **Intelligent Navigation**: Precise navigation based on NAOMark
2. **Person Detection**: Use YOLO model to detect exhibit occupancy
3. **Voice Interaction**: Whisper speech recognition + LLM dialogue
4. **Emotion Detection**: Monitor visitor attention and emotional state
5. **Adaptive Explanation**: Adjust explanation content based on visitor interest

## Important Notes

1. Ensure the NAO robot is connected and configured with the correct IP address
2. Ensure the ZED camera is properly connected
3. LLM service needs to be running on the specified IP address
4. All path configurations need to be adjusted according to the actual environment

## File Mapping

Old filename → New filename:
- `nao_test.py` → `src/core/robot_controller.py`
- `final.py` → `src/core/museum_guide.py`
- `callLLM.py` → `src/services/llm_service.py`
- `speechReco_python3.py` → `src/services/speech_service.py`
- `python3main.py` → `src/services/detection_service.py`
- `test_say.py` → `tests/test_tts.py`
- `test.py` → `tests/test_landmark_detection.py`
- `callLLaMAfromCoregraphe` → `src/choregraphe/llm_integration.py`
- `choregraphe python script` → `src/choregraphe/navigation_script.py`

## License

This project is for academic research purposes.

