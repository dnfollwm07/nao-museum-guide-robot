"""
TTS测试脚本
测试NAO机器人的文本转语音功能
"""
from naoqi import ALProxy
import time

ROBOT_IP = "192.168.1.25"
ROBOT_PORT = 9559

tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
tts.say("Hello!")

