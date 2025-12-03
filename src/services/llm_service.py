"""
LLM服务模块
提供与LLaMA模型交互的功能，包括对话管理和响应生成
"""
import requests
import json
from typing import List, Tuple, Optional
from ..utils.config import llm_config


class LLMService:
    """LLM服务类，负责与LLaMA模型通信"""
    
    def __init__(self, config=None):
        """
        初始化LLM服务
        
        Args:
            config: LLM配置对象，如果为None则使用默认配置
        """
        self.config = config or llm_config
        self.conversation_history: List[Tuple[str, str]] = []
        self.max_history_exchanges = 5  # 保留最近5轮对话
    
    def _build_system_prompt(self, mark_id: Optional[int] = None) -> str:
        """
        构建系统提示词
        
        Args:
            mark_id: 展品ID，用于生成特定展品的提示词
            
        Returns:
            系统提示词字符串
        """
        base_prompt = """You are a museum guide robot interacting with a human visitor.

Behavior Rules:
- Only respond with information about the artwork listed below.
- Do NOT mention any artworks, locations, or artists not listed.
- Do NOT create anything fictional or speculate.
- Answer directly and concisely. Keep it factual and on-topic.
- Use a neutral, professional tone - avoid overly friendly or emotional responses.
- Do NOT say "Guide:" or narrate your own actions.
- Do NOT greet or say goodbye unless specifically asked.
- Respond with plain text and form a paragraph. 
- Do NOT use special/unicode characters in your response.
"""
        
        if mark_id == 80:
            base_prompt += """
Exhibit: *The Starry Night* by Vincent van Gogh  
- Painted in June 1889  
- Oil on canvas  
- Painted while Van Gogh was in an asylum in Saint-Remy-de-Provence  
- Features a swirling night sky over a quiet village with a cypress tree  
- Known for dynamic brushstrokes and vibrant blue-and-yellow contrast  
- Painted from memory, not direct observation
"""
        elif mark_id == 84:
            base_prompt += """
Exhibit: *Water Lilies* by Claude Monet  
- A series of around 250 paintings created between 1897 and 1926  
- Depicts Monet's flower garden in Giverny, especially the pond and its water lilies  
- Painted outdoors to capture natural light and color changes throughout the day  
- Known for soft, layered brushstrokes and a dreamy, abstracted sense of reflection  
- No human figures are present - focus is entirely on water, light, and nature  
"""
        else:
            # 默认提示词，包含两个展品的信息
            base_prompt += """
Exhibit 1: *Mona Lisa* by Leonardo da Vinci  
- Painted between 1503 and 1506, possibly as late as 1517  
- Oil on poplar panel  
- Housed in the Louvre Museum, Paris  
- Known for the subject's subtle smile and sfumato technique  
- Believed to depict Lisa Gherardini, a Florentine woman  
- Stolen in 1911, which increased its global fame  

Exhibit 2: *The Starry Night* by Vincent van Gogh  
- Painted in June 1889  
- Oil on canvas  
- Painted while Van Gogh was in an asylum in Saint-Rémy-de-Provence  
- Features a swirling night sky over a quiet village  
- Expressive, emotional style using thick brushwork  
- Housed in the Museum of Modern Art, New York  
"""
        
        return base_prompt
    
    def query(self, prompt: str, mark_id: Optional[int] = None) -> str:
        """
        查询LLM并获取响应
        
        Args:
            prompt: 用户输入的提示词
            mark_id: 展品ID，用于生成特定展品的响应
            
        Returns:
            LLM生成的响应文本
        """
        system_prompt = self._build_system_prompt(mark_id)
        full_prompt = system_prompt + "\n\nVisitor: " + prompt + "\nGuide:"
        
        data = {
            "prompt": full_prompt,
            "n_predict": self.config.n_predict,
            "temperature": self.config.temperature,
            "top_k": self.config.top_k,
            "top_p": self.config.top_p,
            "stop": ["\nVisitor:", "\n\nVisitor:"]
        }
        
        try:
            response = requests.post(
                self.config.url,
                headers=self.config.headers,
                data=json.dumps(data),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if 'content' in result:
                response_text = result['content'].strip()
                
                # 更新对话历史
                self.conversation_history.append(("user", prompt))
                self.conversation_history.append(("assistant", response_text))
                
                # 保持历史记录在限制范围内
                if len(self.conversation_history) > self.max_history_exchanges * 2:
                    self.conversation_history.pop(0)
                    self.conversation_history.pop(0)
                
                return response_text
            else:
                return "I'm sorry, I couldn't process your request properly."
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting LLM response: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now."
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now."
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
    
    def get_history(self) -> List[Tuple[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表，格式为[(role, message), ...]
        """
        return self.conversation_history.copy()


# 全局服务实例
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    获取LLM服务单例
    
    Returns:
        LLMService实例
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

