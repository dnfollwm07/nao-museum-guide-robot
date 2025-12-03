"""
机器人控制器模块
NAO机器人的主控制逻辑，包括NAOMark检测、导航、交互等功能
"""
import datetime
import socket
import string
import threading
import time
import math
from typing import Optional, Tuple, List
from naoqi import ALProxy
import qi

from ..utils.config import robot_config, network_config, exhibit_config
from ..services import get_llm_service


class RobotController:
    """NAO机器人主控制器"""
    
    def __init__(self, robot_ip: Optional[str] = None, port: Optional[int] = None):
        """
        初始化机器人控制器
        
        Args:
            robot_ip: 机器人IP地址
            port: 机器人端口
        """
        self.robot_ip = robot_ip or robot_config.ip
        self.port = port or robot_config.port
        
        # 初始化NAO代理
        self._initialize_proxies()
        
        # 状态变量
        self.occupied_exhibits = ""
        self.detected_exhibit_ids: List[int] = []
        self.attention_records: List[List] = []
        
        # 服务
        self.llm_service = get_llm_service()
        
        # 禁用自主生命模式
        self.life.setState("disabled")
    
    def _initialize_proxies(self):
        """初始化所有NAO代理"""
        self.tts = ALProxy("ALTextToSpeech", self.robot_ip, self.port)
        self.recorder = ALProxy("ALAudioRecorder", self.robot_ip, self.port)
        self.memory = ALProxy("ALMemory", self.robot_ip, self.port)
        self.landMarkProxy = ALProxy("ALLandMarkDetection", self.robot_ip, self.port)
        self.memoryProxy = ALProxy("ALMemory", self.robot_ip, self.port)
        self.motionProxy = ALProxy("ALMotion", self.robot_ip, self.port)
        self.postureProxy = ALProxy("ALRobotPosture", self.robot_ip, self.port)
        self.life = ALProxy("ALAutonomousLife", self.robot_ip, self.port)
        self.emotion_proxy = ALProxy("ALMood", self.robot_ip, self.port)
        self.localization = ALProxy("ALLocalization", self.robot_ip, self.port)
        self.navigation = ALProxy("ALNavigation", self.robot_ip, self.port)
    
    def detect_naomark(self) -> Optional[Tuple[int, float, float, float, float]]:
        """
        检测NAOMark并返回展品信息
        
        Returns:
            (mark_id, alpha, beta, width, height) 元组，如果未检测到则返回None
        """
        period = 500
        self.landMarkProxy.subscribe("Test_LandMark", period, 0.0)
        print("Attempting to detect landmarks...")
        
        original_head_yaw = self.motionProxy.getAngles("HeadYaw", True)[0]
        head_yaw_positions = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
        
        first_candidate = None
        
        for yaw in head_yaw_positions:
            self.motionProxy.setAngles("HeadYaw", yaw, 0.3)
            self.motionProxy.setAngles("HeadPitch", 0.0, 0.2)
            time.sleep(1.5)
            
            val = self.memoryProxy.getData("LandmarkDetected", 0)
            if not (val and isinstance(val, list) and len(val) >= 2):
                continue
            
            for markInfo in val[1]:
                shape, extra = markInfo
                mark_id = extra[0]
                
                # 检查是否是已知展品
                if mark_id not in exhibit_config.total_exhibit_ids:
                    continue
                
                beta = shape[2]
                width = shape[3]
                height = shape[4]
                alpha = yaw
                
                # 记住第一个检测到的
                if first_candidate is None:
                    first_candidate = (mark_id, alpha, beta, width, height)
                
                idx = exhibit_config.total_exhibit_ids.index(mark_id)
                occupied = self.occupied_exhibits[idx] == '1' if idx < len(self.occupied_exhibits) else False
                print(occupied, mark_id)
                
                if occupied:
                    print(f"Exhibit {mark_id} is occupied; continuing scan.")
                    continue  # 继续寻找空闲的
                
                # 找到空闲展品，立即前往
                if mark_id == 80:
                    self.tts.say("I see the Van Gogh exhibit is free; let's head there!")
                elif mark_id == 84:
                    self.tts.say("The Monet exhibit is empty. Follow me!")
                
                self.detected_exhibit_ids.append(mark_id)
                self.landMarkProxy.unsubscribe("Test_LandMark")
                self.motionProxy.setAngles("HeadYaw", original_head_yaw, 0.2)
                return mark_id, alpha, beta, width, height
        
        # 没有找到空闲展品，使用第一个候选
        self.landMarkProxy.unsubscribe("Test_LandMark")
        self.motionProxy.setAngles("HeadYaw", original_head_yaw, 0.2)
        
        if first_candidate:
            mark_id, alpha, beta, width, height = first_candidate
            self.tts.say("All exhibits seem occupied, but I'll take you to this one anyway.")
            self.detected_exhibit_ids.append(mark_id)
            return mark_id, alpha, beta, width, height
        
        # 完全没有检测到标记
        print("No landmark detected during the sweep.")
        return None
    
    def move_to_naomark(self, alpha: float, beta: float, width: float):
        """
        移动到NAOMark位置
        
        Args:
            alpha: 标记的角度
            beta: 标记的beta值
            width: 标记的宽度
        """
        real_mark_size = 0.1  # 米
        distance = real_mark_size / width
        
        self.motionProxy.wakeUp()
        
        self.motionProxy.moveTo(0, 0, alpha)
        x = distance * math.cos(beta) * math.cos(alpha)
        y = 0
        theta = 0
        print(x, y, theta)
        
        time.sleep(1.5)
        self.motionProxy.moveTo(x * 0.6, y, theta)
        time.sleep(0.1)
        self.motionProxy.stopMove()
        print("Reached near the naomark.")
    
    def introduction_markid(self, mark_id: int):
        """
        根据展品ID给出介绍
        
        Args:
            mark_id: 展品ID
        """
        if mark_id == 84:
            self.tts.say(
                "This painting is part of Claude Monet's Water Lilies series, created between 1897 and 1926. "
                "It captures the surface of a pond in his garden at Giverny, focusing on water lilies, "
                "reflections, and the shifting effects of light. Monet painted outdoors to observe how color "
                "changed throughout the day. The absence of a horizon or human presence emphasizes the immersive "
                "and abstract quality of the scene."
            )
        elif mark_id == 80:
            self.tts.say(
                "The Starry Night was painted by Vincent van Gogh in June 1889 while he was staying at an "
                "asylum in Saint-Remy-de-Provence. It depicts a swirling night sky over a quiet village, with "
                "exaggerated forms and vibrant colors. The painting reflects Van Gogh's emotional state and his "
                "unique use of brushwork and color. It was based not on a direct view, but a combination of memory "
                "and imagination!"
            )
        
        time.sleep(2)
    
    def listen_for_exhibit_status(self) -> bytes:
        """
        监听展品状态（从检测服务获取）
        
        Returns:
            展品占用状态字节串
        """
        self.tts.post.say("Let's see if any exhibits are empty...")
        s = socket.socket()
        s.connect((network_config.host, network_config.detection_port))
        ret = s.recv(1024)
        print("[Metadata] Received:", ret)
        s.close()
        return ret
    
    def listen_for_human_response(self) -> bytes:
        """
        监听人类响应（从语音识别服务获取）
        
        Returns:
            转录的文本字节串
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((network_config.host, network_config.audio_port))
        response = s.recv(1024)
        print("[Dialogue] Response:", response)
        self.tts.post.say("Hmm, let me think...")
        s.close()
        return response
    
    def tracker_face(self):
        """
        跟踪人脸
        
        Returns:
            ALTracker对象
        """
        original_head_yaw = self.motionProxy.getAngles("HeadYaw", True)[0]
        original_head_pitch = self.motionProxy.getAngles("HeadPitch", True)[0]
        
        tracker = ALProxy("ALTracker", self.robot_ip, self.port)
        motion = ALProxy("ALMotion", self.robot_ip, self.port)
        
        head_yaw_positions = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
        head_pitch_positions = [-0.5, -0.25, 0.0]
        
        motion.setStiffnesses("Head", 1.0)
        tracker.registerTarget("Face", 0.1)
        print("Starting face scan...")
        
        face_detected = False
        while not face_detected:
            for pitch in head_pitch_positions:
                if face_detected:
                    break
                for yaw in head_yaw_positions:
                    motion.setAngles("HeadYaw", yaw, 0.3)
                    motion.setAngles("HeadPitch", pitch, 0.2)
                    time.sleep(1.0)
                    
                    if not tracker.isTargetLost():
                        print(f"Face detected at yaw: {yaw}, pitch: {pitch}")
                        face_detected = True
                        break
            
            if not face_detected:
                print("No face detected during scan")
                tracker.stopTracker()
                tracker.unregisterAllTargets()
                motion.setAngles("HeadYaw", original_head_yaw, 0.2)
                motion.setAngles("HeadPitch", original_head_pitch, 0.2)
                motion.setStiffnesses("Head", 0.0)
        
        tracker.track("Face")
        print("Start tracking face")
        return tracker
    
    def continuous_monitor_state(self, stop_event: threading.Event, attention_list: List[float]):
        """
        持续监控访客状态
        
        Args:
            stop_event: 停止事件
            attention_list: 注意力值列表
        """
        self.life.setState("solitary")
        tracker = self.tracker_face()
        
        try:
            print("Continuous tracking started")
            
            while not stop_event.is_set():
                try:
                    if not tracker.isTargetLost():
                        emotion_data = self.emotion_proxy.currentPersonState()
                        valence = emotion_data[0][1][0][1]
                        attention = emotion_data[1][1][0][1]
                        attention_list.append(attention)
                        print(f"Continuous monitoring - Valence: {valence}, Attention: {attention}")
                        self.attention_records.append([
                            datetime.datetime.now(),
                            valence,
                            attention
                        ])
                    time.sleep(5)
                except Exception as e:
                    print(f"Error in continuous monitoring: {e}")
                    time.sleep(5)
        except Exception as e:
            print(f"Error in continuous monitoring: {e}")
        finally:
            try:
                tracker.stopTracker()
                tracker.unregisterAllTargets()
                print("Continuous tracking stopped")
            except:
                pass
    
    def set_home_position(self) -> bool:
        """
        设置home位置
        
        Returns:
            是否成功设置
        """
        self.life.setState("solitary")
        self.localization.learnHome()
        self.life.setState("disabled")
        time.sleep(1)
        
        try:
            current_pose = self.localization.getRobotPosition(False)
            self.memory.insertData("HomePosition", current_pose)
            print("Home position set to:", current_pose)
            return True
        except Exception as e:
            print(f"Error setting home position: {e}")
            return False
    
    def navigate_to_home(self) -> bool:
        """
        导航回home位置
        
        Returns:
            是否成功导航
        """
        try:
            print("Navigating to home position...")
            self.localization.goToHome()
            return True
        except Exception as e:
            print(f"Error navigating to home position: {e}")
            return False
    
    def handle_exhibit_interaction(self, mark_id: int):
        """
        处理展品交互
        
        Args:
            mark_id: 展品ID
        """
        # 移动到展品位置后旋转
        self.motionProxy.moveTo(0, 0, 2.5)
        
        # 启动持续监控
        stop_monitoring = threading.Event()
        attention_measurements = []
        monitor_thread = threading.Thread(
            target=self.continuous_monitor_state,
            args=(stop_monitoring, attention_measurements)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 初始介绍
        self.introduction_markid(mark_id)
        
        # 根据注意力水平响应
        if len(self.attention_records) > 0:
            attention = self.attention_records[-1][2]
            if attention >= 0.7:
                self.tts.say("You look quite interested in this exhibit! Let me share more history with you.")
                if mark_id == 80:
                    self.tts.say(
                        "The Starry Night shows Van Gogh's early move toward expressionism, using bold forms to "
                        "convey emotion rather than realism. The cypress tree, not seen from his window, "
                        "was added from imagination and often symbolizes eternity. Though now iconic, Van Gogh didn't "
                        "think highly of the painting and called it a 'failure' in a letter to his brother."
                    )
                    self.tts.say("Feel free to ask any questions about this painting.")
                elif mark_id == 84:
                    self.tts.say(
                        "Monet's Water Lilies were part of a grand vision. He saw them as a peaceful refuge and arranged "
                        "their display in a specially designed oval room in Paris. Despite cataracts, which may have "
                        "influenced the dreamy, blurred forms, he kept painting. Some panels stretch over six feet, immersing "
                        "viewers in water and light."
                    )
                    self.tts.say("Feel free to ask any questions about this painting.")
            elif 0.4 <= attention < 0.7:
                self.tts.say("You seem a bit indifferent. That's okay! Feel free to ask any questions about this painting.")
            else:
                self.tts.say("You don't look very interested.")
        else:
            self.tts.say("You seem a bit indifferent. That's okay! Feel free to ask any questions about this painting.")
        
        self.tts.say("Say 'move on' to go to another exhibit, or 'stop' to wrap the whole visit up.")
        
        # 交互式Q&A循环
        end = False
        move = False
        
        while True:
            user_input = self.listen_for_human_response().decode("utf-8").strip()
            
            tokens = user_input.lower().split()
            tokens = [t.strip(string.punctuation) for t in tokens]
            
            if "stop" in tokens:
                end = True
                break
            elif "move on" in user_input.lower():
                move = True
                break
            else:
                response = self.llm_service.query(user_input, mark_id)
                self.tts.say(response)
            
            # 根据注意力提供反馈
            if len(self.attention_records) > 0:
                attention = self.attention_records[-1][2]
                if attention >= 0.7:
                    self.tts.say("You look quite interested in this exhibit!")
                    if mark_id == 80:
                        self.tts.say("Anything else you want to know about The Starry Night?")
                    elif mark_id == 84:
                        self.tts.say("Anything else you want to know about this Monet?")
                elif 0.4 <= attention < 0.7:
                    self.tts.say("You seem a bit indifferent. No problem! Feel free to ask anything about this painting.")
                else:
                    self.tts.say("You don't look very interested.")
            else:
                self.tts.say("You seem a bit indifferent. That's okay! Feel free to ask any questions about this painting.")
            
            self.tts.say("Alternatively, say 'move on' to go to another exhibit, or 'stop' to wrap the whole visit up.")
        
        # 停止监控
        stop_monitoring.set()
        monitor_thread.join(timeout=2)
        
        return end, move
    
    def run(self):
        """运行主导览流程"""
        time.sleep(2)
        self.set_home_position()
        
        self.tts.say("Hello and welcome to my museum! Allow me to show you around!")
        self.motionProxy.wakeUp()
        
        while True:
            # 获取展品状态
            self.occupied_exhibits = self.listen_for_exhibit_status().decode('utf-8')
            
            # 检测NAOMark
            result = self.detect_naomark()
            if not result:
                print("No NAO mark detected. Please try again.")
                continue
            
            # 移动到检测到的NAOMark
            mark_id, alpha, beta, width, height = result
            self.move_to_naomark(alpha, beta, width)
            
            # 处理展品交互
            end, move = self.handle_exhibit_interaction(mark_id)
            
            # 处理后续决策
            if move:
                self.navigate_to_home()
                if len(self.detected_exhibit_ids) == len(exhibit_config.total_exhibit_ids):
                    self.tts.say("You've now seen everything in the museum. I hope you enjoyed your visit!")
                    return
            elif end:
                self.tts.say("Thanks for your visit today! Have a wonderful day.")
                self.navigate_to_home()
                return
            else:
                self.navigate_to_home()
                self.life.setState("disabled")


def main():
    """主函数"""
    controller = RobotController()
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nShutting down robot controller...")
    finally:
        print(controller.attention_records)


if __name__ == "__main__":
    main()

