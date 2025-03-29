import re
from fractions import Fraction
from collections import deque
def solve_equation(eq):
    eq = re.sub(r'\s+', '', eq)  
    exp = re.sub(r'\bx', '1x', eq).split('=')
    k, b = [], []
    
    # 对方程两边分别提取系数和常数
    for ex in exp:
        k.append(sum(int(kk) for kk in re.findall(r'([-+]?\d+)x', ex)))  # 提取 x 的系数
        b.append(sum(int(bb) for bb in re.findall(r'([-+]?\d+)\b', ex)))  # 提取常数项
    
    # 计算 K 和 B
    K, B = k[0] - k[1], b[1] - b[0]  # 系数相减，常数项相减

    # 判断方程是否有解
    if K == 0:
        return "任意解" if B == 0 else "无解"
    return Fraction(B, K)

def cal(s):
    stk = []
    sign = '+'
    num = 0
    while s:
        c = s.popleft()
        
        if c.isdigit(): 
            num = num * 10 + int(c)
        
        if c == '(':
            num = cal(s)  
        
        if c in "+-*/)" or not s:  
            if sign == '+':
                stk.append(num)
            elif sign == '-':
                stk.append(-num)
            elif sign == '*':
                stk[-1] = stk[-1] * num
            elif sign == '/':
                stk[-1] = Fraction (stk[-1] , num ) 
            num = 0
            sign = c
        
        if c == ')':
            break  
        
    return sum(stk)

def evaluate(expression: str, user_answer: str) -> bool:
    expression=expression.replace(" ", " ")
    try:
        return  Fraction(user_answer) == cal(expression:=deque(expression))
    except ZeroDivisionError:
        raise ValueError("除数不能为零")
    except Exception as e:
        raise ValueError(f"错误: {e}")

