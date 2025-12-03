"""
Choregraphe LLM集成脚本
用于在Choregraphe中调用LLM服务
"""
from naoqi import ALProxy
import requests
import json


class MyClass(GeneratedClass):
    """Choregraphe生成的类，用于LLM集成"""
    
    def __init__(self):
        GeneratedClass.__init__(self)
    
    def onLoad(self):
        """加载时的初始化代码"""
        pass
    
    def onUnload(self):
        """卸载时的清理代码"""
        pass
    
    def fetch_data(self):
        """获取LLM数据"""
        # LLaMA服务URL
        llama_url = "http://192.168.1.22:8080/completion"  # 替换为你的计算机IP
        headers = {"Content-Type": "application/json"}
        
        # 示例提示词
        prompt = "Hi!"
        
        # POST请求数据
        data = {
            "prompt": prompt,
            "n_predict": 50,
            "temperature": 0.7,
            "top_k": 10,
            "top_p": 0.8
        }
        
        try:
            print("=====> 11111")
            # 同步发送POST请求
            response = requests.post(llama_url, headers=headers, data=json.dumps(data))
            llama_response = response.json()  # 等待响应
            print("=====> 22222")
            print("LLaMA Response:", llama_response)
            
            # 检查响应中是否有'content'键
            if 'content' in llama_response:
                print('=====> 333333')
                response_text = llama_response['content'].strip()
                response_text = str(response_text)
                print("=====> 444444:", response_text)
                
                # 输出响应文本（传递给输出槽）
                self.response(response_text)  # 请求完成后执行
            else:
                print("LLaMA did not return any text.")
                self.response("No text returned from LLaMA service.")
        
        except Exception as e:
            print(f"Error calling LLaMA service: {e}")
            self.response("Error calling LLaMA service")
        
        self.onStopped()  # 触发停止事件以结束模块
    
    def onInput_onStart(self):
        """输入onStart时调用"""
        # 同步调用fetch_data()并等待响应
        self.fetch_data()  # 这将阻塞直到请求完成并设置响应
    
    def onInput_onStop(self):
        """输入onStop时调用"""
        self.onUnload()  # 清理资源
        self.onStopped()  # 停止模块

