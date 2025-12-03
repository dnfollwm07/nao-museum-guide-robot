"""
检测服务模块
提供展品占用检测功能，使用ZED相机和YOLO模型进行人员检测
"""
import socket
import threading
import cv2
import numpy as np
import pyzed.sl as sl
from datetime import datetime
from typing import Optional
from ultralytics import YOLO
from ..utils.config import network_config, detection_config
from .speech_service import get_speech_service


class DetectionService:
    """展品占用检测服务"""
    
    def __init__(self, num_exhibits: int = 2, config=None, network_config_obj=None):
        """
        初始化检测服务
        
        Args:
            num_exhibits: 展品数量
            config: 检测配置对象
            network_config_obj: 网络配置对象
        """
        self.num_exhibits = num_exhibits
        self.config = config or detection_config
        self.network_config = network_config_obj or network_config
        
        # 初始化ZED相机
        self.zed = sl.Camera()
        self._init_zed_camera()
        
        # 初始化YOLO模型
        self.model = YOLO(self.config.yolo_model_path)
        
        # 创建图像存储对象
        self.image = sl.Mat()
        self.runtime_parameters = sl.RuntimeParameters()
        
        # 语音识别服务
        self.speech_service = get_speech_service()
    
    def _init_zed_camera(self):
        """初始化ZED相机"""
        init_params = sl.InitParameters()
        if self.zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError("Unable to open ZED camera")
    
    def capture_and_detect(self) -> str:
        """
        捕获图像并检测展品占用情况
        
        Returns:
            占用状态字符串，例如 "01" 表示第一个展品空闲，第二个展品被占用
        """
        occupied_exhibits = ""
        
        try:
            # 抓取新帧
            if self.zed.grab(self.runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # 检索左图像
                self.zed.retrieve_image(self.image, sl.VIEW.LEFT)
                
                # 转换为numpy数组
                frame = self.image.get_data()
                if frame is None:
                    return occupied_exhibits
                
                frame = np.array(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # 保存完整图像
                filename = f"{self.config.exhibit_detection_dir}/{self.config.exhibit_image_filename}"
                cv2.imwrite(filename, frame)
                print("Image saved!")
                
                # 分割并保存垂直区域
                img = cv2.imread(filename)
                height, width, _ = img.shape
                section_width = width // self.num_exhibits
                
                for i in range(self.num_exhibits):
                    start_x = i * section_width
                    end_x = (i + 1) * section_width if i < self.num_exhibits - 1 else width
                    section = img[:, start_x:end_x]
                    
                    section_filename = f"{self.config.exhibit_detection_dir}/exhibit_section_{i + 1}.jpg"
                    cv2.imwrite(section_filename, section)
                    print(f"Saved section {i + 1} to {section_filename}")
                
                # 检测每个区域是否有人
                for i in range(self.num_exhibits):
                    section_filename = f"{self.config.exhibit_detection_dir}/exhibit_section_{i + 1}.jpg"
                    section_img = cv2.imread(section_filename)
                    results = self.model(section_img)
                    
                    person_found = any(
                        self.model.names[int(box.cls[0])] == "person" 
                        and float(box.conf[0]) > self.config.confidence_threshold
                        for result in results 
                        for box in result.boxes
                    )
                    
                    if person_found:
                        occupied_exhibits += "1"
                        print(f"Person detected in Exhibit {i + 1}")
                    else:
                        occupied_exhibits += "0"
                        print(f"No one detected in Exhibit {i + 1}")
        
        except Exception as e:
            print(f"An error occurred during detection: {e}")
        
        return occupied_exhibits
    
    def send_exhibits_occupied_metadata(self, conn: socket.socket):
        """
        发送展品占用元数据到NAO机器人
        
        Args:
            conn: 已建立的socket连接
        """
        try:
            occupied_exhibits = self.capture_and_detect()
            if occupied_exhibits:
                conn.sendall(occupied_exhibits.encode('utf-8'))
                print("[Metadata] Sent to NAO:", occupied_exhibits)
        except Exception as e:
            print("Error during metadata handling:", e)
        finally:
            conn.close()
    
    def handle_audio(self, conn: socket.socket):
        """
        处理音频请求，进行语音识别
        
        Args:
            conn: 已建立的socket连接
        """
        try:
            recording, fs = self.speech_service.record_audio(5)
            print(f"[Dialogue] Connected")
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"audio-{timestamp}.wav"
            audio_file = self.speech_service.save_audio(recording, fs, filename)
            text = self.speech_service.transcribe_audio(audio_file)
            conn.sendall(text.encode('utf-8'))
        except Exception as e:
            print(f"Error handling audio: {e}")
            conn.sendall("Error processing audio".encode('utf-8'))
        finally:
            conn.close()
    
    def start_audio_server(self):
        """启动音频处理服务器"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.network_config.host, self.network_config.audio_port))
            s.listen(1)
            print(f"[Dialogue] Listening on port {self.network_config.audio_port}...")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_audio, args=(conn,)).start()
    
    def start_occupied_detector(self):
        """启动展品占用检测服务器"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.network_config.host, self.network_config.detection_port))
            s.listen(1)
            print(f"[Metadata] Listening on port {self.network_config.detection_port}...")
            while True:
                conn, addr = s.accept()
                threading.Thread(
                    target=self.send_exhibits_occupied_metadata,
                    args=(conn,)
                ).start()
    
    def start_all_services(self):
        """启动所有服务（阻塞调用）"""
        audio_thread = threading.Thread(target=self.start_audio_server)
        occupied_thread = threading.Thread(target=self.start_occupied_detector)
        
        audio_thread.start()
        occupied_thread.start()
        
        # 阻塞主线程
        audio_thread.join()
        occupied_thread.join()
    
    def close(self):
        """关闭相机资源"""
        if self.zed:
            self.zed.close()


def main():
    """主函数，用于独立运行检测服务"""
    service = DetectionService(num_exhibits=2)
    try:
        service.start_all_services()
    except KeyboardInterrupt:
        print("\nShutting down detection service...")
    finally:
        service.close()


if __name__ == "__main__":
    main()

