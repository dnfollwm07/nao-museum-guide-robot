# 迁移指南

本文档说明如何从旧的代码结构迁移到新的架构。

## 文件映射表

| 旧文件名 | 新位置 | 说明 |
|---------|--------|------|
| `nao_test.py` | `src/core/robot_controller.py` | 机器人主控制器 |
| `final.py` | `src/core/museum_guide.py` | 博物馆导览核心类 |
| `callLLM.py` | `src/services/llm_service.py` | LLM服务 |
| `speechReco_python3.py` | `src/services/speech_service.py` | 语音识别服务 |
| `python3main.py` | `src/services/detection_service.py` | 检测服务 |
| `test_say.py` | `tests/test_tts.py` | TTS测试 |
| `test.py` | `tests/test_landmark_detection.py` | 地标检测测试 |
| `callLLaMAfromCoregraphe` | `src/choregraphe/llm_integration.py` | Choregraphe LLM集成 |
| `choregraphe python script` | `src/choregraphe/navigation_script.py` | Choregraphe导航脚本 |

## 主要变化

### 1. 配置管理

**旧方式：**
```python
ROBOT_IP = "192.168.1.25"
ROBOT_PORT = 9559
LLAMA_URL = "http://192.168.1.22:8080/completion"
```

**新方式：**
```python
from src.utils.config import robot_config, llm_config

robot_ip = robot_config.ip
robot_port = robot_config.port
llama_url = llm_config.url
```

### 2. LLM服务调用

**旧方式：**
```python
import callLLM
response = callLLM.query_llama(prompt)
```

**新方式：**
```python
from src.services import get_llm_service

llm_service = get_llm_service()
response = llm_service.query(prompt, mark_id=80)
```

### 3. 语音识别

**旧方式：**
```python
import speechReco_python3
recording, fs = speechReco_python3.record_audio(5)
text = speechReco_python3.transcribe_audio(audio_file)
```

**新方式：**
```python
from src.services import get_speech_service

speech_service = get_speech_service()
recording, fs = speech_service.record_audio(5)
text = speech_service.transcribe_audio(audio_file)
```

或者使用便捷方法：
```python
text = speech_service.record_and_transcribe(seconds=5)
```

### 4. 机器人控制器

**旧方式：**
```python
# 直接运行 nao_test.py
python nao_test.py
```

**新方式：**
```python
# 方式1：使用主入口文件
python main.py

# 方式2：直接运行模块
from src.core import RobotController
controller = RobotController()
controller.run()
```

### 5. 检测服务

**旧方式：**
```python
# 直接运行 python3main.py
python python3main.py
```

**新方式：**
```python
# 方式1：使用入口文件
python run_detection_service.py

# 方式2：直接运行模块
from src.services import DetectionService
service = DetectionService(num_exhibits=2)
service.start_all_services()
```

## 向后兼容性

为了保持向后兼容，`speech_service.py` 中保留了原有的函数接口：

```python
# 这些函数仍然可用
from src.services.speech_service import record_audio, save_audio, transcribe_audio
```

## 导入路径

### 旧代码中的导入
```python
import speechReco_python3
import callLLM
```

### 新代码中的导入
```python
# 方式1：从包导入
from src.services import get_speech_service, get_llm_service

# 方式2：直接导入模块
from src.services.speech_service import SpeechRecognitionService
from src.services.llm_service import LLMService
```

## 运行测试

### 旧方式
```bash
python test_say.py
python test.py
```

### 新方式
```bash
python tests/test_tts.py
python tests/test_landmark_detection.py
python tests/test_emotion_tracking.py
```

## 注意事项

1. **路径问题**：如果直接运行模块文件，需要确保 `src` 目录在 Python 路径中
2. **配置修改**：所有配置现在集中在 `src/utils/config.py`，修改配置更方便
3. **模块化**：新架构更加模块化，便于测试和维护
4. **功能保留**：所有原有功能都已保留，只是重新组织

## 快速开始

1. 启动检测服务：
   ```bash
   python run_detection_service.py
   ```

2. 运行机器人控制器：
   ```bash
   python main.py
   ```

## 问题排查

如果遇到导入错误，确保：
1. 在项目根目录运行脚本
2. 或者将 `src` 目录添加到 `PYTHONPATH`
3. 检查 `__init__.py` 文件是否存在

