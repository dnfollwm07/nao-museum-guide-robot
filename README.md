# NAO博物馆导览机器人

[English](README_EN.md) | 中文

一个基于NAO机器人的智能博物馆导览系统，集成了计算机视觉、语音识别、自然语言处理和情感检测等功能。

## 项目结构

```
nao-museum-guide-robot/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── robot_controller.py   # 机器人主控制器（原nao_test.py）
│   │   └── museum_guide.py       # 博物馆导览核心类（原final.py）
│   ├── services/                 # 服务层模块
│   │   ├── __init__.py
│   │   ├── llm_service.py        # LLM服务（原callLLM.py）
│   │   ├── speech_service.py     # 语音识别服务（原speechReco_python3.py）
│   │   └── detection_service.py  # 检测服务（原python3main.py）
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   └── exhibit.py            # 展品数据模型
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   └── config.py            # 配置管理
│   └── choregraphe/             # Choregraphe脚本
│       ├── llm_integration.py   # LLM集成（原callLLaMAfromCoregraphe）
│       └── navigation_script.py # 导航脚本（原choregraphe python script）
├── tests/                       # 测试文件
│   ├── __init__.py
│   ├── test_tts.py              # TTS测试（原test_say.py）
│   ├── test_landmark_detection.py  # 地标检测测试（原test.py）
│   └── test_emotion_tracking.py # 情感跟踪测试
├── datasets/                     # 数据集
├── exhibit_detection/           # 展品检测图像
├── runs/                        # 训练结果
├── yolo11n.pt                   # YOLO模型权重
├── main.py                      # 主入口文件（运行机器人控制器）
├── run_detection_service.py     # 检测服务入口文件
├── README.md                    # 本文件（中文版）
└── README_EN.md                 # README (English version)
```

## 核心模块说明

### 1. 核心模块 (src/core/)

#### `robot_controller.py`
NAO机器人的主控制器，负责：
- NAOMark检测和导航
- 展品交互管理
- 访客情感和注意力监控
- 与检测服务和语音服务的通信

#### `museum_guide.py`
博物馆导览系统的核心类，提供：
- 展品管理
- 环境学习
- 导航功能
- 导览数据记录

### 2. 服务模块 (src/services/)

#### `llm_service.py`
LLM服务封装，提供：
- 与LLaMA模型的通信
- 对话历史管理
- 展品特定的提示词生成

#### `speech_service.py`
语音识别服务，使用Whisper模型：
- 音频录制
- 语音转文字
- 模型延迟加载

#### `detection_service.py`
展品占用检测服务：
- ZED相机图像捕获
- YOLO模型人员检测
- Socket服务器（检测和音频）

### 3. 数据模型 (src/models/)

#### `exhibit.py`
定义展品数据结构和情感状态枚举

### 4. 工具模块 (src/utils/)

#### `config.py`
统一配置管理：
- 机器人连接配置
- LLM服务配置
- 网络服务配置
- 检测服务配置
- 语音识别配置
- 展品配置

## 使用方法

### 1. 启动检测服务

在项目根目录运行：

```bash
python run_detection_service.py
```

或者：

```bash
cd src/services
python detection_service.py
```

这将启动两个服务器：
- 端口5001：展品占用检测服务
- 端口5002：语音识别服务

### 2. 运行机器人控制器

在项目根目录运行：

```bash
python main.py
```

或者：

```bash
cd src/core
python robot_controller.py
```

### 3. 运行测试

```bash
# TTS测试
python tests/test_tts.py

# 地标检测测试
python tests/test_landmark_detection.py

# 情感跟踪测试
python tests/test_emotion_tracking.py
```

## 配置说明

所有配置都在 `src/utils/config.py` 中管理。主要配置项包括：

- **机器人配置**：IP地址、端口、录音路径
- **LLM配置**：服务URL、生成参数
- **网络配置**：主机地址、端口号
- **检测配置**：YOLO模型路径、置信度阈值
- **语音配置**：采样率、Whisper模型
- **展品配置**：展品ID列表、消息模板

## 依赖项

主要依赖：
- `naoqi` - NAO机器人SDK
- `ultralytics` - YOLO模型
- `whisper` - 语音识别
- `pyzed` - ZED相机SDK
- `requests` - HTTP请求
- `sounddevice` - 音频录制
- `opencv-python` - 图像处理

## 功能特性

1. **智能导航**：基于NAOMark的精确导航
2. **人员检测**：使用YOLO模型检测展品占用情况
3. **语音交互**：Whisper语音识别 + LLM对话
4. **情感检测**：监控访客的注意力和情感状态
5. **自适应讲解**：根据访客兴趣调整讲解内容

## 注意事项

1. 确保NAO机器人已连接并配置正确的IP地址
2. 确保ZED相机已正确连接
3. LLM服务需要在指定IP地址上运行
4. 所有路径配置需要根据实际环境调整

## 文件映射

旧文件名 → 新文件名：
- `nao_test.py` → `src/core/robot_controller.py`
- `final.py` → `src/core/museum_guide.py`
- `callLLM.py` → `src/services/llm_service.py`
- `speechReco_python3.py` → `src/services/speech_service.py`
- `python3main.py` → `src/services/detection_service.py`
- `test_say.py` → `tests/test_tts.py`
- `test.py` → `tests/test_landmark_detection.py`
- `callLLaMAfromCoregraphe` → `src/choregraphe/llm_integration.py`
- `choregraphe python script` → `src/choregraphe/navigation_script.py`

## 许可证

本项目用于学术研究目的。

