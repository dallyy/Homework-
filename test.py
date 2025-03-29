# -*- coding: utf-8 -*-
from tkinter import messagebox
import time
from homework_logic import Homework, Question
import tkinter as tk
from button_style import ButtonStyle
from tkinter import ttk


class UIComponents:
    """UI组件管理类"""
    @staticmethod
    def create_styled_entry(master, width=20, bind_submit=None):
        style = ttk.Style()
        style.configure("Rounded.TEntry", padding=5, relief="flat", borderwidth=0)
        
        entry = ttk.Entry(master, width=width, style="Rounded.TEntry", 
                         font=("Microsoft YaHei", 14), justify="center")
        entry.pack(pady=20)
        if bind_submit:
            entry.bind("<Return>", bind_submit)
        return entry
    
    @staticmethod
    def create_label(master, text, font_size, bg_color, **kwargs):
        label = tk.Label(
            master,
            text=text,
            font=("Microsoft YaHei", font_size),
            bg=bg_color,
            **kwargs
        )
        label.pack(pady=10)
        return label

class ThemeManager:
    """主题管理类"""
    THEMES = {
        '蓝色主题': {
            'start': {'r': 230, 'g': 243, 'b': 255},  # E6F3FF
            'end': {'r': 184, 'g': 226, 'b': 255}     # B8E2FF
        },
        '绿色主题': {
            'start': {'r': 230, 'g': 255, 'b': 230},  # E6FFE6
            'end': {'r': 184, 'g': 255, 'b': 184}     # B8FFB8
        },
        '紫色主题': {
            'start': {'r': 243, 'g': 230, 'b': 255},  # F3E6FF
            'end': {'r': 226, 'g': 184, 'b': 255}     # E2B8FF
        }
    }
    
    @staticmethod
    def get_theme_color(theme_name):
        theme = ThemeManager.THEMES[theme_name]
        start_color = "#{:02x}{:02x}{:02x}".format(
            theme['start']['r'],
            theme['start']['g'],
            theme['start']['b']
        )
        return start_color
    
    @staticmethod
    def create_gradient_background(master, theme_name, width=800, height=900):
        canvas = tk.Canvas(master, width=width, height=height, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        theme = ThemeManager.THEMES[theme_name]
        start, end = theme['start'], theme['end']
        
        for i in range(height):
            progress = i / height
            r = int(start['r'] - (start['r']-end['r'])*progress)
            g = int(start['g'] - (start['g']-end['g'])*progress)
            b = int(start['b'] - (start['b']-end['b'])*progress)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)

