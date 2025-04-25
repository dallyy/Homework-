import os
import yaml
import re
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

def convert_latex_to_readable(text):
    """将LaTeX数学公式转换为更易读的格式，递归处理$...$、\(...\)、\begin{...}...\end{...}等结构
    Args:
        text (str): 包含LaTeX代码的文本
    Returns:
        str: 转换后的易读文本
    """
    import re as _re
    if not isinstance(text, str):
        return text
    # 1. 递归处理$...$结构
    def remove_dollar(match):
        inner = match.group(1)
        return convert_latex_to_readable(inner)
    text = _re.sub(r'\${1,2}([^$]+)\${1,2}', remove_dollar, text)
    # 2. 递归处理\(...\)结构
    text = _re.sub(r'\\\((.*?)\\\)', lambda m: convert_latex_to_readable(m.group(1)), text)
    # 3. 递归处理\begin{...}...\end{...}结构
    def begin_end_repl(match):
        inner = match.group(2)
        return convert_latex_to_readable(inner)
    text = _re.sub(r'\\begin\{[^}]+\}(.*?)\\end\{[^}]+\}', begin_end_repl, text, flags=_re.DOTALL)
    # 4. 定义LaTeX符号到易读格式的映射
    replacements = {
        r'\\frac\{([^{}]+)\}\{([^{}]+)\}': r'(\1)/(\2)',
        r'\\sqrt\{([^{}]+)\}': r'√(\1)',
        r'\\sum_': '∑',
        r'\\prod_': '∏',
        r'\\int_': '∫',
        r'\\infty': '∞',
        r'\\pi': 'π',
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\delta': 'δ',
        r'\\theta': 'θ',
        r'\\lambda': 'λ',
        r'\\mu': 'μ',
        r'\\sigma': 'σ',
        r'\\omega': 'ω',
        r'\\leq': '≤',
        r'\\geq': '≥',
        r'\\neq': '≠',
        r'\\approx': '≈',
        r'\\times': '×',
        r'\\div': '÷',
        r'\\pm': '±',
        r'\\cdot': '·',
        r'(?<![\\^])\^\{([^{}]+)\}': r'^(\1)',
        r'(?<![\\_])_\{([^{}]+)\}': r'_(\1)',
        r'\\left': '',
        r'\\right': '',
        r'\\\\': '\n'
    }
    for pattern, replacement in replacements.items():
        text = _re.sub(pattern, replacement, text)
    # 移除残留的$和\(\)
    text = _re.sub(r'\$', '', text)
    text = _re.sub(r'\\\(|\\\)', '', text)
    # 清理多余空白
    text = _re.sub(r'\s+', ' ', text).strip()
    return text

def get_ai_response(prompt):
    """获取AI对提示的回复
    
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
        
        # 获取回复内容并转换LaTeX公式
        content = response.choices[0].message.content
        return convert_latex_to_readable(content)
    except Exception as e:
        return f"API调用错误: {str(e)}"

def chat_with_ai(user_message, history=None, timeout=30):
    """与AI进行对话，并获取回复内容和推理过程
    
    Args:
        user_message (str): 用户输入的消息
        history (list, optional): 历史对话记录，格式为[{"role": "...", "content": "..."}]
        timeout (int, optional): API请求超时时间，默认30秒
    
    Returns:
        tuple: (content, reasoning_content) 返回AI的回复内容和推理内容
    """
    try:
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
        
        # 创建聊天完成请求，设置超时和重试参数
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=True,
            timeout=max(30, timeout)  # 确保最小超时时间为30秒
        )
        
        # 处理流式响应
        reasoning_content = ""
        content = ""
        
        for chunk in response:
            if not chunk or not hasattr(chunk, 'choices') or not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            # 健壮性增强：类型和内容判断
            if hasattr(delta, 'reasoning_content') and isinstance(delta.reasoning_content, str) and delta.reasoning_content:
                reasoning_content += delta.reasoning_content
            elif hasattr(delta, 'content') and isinstance(delta.content, str) and delta.content:
                content += delta.content
        
        # 检查是否获取到内容
        if not content and not reasoning_content:
            raise Exception("未能获取到有效的AI回复内容")
            
        # 转换LaTeX公式为易读格式
        content = convert_latex_to_readable(content)
        reasoning_content = convert_latex_to_readable(reasoning_content)
        
        return content, reasoning_content
        
    except Exception as e:
        error_msg = f"AI回复出错: {e!r}"
        return error_msg, ""

