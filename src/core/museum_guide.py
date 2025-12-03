"""
博物馆导览核心模块
提供博物馆导览机器人的主要功能类
"""
from naoqi import ALProxy
import time
import json
import logging
from typing import List, Set, Optional
from ..models.exhibit import Exhibit, EmotionState
from ..utils.config import robot_config


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MuseumGuide:
    """博物馆导览机器人主类"""
    
    def __init__(self, robot_ip: Optional[str] = None, port: Optional[int] = None):
        """
        初始化博物馆导览机器人
        
        Args:
            robot_ip: 机器人IP地址，如果为None则使用配置中的默认值
            port: 机器人端口，如果为None则使用配置中的默认值
        """
        self.robot_ip = robot_ip or robot_config.ip
        self.port = port or robot_config.port
        self.exhibits = self._initialize_exhibits()
        self.visited_exhibits: Set[int] = set()
        self.current_emotion = EmotionState.NEUTRAL
        self._initialize_proxies()
    
    def _initialize_proxies(self):
        """初始化NAO机器人代理"""
        try:
            self.motion = ALProxy("ALMotion", self.robot_ip, self.port)
            self.tts = ALProxy("ALTextToSpeech", self.robot_ip, self.port)
            self.localization = ALProxy("ALLocalization", self.robot_ip, self.port)
            self.people_perception = ALProxy("ALPeoplePerception", self.robot_ip, self.port)
            self.speech_recognition = ALProxy("ALSpeechRecognition", self.robot_ip, self.port)
            self.memory = ALProxy("ALMemory", self.robot_ip, self.port)
            logger.info("All NAO proxies initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NAO proxies: {e}")
            raise
    
    def _initialize_exhibits(self) -> List[Exhibit]:
        """
        初始化展品数据
        
        Returns:
            展品列表
        """
        return [
            Exhibit(
                id=1,
                x=0.5,
                y=0.0,
                theta=0.0,
                description="Welcome to Exhibit 1.",
                detailed_description="This exhibit showcases ancient artifacts..."
            ),
            Exhibit(
                id=2,
                x=0.25,
                y=0.43,
                theta=1.05,
                description="This is Exhibit 2.",
                detailed_description="Here we have a collection of medieval paintings..."
            ),
            # 可以在这里添加更多展品
        ]
    
    def learn_environment(self) -> bool:
        """
        学习并保存初始位置
        
        Returns:
            是否成功学习环境
        """
        try:
            self.motion.wakeUp()
            loc_status = self.localization.learnHome()
            
            if loc_status == 0:
                logger.info("Home position learned successfully")
                self.localization.save("home_position")
                return True
            else:
                logger.error(f"Failed to learn home position. Error: {loc_status}")
                return False
        except Exception as e:
            logger.error(f"Error learning environment: {e}")
            return False
    
    def detect_emotion(self) -> EmotionState:
        """
        检测访客的情感状态
        
        Returns:
            情感状态枚举值
        """
        # TODO: 实现实际的情感检测
        return EmotionState.NEUTRAL
    
    def adjust_explanation(self, exhibit: Exhibit) -> str:
        """
        根据访客情感调整解释内容
        
        Args:
            exhibit: 展品对象
            
        Returns:
            调整后的解释文本
        """
        base_description = exhibit.description
        # TODO: 根据情感状态调整描述
        return base_description
    
    def check_exhibit_occupancy(self, exhibit: Exhibit) -> bool:
        """
        检查展品是否被占用（通过外部相机）
        
        Args:
            exhibit: 展品对象
            
        Returns:
            是否被占用
        """
        # TODO: 实现实际的占用检测
        return False
    
    def go_to_exhibit(self, exhibit_id: int) -> bool:
        """
        导航到指定展品
        
        Args:
            exhibit_id: 展品ID
            
        Returns:
            是否成功导航到展品
        """
        exhibit = next((e for e in self.exhibits if e.id == exhibit_id), None)
        if exhibit is None:
            logger.error(f"Exhibit {exhibit_id} not found")
            return False
        
        if self.check_exhibit_occupancy(exhibit):
            self.suggest_alternative_exhibit(exhibit_id)
            return False
        
        try:
            self.motion.moveTo(exhibit.x, exhibit.y, exhibit.theta)
            self.motion.waitUntilMoveIsFinished()
            
            # 更新情感并调整解释
            self.current_emotion = self.detect_emotion()
            explanation = self.adjust_explanation(exhibit)
            
            self.tts.say(explanation)
            self.visited_exhibits.add(exhibit_id)
            exhibit.visited = True
            
            return True
        except Exception as e:
            logger.error(f"Error navigating to exhibit: {e}")
            return False
    
    def suggest_alternative_exhibit(self, current_exhibit_id: int):
        """
        当请求的展品被占用时，建议替代展品
        
        Args:
            current_exhibit_id: 当前展品ID
        """
        self.tts.say("This exhibit is currently busy. Would you like to visit another exhibit?")
        # TODO: 基于受欢迎程度和距离实现智能展品推荐
    
    def return_to_home(self) -> bool:
        """
        返回初始位置
        
        Returns:
            是否成功返回
        """
        try:
            self.localization.goToHome()
            return True
        except Exception as e:
            logger.error(f"Error returning to home: {e}")
            return False
    
    def collect_feedback(self):
        """收集访客对导览的反馈"""
        # TODO: 实现反馈收集机制
        pass
    
    def save_tour_data(self):
        """保存导览数据用于分析"""
        tour_data = {
            "visited_exhibits": list(self.visited_exhibits),
            "timestamp": time.time()
        }
        try:
            with open("tour_data.json", "a") as f:
                json.dump(tour_data, f)
                f.write("\n")
        except Exception as e:
            logger.error(f"Error saving tour data: {e}")


def main():
    """主函数，用于独立运行博物馆导览系统"""
    guide = MuseumGuide()
    
    if not guide.learn_environment():
        logger.error("Failed to learn environment")
        return
    
    # 示例导览序列
    try:
        for exhibit in guide.exhibits:
            guide.go_to_exhibit(exhibit.id)
            time.sleep(2)  # 展品之间等待
        
        guide.return_to_home()
        guide.save_tour_data()
    except Exception as e:
        logger.error(f"Error during tour: {e}")
        guide.return_to_home()


if __name__ == "__main__":
    main()

