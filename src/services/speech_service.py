"""
语音识别服务模块
使用Whisper模型进行语音转文字功能
"""
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os
import sys
import torch
from typing import Tuple, Optional
from ..utils.config import speech_config


class SpeechRecognitionService:
    """语音识别服务类"""
    
    def __init__(self, config=None):
        """
        初始化语音识别服务
        
        Args:
            config: 语音识别配置对象，如果为None则使用默认配置
        """
        self.config = config or speech_config
        self.model: Optional[whisper.Whisper] = None
        self._model_loaded = False
    
    def _load_model(self):
        """延迟加载Whisper模型"""
        if not self._model_loaded:
            print("Loading Whisper model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            self.model = whisper.load_model(self.config.whisper_model, device=device)
            self._model_loaded = True
    
    def record_audio(self, seconds: int = 3, fs: Optional[int] = None) -> Tuple:
        """
        录制音频
        
        Args:
            seconds: 录制时长（秒）
            fs: 采样率，如果为None则使用配置中的采样率
            
        Returns:
            (录音数据, 采样率) 元组
        """
        if fs is None:
            fs = self.config.sample_rate
        
        try:
            print("Starting recording...")
            recording = sd.rec(
                int(seconds * fs),
                samplerate=fs,
                channels=self.config.channels,
                dtype="int16"
            )
            sd.wait()  # 等待录制完成
            return recording, fs
        except Exception as e:
            print(f"Error during recording: {str(e)}")
            raise
    
    def save_audio(self, recording, fs: int, filename: str = "output.wav") -> str:
        """
        保存音频文件
        
        Args:
            recording: 录音数据
            fs: 采样率
            filename: 保存的文件名
            
        Returns:
            保存的文件路径
        """
        try:
            write(filename, fs, recording)
            print(f"Recording completed, saved as {filename}")
            return filename
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")
            raise
    
    def transcribe_audio(self, audio_file: str) -> str:
        """
        将音频文件转换为文字
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            转录的文字
        """
        try:
            self._load_model()
            print("Converting speech to text...")
            
            # 确保使用绝对路径
            if not os.path.isabs(audio_file):
                audio_file = os.path.join(os.getcwd(), audio_file)
            
            result = self.model.transcribe(
                audio_file,
                language=self.config.language
            )
            return result["text"]
        except Exception as e:
            print(f"Error during speech conversion: {str(e)}")
            raise
    
    def record_and_transcribe(self, seconds: int = 3, save_file: Optional[str] = None) -> str:
        """
        录制音频并直接转换为文字（便捷方法）
        
        Args:
            seconds: 录制时长（秒）
            save_file: 可选，保存音频文件的路径
            
        Returns:
            转录的文字
        """
        recording, fs = self.record_audio(seconds)
        
        if save_file:
            audio_file = self.save_audio(recording, fs, save_file)
        else:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            audio_file = f"audio-{timestamp}.wav"
            audio_file = self.save_audio(recording, fs, audio_file)
        
        return self.transcribe_audio(audio_file)


# 全局服务实例
_speech_service_instance: Optional[SpeechRecognitionService] = None


def get_speech_service() -> SpeechRecognitionService:
    """
    获取语音识别服务单例
    
    Returns:
        SpeechRecognitionService实例
    """
    global _speech_service_instance
    if _speech_service_instance is None:
        _speech_service_instance = SpeechRecognitionService()
    return _speech_service_instance


# 为了向后兼容，保留原有函数接口
def record_audio(seconds=3, fs=16000):
    """向后兼容的函数接口"""
    service = get_speech_service()
    return service.record_audio(seconds, fs)


def save_audio(recording, fs, filename="output.wav"):
    """向后兼容的函数接口"""
    service = get_speech_service()
    return service.save_audio(recording, fs, filename)


def transcribe_audio(audio_file):
    """向后兼容的函数接口"""
    service = get_speech_service()
    return service.transcribe_audio(audio_file)

