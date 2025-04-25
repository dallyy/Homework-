# -*- coding: utf-8 -*-
"""
ai_application_question.py
AI自动生成应用题及答案逻辑模块
"""
import random
import math
from API import get_ai_response

class AIApplicationQuestion:
    def __init__(self):
        pass

    def generate_question_and_answer(self):
        # 优先调用AI大模型API生成题目和答案
        try:
            prompt = "请生成一道小学数学应用题，并给出标准答案，格式为：题目：xxx\n答案：yyy"
            content = get_ai_response(prompt)
            if "题目：" in content and "答案：" in content:
                q = content.split("题目：",1)[1].split("答案：",1)
                question = q[0].strip()
                answer = q[1].strip()
                return question, answer
        except Exception as e:
            pass
        # 回退到模板生成
        templates = [
            ("小明有{a}个苹果，又买了{b}个，现在有多少个苹果？", lambda a, b: a + b),
            ("一辆汽车每小时行驶{a}公里，{b}小时后行驶了多少公里？", lambda a, b: a * b),
            ("妈妈买了{a}个鸡蛋，做菜用了{b}个，还剩多少个？", lambda a, b: a - b),
            ("一个长方形长{a}厘米，宽{b}厘米，面积是多少平方厘米？", lambda a, b: a * b),
            ("一瓶水重{a}克，又加了{b}克，现在有多少克？", lambda a, b: a + b),
            ("小红有{a}元钱，买了{b}元的文具，还剩多少钱？", lambda a, b: a - b),
            ("一辆火车每小时行驶{a}公里，{b}小时后行驶了多少公里？", lambda a, b: a * b),
            ("一根绳子长{a}米，剪去{b}米，还剩多少米？", lambda a, b: a - b),
            ("一个班有{a}个男生，{b}个女生，班里共有多少人？", lambda a, b: a + b),
            ("一桶油重{a}千克，倒出{b}千克，还剩多少千克？", lambda a, b: a - b),
            ("小明买了{a}支铅笔，每支{b}元，一共花了多少钱？", lambda a, b: a * b),
            ("一本书有{a}页，小明每天看{b}页，几天能看完？", lambda a, b: math.ceil(a / b)),
        ]
        idx = random.randint(0, len(templates)-1)
        a = random.randint(5, 100)
        b = random.randint(2, 30)
        q_tpl, ans_func = templates[idx]
        question = q_tpl.format(a=a, b=b)
        answer = str(ans_func(a, b))
        return question, answer
