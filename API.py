import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("未找到OPENAI_API_KEY环境变量，请确保.env文件中包含该变量")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 加载gsm8k_cod.yaml配置文件
try:
    with open('gsm8k_cod.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    system_prompt = config.get('system_prompt', '')
except Exception as e:
    print(f"加载配置文件失败: {e}")
    system_prompt = "Think step by step, but only keep minimum draft for each thinking step, with 5 words at most.\nReturn the answer at the end of the response after a separator ####."

def get_ai_response(prompt):
    """
    获取AI对提示的回复
    
    Args:
        prompt (str): 提示词
        
    Returns:
        str: AI的回复内容
    """
    try:
        # 创建消息列表，包含系统提示和用户提示
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 创建聊天完成请求
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages
        )
        
        # 返回AI的回复内容
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用错误: {str(e)}"

def chat_with_ai(user_message, history=None):
    """
    与AI进行对话，并获取回复内容和推理过程
    
    Args:
        user_message (str): 用户输入的消息
        history (list, optional): 历史对话记录，格式为[{"role": "...", "content": "..."}]
    
    Returns:
        tuple: (content, reasoning_content) 返回AI的回复内容和推理内容
    """
    # 如果没有提供历史记录，则创建一个新的消息列表
    if history is None:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    else:
        # 使用提供的历史记录，并添加系统提示和新的用户消息
        messages = history.copy()
        # 确保第一条消息是系统提示
        if not messages or messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
    
    # 创建聊天完成请求
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=True
    )
    
    # 处理流式响应
    reasoning_content = ""
    content = ""
    
    for chunk in response:
        if chunk.choices[0].delta.reasoning_content:
            reasoning_content += chunk.choices[0].delta.reasoning_content
        elif chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
    
    return content, reasoning_content

