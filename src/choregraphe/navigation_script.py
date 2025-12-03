"""
Choregraphe导航脚本
用于在Choregraphe中实现home位置学习和导航功能
"""
from naoqi import ALProxy
import time


ROBOT_IP = "192.168.1.30"
PORT = 9559


class MyClass(GeneratedClass):
    """Choregraphe生成的类，用于导航功能"""
    
    def __init__(self):
        GeneratedClass.__init__(self)
    
    def onLoad(self):
        """加载时的初始化代码"""
        pass
    
    def onUnload(self):
        """卸载时的清理代码"""
        pass
    
    def onInput_onStart(self):
        """输入onStart时调用"""
        # 初始化代理
        localization = ALProxy("ALLocalization", ROBOT_IP, PORT)
        motion = ALProxy("ALMotion", ROBOT_IP, PORT)
        navigation = ALProxy("ALNavigation", ROBOT_IP, PORT)
        memory = ALProxy("ALMemory", ROBOT_IP, PORT)
        
        # 步骤1: 让机器人学习当前位置作为home
        print("Learning home position...")
        localization.learnHome()
        time.sleep(1)  # 可选，确保位置学习完成
        
        # 步骤2: 获取当前坐标作为home
        current_pose = localization.getRobotPosition(False)
        memory.insertData("HomePosition", current_pose)
        print("Home position set to:", current_pose)
        
        # 步骤3: 向前走一小段
        print("Moving forward 0.3m...")
        motion.moveTo(0.3, 0, 0)
        
        # 步骤4: 回到home位置
        print("Returning to home...")
        home = memory.getData("HomePosition")
        if home:
            x, y, theta = home
            navigation.navigateToInMap([x, y, theta])
            print("Navigated to:", home)
        else:
            print("Error: Home position not found in ALMemory")
        
        self.onStopped()
    
    def onInput_onStop(self):
        """输入onStop时调用"""
        self.onUnload()  # 建议在停止时重用清理代码
        self.onStopped()  # 激活框的输出

