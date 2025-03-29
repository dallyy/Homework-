from collections import namedtuple
from sortedcontainers import SortedSet
import Un
from fractions import Fraction
Question = namedtuple('Question', ['id', 'diff', 'q', 'limit'])

class Homework:
    def __init__(self):
        self.student = {"name": "张三", "rating": 1000}
        self.q_bank = None
        self.update_q_bank()
        self.cur_q = None
        self.done = 0
        self.next_id = 22  # 下一个题目的ID

    def update_q_bank(self):
        question_list = [
            Question(1, 800, "12/5 *2= ?", 12),
            Question(2, 800, "3 + 1 = ?", 10),
            Question(3, 1000, "5 * 5 = ?", 15),
            Question(4, 1000, "2*(5+5*2)/3+(6/2+8)= ?", 15),
            Question(5, 1200, "12 / 4+2+3 = ?", 20),
            Question(6, 1200, "3 * 4 = ?", 20),
            Question(7, 1400, "25 + 37 = ?", 25),
            Question(8, 1400, "50 - 13 = ?", 25),
            Question(10, 1600, "9 * 9 = ?", 30),
            Question(13, 2000, "1/2 + 1/3 = ?", 30),
            Question(14, 2000, "1 + 1/2 = ?", 30),
            Question(15, 2000, "1/2 * 3/4 = ?", 30),
            Question(16, 2000, "1/2 / 1/4 = ?", 30),
            Question(20, 2000, "(1/2) / (1/4) = ?", 30),
            Question(21, 2000, "(2*(5+5*2)/3+(6/2+8))/2 = ?", 30),
            Question(17, 1500, "3 + 2x = 7x+1", 20),
            Question(18, 1500, "3x-5=10", 20),
            Question(19, 1500, "6 - 3x =10", 20),
        ]

        self.q_bank = SortedSet(question_list, key=lambda q: abs(q.diff - self.student["rating"]))

    def add_question(self, question_text, difficulty):
        """添加新题目，并验证题目是否符合要求"""
        if not self.is_valid_question(question_text):
            raise ValueError("题目不符合要求，只能添加整分数的四则运算或一元一次方程的题目。")

        new_question = Question(self.next_id, difficulty, question_text, 30)
        self.q_bank.add(new_question)
        self.next_id += 1

    def is_valid_question(self, question_text):
        """验证题目是否符合要求：整分数的四则运算或一元一次方程"""
        if "x" in question_text:
            # 检查是否为一元一次方程
            try:
                Un.solve_equation(question_text)
                return True
            except:
                return False
        else:
            # 检查是否为整分数的四则运算
            try:
                expression = question_text.replace("=", "").replace("?", "").strip()
                Un.evaluate(expression, 0)  # 仅验证表达式是否有效
                return True
            except:
                return False


    def recommend(self, correct):
        self.q_bank = SortedSet(self.q_bank, key=lambda q: abs(q.diff - self.student["rating"]))
        if correct:return self.q_bank.pop(0)
        else:
            return self.cur_q

    def update_rating(self, q, correct, time_taken):
        threshold_time = 10
        time_factor = max(0.5, 1 - (time_taken / threshold_time)) if correct else 1 + max(0, (time_taken - threshold_time) / threshold_time)
        e = 1 / (1 + 10 ** ((q.diff - self.student["rating"]) / 400))
        min_penalty = 10

        reward = 30 * time_factor * (1 - e) if correct else -max(min_penalty, 30 * e) * time_factor
        self.student["rating"] = max(800, min(2000, self.student["rating"] + reward))
        self.done += 1

    def search_by_diff(self, diff_min=None, diff_max=None):

        start_index = self.q_bank.bisect_left(Question(0, diff_min, '', 0)) if diff_min is not None else 0
        end_index = self.q_bank.bisect_right(Question(0, diff_max, '', 0)) if diff_max is not None else len(self.q_bank)
        return list(self.q_bank[start_index:end_index])

    def evaluate_answer(self, q, user_answer):
        user_answer=Fraction(user_answer)
        try:
            if 'x' in q.q:
                return user_answer == Un.solve_equation(q.q)
            
            expression = q.q.replace("=", "").replace("?", "").strip()
            return Un.evaluate(expression, user_answer)

        except Exception as e:
            print(f"错误：{e}")
            return False, None

