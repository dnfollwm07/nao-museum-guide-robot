"""
地标检测测试脚本
测试NAO机器人的NAOMark检测和导航功能
"""
from naoqi import ALProxy
import time
import math

ROBOT_IP = "192.168.1.25"
PORT = 9559

tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
tts.say("Hello!")

# 创建ALLandMarkDetection代理
try:
    landMarkProxy = ALProxy("ALLandMarkDetection", ROBOT_IP, PORT)
except Exception as e:
    print("Error when creating landmark detection proxy:")
    print(str(e))
    exit(1)

# 订阅ALLandMarkDetection代理
period = 500
landMarkProxy.subscribe("Test_LandMark", period, 0.0)

# ALMemory变量，ALLandMarkdetection模块输出结果的位置
memValue = "LandmarkDetected"

# 创建ALMemory代理
try:
    memoryProxy = ALProxy("ALMemory", ROBOT_IP, PORT)
except Exception as e:
    print("Error when creating memory proxy:")
    print(str(e))
    exit(1)

print("Creating landmark detection proxy")

# 简单循环，读取memValue并检查是否检测到地标
for i in range(0, 20):
    time.sleep(0.5)
    val = memoryProxy.getData(memValue, 0)
    print("")
    print("\*****")
    print("")

# 检查是否获得有效输出：包含两个字段的列表
if val and isinstance(val, list) and len(val) >= 2:
    # 检测到地标！
    # 对于每个标记，可以读取其形状信息和ID
    # 第一个字段 = 时间戳
    timeStamp = val[0]
    # 第二个字段 = Mark_Info数组
    markInfoArray = val[1]
    
    try:
        # 浏览markInfoArray以获取每个检测到的标记的信息
        for markInfo in markInfoArray:
            # 第一个字段 = 形状信息
            markShapeInfo = markInfo[0]
            # 第二个字段 = 额外信息（即标记ID）
            markExtraInfo = markInfo[1]
            # 打印标记信息
            print("mark  ID: %d" % (markExtraInfo[0]))
            tts.say("detected naomark id is:")
            tts.say(str(markExtraInfo[0]))
            print("  alpha %.3f - beta %.3f" % (markShapeInfo[1], markShapeInfo[2]))
            print("  width %.3f - height %.3f" % (markShapeInfo[3], markShapeInfo[4]))
            
            # 存储信息以计算距离
            alpha = markShapeInfo[1]
            beta = markShapeInfo[2]
            width = markShapeInfo[3]
            height = markShapeInfo[4]
    except Exception as e:
        print("Landmarks detected, but it seems getData is invalid. ALValue =")
        print(val)
        print("Error msg %s" % (str(e)))
else:
    print("Error with getData. ALValue = %s" % (str(val)))
    tts.say("time out, please try again")

# 取消订阅模块
landMarkProxy.unsubscribe("Test_LandMark")
print("Test terminated successfully.")

# 计算行走距离
real_mark_size = 0.1
distance = real_mark_size / width

motion = ALProxy("ALMotion", ROBOT_IP, PORT)
motion.wakeUp()

start_pos = motion.getRobotPosition(False)

x = distance * math.cos(beta) * math.cos(alpha)
y = distance * math.cos(beta) * math.sin(alpha)
theta = 0.0
frequency = 0.1  # 最大移动速度
motion.moveToward(x, y, theta, [["Frequency", frequency]])

while True:
    current_pos = motion.getRobotPosition(False)
    dx = current_pos[0] - start_pos[0]
    dy = current_pos[1] - start_pos[1]
    dist = math.hypot(dx, dy)
    if dist >= 0.3:
        break
    time.sleep(0.1)

motion.stopMove()