class App(tk.Tk):
    
    def clear_root(self):
        """清除窗口中的所有组件"""
        for widget in self.winfo_children():
            widget.destroy()
    def __init__(self):
        super().__init__()
        self.hw = Homework()
        self.current_theme = '蓝色主题'
        self.ui = UIComponents()
        self.chat_history = []  # 添加聊天历史记录列表
        self.setup_ui()

    def setup_ui(self):
        self.clear_root()
        self.title("作业推荐")
        self.geometry("800x900")
        
        ThemeManager.create_gradient_background(self, self.current_theme)
        self.setup_main_frame()
        self.start_quiz()

    def setup_main_frame(self):
        start_color = ThemeManager.get_theme_color(self.current_theme)
        content_frame = tk.Frame(self, bg=start_color)
        content_frame.place(relx=0.5, rely=0.1, anchor='n', relwidth=0.9, relheight=0.8)
        
        self.setup_rating_label(content_frame)
        self.setup_question_label(content_frame)
        self.setup_answer_entry(content_frame)
        self.setup_buttons(content_frame)

    def setup_rating_label(self, parent):
        start_color = ThemeManager.get_theme_color(self.current_theme)
        self.rating_label = UIComponents.create_label(
            parent,
            f"学力：{self.hw.student['rating']:.2f}",
            18,
            start_color,
            anchor="nw",
            padx=40,
            pady=40
        )

    def setup_question_label(self, parent):
        if self.hw.cur_q:
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷')
        else:
            self.hw.cur_q = self.hw.recommend(correct=True)
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷') if self.hw.cur_q else "没有更多题目！"
        
        start_color = ThemeManager.get_theme_color(self.current_theme)
        self.q_label = UIComponents.create_label(
            parent,
            question_text,
            16,
            start_color,
            pady=20
        )

    def setup_answer_entry(self, parent):
        self.entry = UIComponents.create_styled_entry(
            parent,
            bind_submit=lambda event: self.submit()
        )

    def setup_buttons(self, parent):
        start_color = ThemeManager.get_theme_color(self.current_theme)
        button_frame = tk.Frame(parent, bg=start_color)
        button_frame.pack(pady=30)
        
        buttons = [
            ("提交", self.submit),
            ("难度筛选", self.open_filter_page),
            ("增加题目", self.open_add_question_page),
            ("主题设置", self.open_theme_page),
            ("AI问答", self.open_ai_chat_page),
            ("结束", self.end)
        ]
        
        for text, command in buttons:
            ButtonStyle(button_frame, text, command)


    def add_question(self, question_entry, diff_entry):
        """添加题目"""
        question_text = question_entry.get().replace('×', '*').replace('÷', '/')
        try:
            difficulty = int(diff_entry.get())
            if difficulty < 800 or difficulty > 2000:
                raise ValueError("难度必须在800到2000之间。")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的难度值！\n{e}")
            return

        try:
            # 验证题目格式
            if not question_text.strip():
                raise ValueError("题目不能为空！")
            
            self.hw.add_question(question_text, difficulty)
            messagebox.showinfo("成功", "题目添加成功！")
            self.setup_ui()
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            
    


    def display_question(self):
        """根据题目状态显示题目"""
        if self.hw.cur_q:
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷')
        else:
            self.hw.cur_q = self.hw.recommend(correct=True)
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷') if self.hw.cur_q else "没有更多题目！"
        
        self.q_label = self.create_label(question_text, 16, pady=20)

    def start_quiz(self):
        """启动计时器"""
        self.start_time = time.time()

    def refresh_ui(self):
        """刷新主界面UI"""
        self.rating_label.config(text=f"学力：{self.hw.student['rating']:.2f}")
        self.q_label.config(text=self.hw.cur_q.q.replace('*', '×').replace('/', '÷') if self.hw.cur_q else "没有更多题目！")
        self.entry.delete(0, tk.END)

    def submit(self):
        """提交答案"""
        if not self.hw.cur_q:
            return messagebox.showerror("错误", "没有当前题目！")

        elapsed = time.time() - self.start_time
        user_answer = self.entry.get().replace('×', '*').replace('÷', '/')

        try:
            correct = self.hw.evaluate_answer(self.hw.cur_q, user_answer)
            self.hw.update_rating(self.hw.cur_q, correct, elapsed)
            messagebox.showinfo("结果", "正确" if correct else "错误")  # 显示结果消息框
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
        """打开难度筛选页面"""
        self.clear_root()
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        start_color = ThemeManager.get_theme_color(self.current_theme)
        content_frame = tk.Frame(self, bg=start_color)
        content_frame.place(relx=0.5, rely=0.1, anchor='n', relwidth=0.9, relheight=0.8)
        
        # 创建标题
        tk.Label(
            content_frame,
            text="题目难度筛选",
            font=("Microsoft YaHei", 24, 'bold'),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(0, 30))
        
        # 创建输入区域
        input_frame = tk.Frame(content_frame, bg=start_color)
        input_frame.pack(pady=20, fill='x')
        
        # 最小难度输入
        tk.Label(
            input_frame,
            text="最小难度：",
            font=("Microsoft YaHei", 16),
            bg=start_color,
            fg='#333333'
        ).pack()
        
        diff_min_entry = UIComponents.create_styled_entry(input_frame)
        
        # 最大难度输入
        tk.Label(
            input_frame,
            text="最大难度：",
            font=("Microsoft YaHei", 16),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(20, 0))
        
        diff_max_entry = UIComponents.create_styled_entry(input_frame)
        
        # 创建按钮区域
        button_frame = tk.Frame(content_frame, bg=start_color)
        button_frame.pack(pady=30)
        
        ButtonStyle(button_frame, "筛选", lambda: self.filter_by_diff(diff_min_entry, diff_max_entry))
        ButtonStyle(button_frame, "返回", self.setup_ui)
        
        # 创建结果列表
        self.result_list = tk.Listbox(
            content_frame,
            font=("Microsoft YaHei", 14),
            height=12,
            width=60,
            relief="flat",
            bg='#ffffff',
            fg='#333333',
            selectmode='single',
            activestyle='none'
        )
        self.result_list.pack(pady=20)
        self.result_list.bind("<<ListboxSelect>>", self.select_question)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.result_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_list.config(yscrollcommand=scrollbar.set)

    def open_theme_page(self):
        """打开主题设置页面"""
        self.clear_root()
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        start_color = ThemeManager.get_theme_color(self.current_theme)
        content_frame = tk.Frame(self, bg=start_color)
        content_frame.place(relx=0.5, rely=0.1, anchor='n', relwidth=0.9, relheight=0.8)
        
        # 创建标题
        tk.Label(
            content_frame,
            text="主题设置",
            font=("Microsoft YaHei", 24, 'bold'),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(0, 30))
        
        # 创建主题选择区域
        theme_frame = tk.Frame(content_frame, bg=start_color)
        theme_frame.pack(expand=True, fill="both", padx=50)
        
        for theme_name, theme_colors in ThemeManager.THEMES.items():
            theme_button_frame = tk.Frame(theme_frame, bg=start_color)
            theme_button_frame.pack(pady=15)
            
            # 创建主题预览
            preview = tk.Canvas(theme_button_frame, width=120, height=60, highlightthickness=1, highlightbackground="#ddd")
            preview.pack(side="left", padx=(0, 20))
            
            # 绘制渐变预览
            steps = 30
            height_per_step = 60 / steps
            for i in range(steps):
                progress = i / steps
                r = int(theme_colors['start']['r'] + (theme_colors['end']['r'] - theme_colors['start']['r']) * progress)
                g = int(theme_colors['start']['g'] + (theme_colors['end']['g'] - theme_colors['start']['g']) * progress)
                b = int(theme_colors['start']['b'] + (theme_colors['end']['b'] - theme_colors['start']['b']) * progress)
                color = f'#{r:02x}{g:02x}{b:02x}'
                
                y1 = i * height_per_step
                y2 = (i + 1) * height_per_step
                preview.create_rectangle(0, y1, 120, y2, fill=color, outline=color)
            
            # 创建主题按钮
            ButtonStyle(theme_button_frame, theme_name, lambda t=theme_name: self.change_theme(t))
        
        # 创建返回按钮
        button_frame = tk.Frame(content_frame, bg=start_color)
        button_frame.pack(pady=30)
        ButtonStyle(button_frame, "返回", self.setup_ui)


    def change_theme(self, theme_name):
        """切换主题"""
        self.current_theme = theme_name
        self.setup_ui()

    def filter_by_diff(self, diff_min_entry, diff_max_entry):
        """根据难度范围筛选题目"""
        try:
            diff_min = int(diff_min_entry.get()) if diff_min_entry.get() else None
            diff_max = int(diff_max_entry.get()) if diff_max_entry.get() else None

            if diff_min and diff_min < 800:
                raise ValueError("最小难度不能小于800")
            if diff_max and diff_max > 2000:
                raise ValueError("最大难度不能大于2000")
            if diff_min and diff_max and diff_min > diff_max:
                raise ValueError("最小难度不能大于最大难度")

            # 清空列表框
            self.result_list.delete(0, tk.END)

            # 获取筛选结果
            filtered_questions = self.hw.search_by_diff(diff_min, diff_max)

            # 显示结果
            for q in filtered_questions:
                display_text = f"难度: {q.diff} - {q.q.replace('*', '×').replace('/', '÷')}"
                self.result_list.insert(tk.END, display_text)

        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def select_question(self, event):
        """从列表中选择题目"""
        selection = self.result_list.curselection()
        if not selection:
            return

        # 获取选中的题目文本
        selected_text = self.result_list.get(selection[0])
        difficulty = int(selected_text.split(':')[1].split('-')[0].strip())

        # 在题库中查找对应的题目
        for q in self.hw.q_bank:
            if q.diff == difficulty and q.q.replace('*', '×').replace('/', '÷') in selected_text:
                self.hw.cur_q = q
                self.setup_ui()
                break



    def __init__(self):
        super().__init__()
        self.hw = Homework()
        self.current_theme = '蓝色主题'
        self.ui = UIComponents()
        self.chat_history = []  # 添加聊天历史记录列表
        self.setup_ui()
        
    def open_add_question_page(self):
        """打开添加题目页面"""
        self.clear_root()
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        start_color = ThemeManager.get_theme_color(self.current_theme)
        content_frame = tk.Frame(self, bg=start_color)
        content_frame.place(relx=0.5, rely=0.1, anchor='n', relwidth=0.9, relheight=0.8)
        
        # 创建标题
        tk.Label(
            content_frame,
            text="添加题目",
            font=("Microsoft YaHei", 24, 'bold'),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(0, 30))
        
        # 创建输入区域
        input_frame = tk.Frame(content_frame, bg=start_color)
        input_frame.pack(pady=20, fill='x')
        
        # 题目输入
        tk.Label(
            input_frame,
            text="题目内容：",
            font=("Microsoft YaHei", 16),
            bg=start_color,
            fg='#333333'
        ).pack()
        
        question_entry = UIComponents.create_styled_entry(input_frame)
        
        # 难度输入
        tk.Label(
            input_frame,
            text="难度 (800-2000)：",
            font=("Microsoft YaHei", 16),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(20, 0))
        
        diff_entry = UIComponents.create_styled_entry(input_frame)
        
        # 创建按钮区域
        button_frame = tk.Frame(content_frame, bg=start_color)
        button_frame.pack(pady=30)
        
        ButtonStyle(button_frame, "添加", lambda: self.add_question(question_entry, diff_entry))
        
        ButtonStyle(button_frame, "返回", self.setup_ui)

    def open_ai_chat_page(self):
        """打开AI问答页面"""
        self.clear_root()
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        start_color = ThemeManager.get_theme_color(self.current_theme)
        content_frame = tk.Frame(self, bg=start_color)
        content_frame.place(relx=0.5, rely=0.1, anchor='n', relwidth=0.9, relheight=0.8)
        
        # 创建标题
        header_frame = tk.Frame(content_frame, bg=start_color)
        header_frame.pack(pady=(0, 30), fill='x')
        
        # 添加标题
        tk.Label(
            header_frame,
            text="AI问答",
            font=("Microsoft YaHei", 24, 'bold'),
            bg=start_color,
            fg='#333333'
        ).pack(pady=(0, 30))
        
        # 创建对话历史显示区域
        chat_frame = tk.Frame(content_frame, bg='#ffffff')
        chat_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.chat_text = tk.Text(
            chat_frame,
            font=("Microsoft YaHei", 12),
            wrap='word',
            relief='flat',
            bg='#ffffff',
            fg='#333333',
            height=20
        )
        self.chat_text.pack(fill='both', expand=True, side='left')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_text.config(yscrollcommand=scrollbar.set)
        
        # 创建输入区域
        input_frame = tk.Frame(content_frame, bg=start_color)
        input_frame.pack(fill='x', pady=20, padx=20)
        
        # 创建输入框和按钮的容器
        input_button_frame = tk.Frame(input_frame, bg=start_color)
        input_button_frame.pack(fill='x')
        
        # 创建输入框
        self.chat_entry = UIComponents.create_styled_entry(
            input_button_frame,
            width=50,
            bind_submit=lambda event: self.send_message()
        )
        self.chat_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        
        # 添加返回按钮到输入框右侧
        ButtonStyle(input_button_frame, "返回", self.setup_ui)
        
        # 创建按钮区域
        button_frame = tk.Frame(content_frame, bg=start_color)
        button_frame.pack(pady=30)
        
        # 添加功能按钮
        ButtonStyle(button_frame, "发送", self.send_message)
        ButtonStyle(button_frame, "清空对话", self.clear_chat)
        ButtonStyle(button_frame, "保存对话", self.save_chat_history)
        
        # 创建返回按钮容器（右下角）
        return_frame = tk.Frame(content_frame, bg=start_color)
        return_frame.pack(fill='x', pady=10)
        return_button_container = tk.Frame(return_frame, bg=start_color)
        return_button_container.pack(side='right', padx=20)
        ButtonStyle(return_button_container, "返回", self.setup_ui)
        
        # 显示历史对话记录
        self.display_chat_history()
    
    def clear_chat(self):
        """清空对话历史"""
        self.chat_history = []
        self.chat_text.delete(1.0, tk.END)
        messagebox.showinfo("提示", "对话历史已清空")
    

    def send_message(self):
        """发送消息到AI并显示回复"""
        user_input = self.chat_entry.get()
        if not user_input.strip():
            return
        
        # 显示用户输入
        self.chat_text.insert(tk.END, "你: " + user_input + "\n", "user")
        self.chat_text.tag_configure("user", foreground="#333333")
        
        # 添加到历史记录
        self.chat_history.append({"role": "user", "content": user_input})
        
        # 显示加载状态
        loading_id = self.show_loading_indicator()
        self.update()  # 强制更新UI
        
        try:
            # 使用API模块中的chat_with_ai函数
            from API import chat_with_ai
            
            # 获取历史对话记录（如果需要）
            # 注意：这里只传递最后一条用户消息，不传递历史记录
            # 如果需要保持对话上下文，可以传递self.chat_history
            
            # 显示AI回复的标题
            self.chat_text.insert(tk.END, "AI: ", "ai")
            self.chat_text.tag_configure("ai", foreground="#0066cc")
            
            # 调用API获取AI回复
            ai_response, reasoning = chat_with_ai(user_input)
            
            # 显示AI思考过程
            if reasoning:
                self.chat_text.insert(tk.END, "思考过程:\n", "reasoning_title")
                self.chat_text.tag_configure("reasoning_title", foreground="#006600", font=("Microsoft YaHei", 10, "bold"))
                self.chat_text.insert(tk.END, reasoning + "\n\n", "reasoning")
                self.chat_text.tag_configure("reasoning", foreground="#006600", font=("Microsoft YaHei", 10))
            
            # 显示AI回复
            self.chat_text.insert(tk.END, ai_response, "ai")
            self.chat_text.see(tk.END)
            self.update()
            
            self.chat_text.insert(tk.END, "\n\n", "ai")
            
            # 移除加载指示器
            self.hide_loading_indicator(loading_id)
            
            # 添加到历史记录
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            # 移除加载指示器
            self.hide_loading_indicator(loading_id)
            
            # 显示详细错误信息
            error_message = f"错误: {str(e)}"
            self.chat_text.insert(tk.END, error_message + "\n\n", "error")
            self.chat_text.tag_configure("error", foreground="#ff0000")
            
            # 记录错误到历史
            self.chat_history.append({"role": "system", "content": error_message})
        
        # 清空输入框并滚动到底部
        self.chat_entry.delete(0, tk.END)
        self.chat_text.see(tk.END)
    
    def show_loading_indicator(self):
        """显示加载指示器"""
        loading_id = "loading_" + str(time.time())
        self.chat_text.insert(tk.END, "AI思考中...", loading_id)
        self.chat_text.tag_configure(loading_id, foreground="#999999")
        self.chat_text.see(tk.END)
        return loading_id
    
    def hide_loading_indicator(self, loading_id):
        """隐藏加载指示器"""
        try:
            # 查找加载指示器的位置
            start_index = self.chat_text.search("AI思考中...", "1.0", tk.END)
            if start_index:
                # 计算结束位置
                end_index = f"{start_index}+{len('AI思考中...')}c"
                # 删除加载指示器
                self.chat_text.delete(start_index, end_index)
        except Exception:
            pass  # 忽略可能的错误

    def end(self):
        """结束答题"""
        messagebox.showinfo("结束", f"提交次数：{self.hw.done}\n最终学力:{self.hw.student['rating']:.2f}")
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
