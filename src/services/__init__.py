"""
服务模块
包含各种外部服务集成
"""
from .llm_service import LLMService, get_llm_service
from .speech_service import SpeechRecognitionService, get_speech_service
from .detection_service import DetectionService

__all__ = [
    'LLMService',
    'get_llm_service',
    'SpeechRecognitionService',
    'get_speech_service',
    'DetectionService'
]

