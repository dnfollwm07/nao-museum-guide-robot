"""
配置管理模块
统一管理机器人连接、服务端口、LLM服务等配置信息
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RobotConfig:
    """NAO机器人配置"""
    ip: str = "192.168.1.25"
    port: int = 9559
    recording_path: str = "/home/nao/recordings/interaction.wav"


@dataclass
class LLMConfig:
    """LLM服务配置"""
    url: str = "http://192.168.1.22:8080/completion"
    headers: dict = None
    n_predict: int = 250
    temperature: float = 0.7
    top_k: int = 10
    top_p: float = 0.8
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


@dataclass
class NetworkConfig:
    """网络服务配置"""
    host: str = "localhost"
    detection_port: int = 5001
    audio_port: int = 5002


@dataclass
class DetectionConfig:
    """检测服务配置"""
    yolo_model_path: str = "yolo11n.pt"
    exhibit_detection_dir: str = "exhibit_detection"
    exhibit_image_filename: str = "exhibits.jpg"
    confidence_threshold: float = 0.5


@dataclass
class SpeechConfig:
    """语音识别配置"""
    sample_rate: int = 16000
    channels: int = 1
    whisper_model: str = "tiny"
    language: str = "en"


@dataclass
class ExhibitConfig:
    """展品配置"""
    total_exhibit_ids: list = None
    exhibit_messages: dict = None
    
    def __post_init__(self):
        if self.total_exhibit_ids is None:
            self.total_exhibit_ids = [84, 80]
        if self.exhibit_messages is None:
            self.exhibit_messages = {
                "1": "Exhibit 1 is occupied.",
                "2": "Exhibit 2 is occupied.",
                "3": "Exhibit 3 is occupied."
            }


# 全局配置实例
robot_config = RobotConfig()
llm_config = LLMConfig()
network_config = NetworkConfig()
detection_config = DetectionConfig()
speech_config = SpeechConfig()
exhibit_config = ExhibitConfig()

