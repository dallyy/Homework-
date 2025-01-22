import tkinter as tk
from tkinter import messagebox
import time
from homework_logic import Homework

class App:
    __slots__ = ['hw', 'root', 'rating_label', 'entry', 'q_label','start_time','result_list']

    def __init__(self, root):
        self.hw = Homework()
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        """主界面：答题界面"""
        self.clear_root()
        self.root.title("作业推荐")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f8ff")
        
        # 显示学力
        self.rating_label = self.create_label(f"学力：{self.hw.student['rating']:.2f}", 14, anchor="nw", padx=10, pady=10)
        
        # 显示当前题目
        self.display_question()

        # 控件列表
        buttons = [
            ("提交", self.submit),
            ("难度筛选", self.open_filter_page),
            ("结束", self.end)
        ]
        
        # 创建输入框和按钮
        self.entry = self.create_entry(30)
        for text, command in buttons:
            self.create_button(text, command)

        self.start_quiz()

    def create_label(self, text, font_size, **kwargs):
        label = tk.Label(self.root, text=text, font=("Arial", font_size), bg="#f0f8ff", **kwargs)
        label.pack()
        return label

    def create_entry(self, width):
        entry = tk.Entry(self.root, font=("Arial", 12), justify="center", relief="solid", width=width)
        entry.pack(pady=10)
        entry.bind("<Return>", lambda event: self.submit())
        return entry

    def create_button(self, text, command):
        button = tk.Button(self.root, text=text, font=("Arial", 12), bg="#87CEFA", fg="white", width=10, relief="flat", command=command)
        button.pack(pady=10)
        return button

    def display_question(self):
        """根据题目状态显示题目"""
        if self.hw.cur_q:
            question_text = self.hw.cur_q.q
        else:
            self.hw.cur_q = self.hw.recommend(correct=True)
            question_text = self.hw.cur_q.q if self.hw.cur_q else "没有更多题目！"
        
        self.q_label = self.create_label(question_text, 12, pady=20)

    def start_quiz(self):
        """启动计时器"""
        self.start_time = time.time()

    def refresh_ui(self):
        """刷新主界面UI"""
        self.rating_label.config(text=f"学力：{self.hw.student['rating']:.2f}")
        self.q_label.config(text=self.hw.cur_q.q if self.hw.cur_q else "没有更多题目！")
        self.entry.delete(0, tk.END)

    def submit(self):
        """提交答案"""
        if not self.hw.cur_q:
            return messagebox.showerror("错误", "没有当前题目！")

        elapsed = time.time() - self.start_time
        user_answer = self.entry.get()

        try:
            correct = self.hw.evaluate_answer(self.hw.cur_q, user_answer)
            self.hw.update_rating(self.hw.cur_q, correct, elapsed)
            messagebox.showinfo("结果", "正确" if correct else "错误")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的答案格式！\n{e}")
            return
        except Exception as e:
            messagebox.showerror("错误", f"未知错误：{e}")
            return

        # 更新问题并刷新UI
        self.hw.cur_q = self.hw.recommend(correct)
        self.refresh_ui()
        self.start_time = time.time()

    def open_filter_page(self):
        """切换到筛选页面"""
        self.clear_root()

        # 创建筛选页面的标题和布局
        self.create_label("题目难度筛选", 14, pady=20)

        diff_frame = tk.Frame(self.root, bg="#f0f8ff")
        diff_frame.pack(pady=10)

        # 批量创建输入框
        diff_min_entry = self.create_entry(10)
        diff_max_entry = self.create_entry(10)

        # 为输入框绑定回车键事件，触发筛选操作
        diff_min_entry.bind("<Return>", lambda event: self.filter_by_diff(diff_min_entry, diff_max_entry))
        diff_max_entry.bind("<Return>", lambda event: self.filter_by_diff(diff_min_entry, diff_max_entry))

        # 批量创建按钮
        buttons = [("筛选", lambda: self.filter_by_diff(diff_min_entry, diff_max_entry)), ("返回", self.setup_ui)]
        for text, command in buttons:
            self.create_button(text, command)

        # 创建列表框
        self.result_list = self.create_listbox()

    def create_listbox(self):
        result_list = tk.Listbox(self.root, font=("Arial", 12), height=10, relief="solid")
        result_list.pack(pady=10)
        result_list.bind("<<ListboxSelect>>", self.select_question)
        return result_list

    def filter_by_diff(self, diff_min_entry, diff_max_entry):
        """根据难度筛选题目"""
        try:
            diff_min = int(diff_min_entry.get()) if diff_min_entry.get() else None
            diff_max = int(diff_max_entry.get()) if diff_max_entry.get() else None
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字范围！")
            return

        results = self.hw.search_by_diff(diff_min, diff_max)
        self.result_list.delete(0, tk.END)
        for q in results:
            self.result_list.insert(tk.END, f"{q.id}: {q.q}(难度：{q.diff})")

    def select_question(self, event):
        """选择题目并返回主界面"""
        try:
            selection = self.result_list.get(self.result_list.curselection())
            q_id = int(selection.split(":")[0])
            self.hw.cur_q = next(q for q in self.hw.q_bank if q.id == q_id)
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("错误", f"无法选择题目！\n{str(e)}")

    def clear_root(self):
        """清空当前界面"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def end(self):
        """结束答题"""
        messagebox.showinfo("结束", f"提交次数：{self.hw.done}\n最终学力:{self.hw.student['rating']:.2f}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
