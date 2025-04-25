# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFrame, QMessageBox, QListWidget, QLabel)
from PyQt5.QtCore import Qt, QTimer
import time
from homework_logic import Homework, Question
from ui_components import UIComponents, ThemeManager

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hw = Homework()
        self.current_theme = '蓝色主题'
        self.ui = UIComponents()
        self.chat_history = []
        self.filter_window = None
        self.theme_window = None
        self.add_question_window = None
        self.ai_chat_window = None
        self.setup_ui()
        
        # 主窗口关闭时清理所有资源
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.destroyed.connect(self.cleanup_resources)
        
    def cleanup_resources(self):
        # 清理所有窗口资源
        if self.filter_window:
            self.filter_window.close()
            self.filter_window.deleteLater()
        if self.theme_window:
            self.theme_window.close()
            self.theme_window.deleteLater()
        if self.add_question_window:
            self.add_question_window.close()
            self.add_question_window.deleteLater()
        if self.ai_chat_window:
            self.ai_chat_window.close()
            self.ai_chat_window.deleteLater()
        
        # 清理其他资源
        self.chat_history.clear()
        self.hw = None
        self.ui = None

    def setup_ui(self):
        self.setWindowTitle("作业推荐")
        self.resize(800, 900)  # 设置初始大小但允许调整
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 设置主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)  # 减小外边距
        main_layout.setSpacing(25)  # 增加组件间距
        
        # 设置背景
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        # 创建内容框架
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.75);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
        """)
        main_layout.addWidget(content_frame, stretch=1)
        
        # 设置内容布局
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)  # 设置内容边距
        content_layout.setSpacing(25)  # 增加组件间距
        
        # 添加组件
        self.setup_rating_label(content_layout)
        self.setup_question_label(content_layout)
        
        # 创建水平布局容器来居中输入框
        entry_container = QWidget()
        entry_layout = QHBoxLayout(entry_container)
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.addStretch(1)
        self.entry = self.ui.create_styled_entry(
            self,
            width=30,
            bind_submit=self.submit
        )
        entry_layout.addWidget(self.entry)
        entry_layout.addStretch(1)
        content_layout.addWidget(entry_container)
        
        self.setup_buttons(content_layout)
        
        self.start_quiz()

    def setup_rating_label(self, layout):
        self.rating_label = self.ui.create_label(
            self,
            f"学力：{self.hw.student['rating']:.2f}",
            18,
            ThemeManager.get_theme_color(self.current_theme),
            anchor="nw"
        )
        layout.addWidget(self.rating_label)

    def setup_question_label(self, layout):
        if self.hw.cur_q:
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷')
        else:
            self.hw.cur_q = self.hw.recommend(correct=True)
            question_text = self.hw.cur_q.q.replace('*', '×').replace('/', '÷') if self.hw.cur_q else "没有更多题目！"
        
        self.q_label = self.ui.create_label(
            self,
            question_text,
            24,  # 将字体大小从16px调整为24px
            ThemeManager.get_theme_color(self.current_theme)
        )
        layout.addWidget(self.q_label)

    def setup_answer_entry(self, layout):
        self.entry = self.ui.create_styled_entry(
            self,
            width=30,
            bind_submit=self.submit
        )
        layout.addWidget(self.entry)

    def setup_buttons(self, layout):
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.get_theme_color(self.current_theme)};
                border-radius: 10px;
                padding: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)  # 设置按钮间距
        
        buttons = [
            ("提交", self.submit),
            ("难度筛选", self.open_filter_page),
            ("增加题目", self.open_add_question_page),
            ("主题设置", self.open_theme_page),
            ("AI问答", self.open_ai_chat_page),
            ("AI布置应用题", self.open_ai_application_question_page)
        ]
        
        for text, command in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(74, 144, 226, 0.85);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-family: 'Microsoft YaHei';
                    font-size: 14px;
                    min-width: 100px;
                    backdrop-filter: blur(5px);
                }
                QPushButton:hover {
                    background-color: rgba(53, 122, 189, 0.9);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                QPushButton:pressed {
                    background-color: rgba(42, 95, 158, 0.95);
                    border: 1px solid rgba(255, 255, 255, 0.4);
                }
            """)
            btn.clicked.connect(command)
            button_layout.addWidget(btn)
        
        layout.addWidget(button_frame)

    def submit(self):
        if not self.hw.cur_q:
            QMessageBox.critical(self, "错误", "没有当前题目！")
            return

        elapsed = time.time() - self.start_time
        user_answer = self.entry.text().replace('×', '*').replace('÷', '/')

        try:
            correct = self.hw.evaluate_answer(self.hw.cur_q, user_answer)
            self.hw.update_rating(self.hw.cur_q, correct, elapsed)
            QMessageBox.information(self, "结果", "正确" if correct else "错误")
        except ValueError as e:
            QMessageBox.critical(self, "错误", f"无效的答案格式！\n{e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"未知错误：{e}")
            return

        self.hw.cur_q = self.hw.recommend(correct)
        self.refresh_ui()
        self.start_time = time.time()

    def refresh_ui(self):
        self.rating_label.setText(f"学力：{self.hw.student['rating']:.2f}")
        self.q_label.setText(self.hw.cur_q.q.replace('*', '×').replace('/', '÷') if self.hw.cur_q else "没有更多题目！")
        self.entry.clear()
        
    def cleanup_filter_window(self, event):
        # 清理筛选窗口资源
        if self.filter_window:
            self.filter_window = None
        event.accept()

    def start_quiz(self):
        self.start_time = time.time()

    def open_filter_page(self):
        # 如果窗口已存在，先清理旧窗口
        if self.filter_window:
            self.filter_window.close()
            self.filter_window.deleteLater()
            
        # 创建新窗口
        self.filter_window = QMainWindow(self)
        self.filter_window.setWindowTitle("题目难度筛选")
        self.filter_window.resize(800, 900)  # 设置初始大小但允许调整
        self.filter_window.setAttribute(Qt.WA_DeleteOnClose)
        
        # 窗口关闭时清理资源
        self.filter_window.closeEvent = lambda event: self.cleanup_filter_window(event)
        
        # 设置中央部件和布局
        central_widget = QWidget()
        self.filter_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 设置背景
        ThemeManager.create_gradient_background(self.filter_window, self.current_theme)
        
        # 创建输入区域
        min_label = self.ui.create_label(self.filter_window, "最小难度：", 16, ThemeManager.get_theme_color(self.current_theme))
        layout.addWidget(min_label)
        
        # 创建水平布局容器来居中最小难度输入框
        min_entry_container = QWidget()
        min_entry_layout = QHBoxLayout(min_entry_container)
        min_entry_layout.setContentsMargins(0, 0, 0, 0)
        min_entry_layout.addStretch(1)
        self.min_entry = self.ui.create_styled_entry(self.filter_window)
        self.min_entry.textChanged.connect(self.filter_by_diff)  # 添加实时筛选
        min_entry_layout.addWidget(self.min_entry)
        min_entry_layout.addStretch(1)
        layout.addWidget(min_entry_container)
        
        max_label = self.ui.create_label(self.filter_window, "最大难度：", 16, ThemeManager.get_theme_color(self.current_theme))
        layout.addWidget(max_label)
        
        # 创建水平布局容器来居中最大难度输入框
        max_entry_container = QWidget()
        max_entry_layout = QHBoxLayout(max_entry_container)
        max_entry_layout.setContentsMargins(0, 0, 0, 0)
        max_entry_layout.addStretch(1)
        self.max_entry = self.ui.create_styled_entry(self.filter_window)
        self.max_entry.textChanged.connect(self.filter_by_diff)  # 添加实时筛选
        max_entry_layout.addWidget(self.max_entry)
        max_entry_layout.addStretch(1)
        layout.addWidget(max_entry_container)
        
        # 创建结果列表并添加点击事件
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.on_question_selected)
        self.result_list.setStyleSheet("""
            QListWidget {
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                margin: 10px 0;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.result_list)
        
        # 创建按钮
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        back_btn.clicked.connect(self.filter_window.close)
        button_layout.addWidget(back_btn)
        
        layout.addWidget(button_frame)
        
        # 初始显示所有题目
        self.filter_by_diff()
        
        self.filter_window.show()
        
    def on_question_selected(self, item):
        # 从列表项文本中提取题目ID
        question_id = int(item.text().split('.')[0])
        
        # 在题库中找到对应的题目
        selected_question = None
        for question in self.hw.q_bank:
            if question.id == question_id:
                selected_question = question
                break
        
        if selected_question:
            # 更新当前题目
            self.hw.cur_q = selected_question
            self.hw.xuanti[selected_question.id]=True
            # 关闭筛选窗口
            self.filter_window.close()
            # 刷新主界面
            self.refresh_ui()
            # 重置计时器
            self.start_time = time.time()

    def filter_by_diff(self):
        try:
            # 获取输入值，如果为空则设为None
            diff_min = int(self.min_entry.text()) if self.min_entry.text().strip() else None
            diff_max = int(self.max_entry.text()) if self.max_entry.text().strip() else None

            # 验证输入范围
            if diff_min is not None and diff_min < 800:
                self.min_entry.setStyleSheet("border-color: red;")
                return
            else:
                self.min_entry.setStyleSheet("")

            if diff_max is not None and diff_max > 2000:
                self.max_entry.setStyleSheet("border-color: red;")
                return
            else:
                self.max_entry.setStyleSheet("")

            if diff_min is not None and diff_max is not None and diff_min > diff_max:
                self.min_entry.setStyleSheet("border-color: red;")
                self.max_entry.setStyleSheet("border-color: red;")
                return

            # 清空列表并添加新的筛选结果
            self.result_list.clear()
            filtered_questions = self.hw.search_by_diff(diff_min, diff_max)

            for q in filtered_questions:
                display_text = f"{q.id}. 难度: {q.diff} - {q.q.replace('*', '×').replace('/', '÷')}"
                self.result_list.addItem(display_text)

        except ValueError:
            # 输入非数字时不进行处理，保持当前显示
            pass

    def open_add_question_page(self):
        # 创建新窗口
        self.add_window = QMainWindow(self)
        self.add_window.setWindowTitle("添加题目")
        self.add_window.setFixedSize(800, 900)
        
        # 设置中央部件和布局
        central_widget = QWidget()
        self.add_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 设置背景
        ThemeManager.create_gradient_background(self.add_window, self.current_theme)
        
        # 创建输入区域
        question_label = self.ui.create_label(self.add_window, "题目内容：", 16, ThemeManager.get_theme_color(self.current_theme))
        layout.addWidget(question_label)
        
        # 创建水平布局容器来居中题目输入框
        question_container = QWidget()
        question_layout = QHBoxLayout(question_container)
        question_layout.setContentsMargins(0, 0, 0, 0)
        question_layout.addStretch(1)
        self.question_entry = self.ui.create_styled_entry(self.add_window, width=40, bind_submit=lambda: self.add_question())
        question_layout.addWidget(self.question_entry)
        question_layout.addStretch(1)
        layout.addWidget(question_container)
        
        diff_label = self.ui.create_label(self.add_window, "难度 (800-2000)：", 16, ThemeManager.get_theme_color(self.current_theme))
        layout.addWidget(diff_label)
        
        # 创建水平布局容器来居中难度输入框
        diff_container = QWidget()
        diff_layout = QHBoxLayout(diff_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_layout.addStretch(1)
        self.diff_entry = self.ui.create_styled_entry(self.add_window)
        diff_layout.addWidget(self.diff_entry)
        diff_layout.addStretch(1)
        layout.addWidget(diff_container)
        
        # 创建按钮
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        add_btn = QPushButton("添加")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        add_btn.clicked.connect(lambda: self.add_question())
        button_layout.addWidget(add_btn)
        
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        back_btn.clicked.connect(self.add_window.close)
        button_layout.addWidget(back_btn)
        
        layout.addWidget(button_frame)
        
        self.add_window.show()

    def add_question(self):
        question_text = self.question_entry.text().replace('×', '*').replace('÷', '/')
        try:
            difficulty = int(self.diff_entry.text())
            if difficulty < 800 or difficulty > 2000:
                raise ValueError("难度必须在800到2000之间。")
        except ValueError as e:
            QMessageBox.critical(self, "错误", f"无效的难度值！\n{e}")
            return

        try:
            if not question_text.strip():
                raise ValueError("题目不能为空！")
            
            self.hw.add_question(question_text, difficulty)
            QMessageBox.information(self, "成功", "题目添加成功！")
            self.add_window.close()
            self.refresh_ui()
        except ValueError as e:
            QMessageBox.critical(self, "错误", str(e))

    def open_theme_page(self):
        # 创建新窗口
        self.theme_window = QMainWindow(self)
        self.theme_window.setWindowTitle("主题设置")
        self.theme_window.setFixedSize(800, 900)
        
        # 设置中央部件和布局
        central_widget = QWidget()
        self.theme_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 设置背景
        ThemeManager.create_gradient_background(self.theme_window, self.current_theme)
        
        # 创建标题标签
        title_label = QLabel("选择主题")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 24px;
                margin: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建主题按钮
        theme = ThemeManager.THEMES[self.current_theme]
        button_style = f"""
            QPushButton {{
                background-color: {theme['button']};
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                margin: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """
        
        for theme_name in ThemeManager.THEMES.keys():
            theme_btn = QPushButton(theme_name)
            theme_btn.setStyleSheet(button_style)
            theme_btn.clicked.connect(lambda checked, name=theme_name: self.change_theme(name))
            layout.addWidget(theme_btn)
        
        # 返回按钮
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet(button_style)
        back_btn.clicked.connect(self.theme_window.close)
        layout.addWidget(back_btn)
        
        self.theme_window.show()

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        theme = ThemeManager.THEMES[theme_name]
        
        # 更新背景
        ThemeManager.create_gradient_background(self, self.current_theme)
        
        # 更新按钮样式
        button_style = f"""
            QPushButton {{
                background-color: {theme['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """
        
        # 更新所有按钮的样式
        for child in self.findChildren(QPushButton):
            child.setStyleSheet(button_style)
        
        self.theme_window.close()
        self.refresh_ui()

    def open_ai_chat_page(self):
        # 创建新窗口
        self.chat_window = QMainWindow(self)
        self.chat_window.setWindowTitle("AI问答")
        self.chat_window.resize(800, 900)
        # 设置中央部件和布局
        central_widget = QWidget()
        self.chat_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # 设置背景
        ThemeManager.create_gradient_background(self.chat_window, self.current_theme)
        # --- 新增：分析过程和解答过程显示区 ---
        from PyQt5.QtWidgets import QTextEdit
        self.reasoning_text = QTextEdit()
        self.reasoning_text.setReadOnly(True)
        self.reasoning_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei';
                font-size: 22px;
                color: #1565c0;
                background-color: #e3f2fd;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 10px;
            }
        """)
        self.reasoning_text.setPlaceholderText("AI分析过程将在此显示...")
        layout.addWidget(self.reasoning_text)
        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        self.answer_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei';
                font-size: 24px;
                color: #1b5e20;
                background-color: #e8f5e9;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 10px;
            }
        """)
        self.answer_text.setPlaceholderText("AI解答过程将在此显示...")
        layout.addWidget(self.answer_text)
        # 创建输入区域
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        self.chat_entry = self.ui.create_styled_entry(self.chat_window, width=50, bind_submit=self.send_message)
        input_layout.addWidget(self.chat_entry)
        send_btn = QPushButton("发送")
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        layout.addWidget(input_frame)
        # 功能按钮
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        clear_btn = QPushButton("清空对话")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        clear_btn.clicked.connect(self.clear_chat)
        button_layout.addWidget(clear_btn)
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.THEMES[self.current_theme]['button_pressed']};
            }}
        """)
        back_btn.clicked.connect(self.chat_window.close)
        button_layout.addWidget(back_btn)
        layout.addWidget(button_frame)
        self.chat_window.show()

    def send_message(self):
        user_input = self.chat_entry.text()
        if not user_input.strip():
            return
        self.chat_entry.clear()
        self.reasoning_text.setText("AI正在思考分析...")
        self.answer_text.setText("")
        QTimer.singleShot(1000, lambda: self.show_ai_response(user_input))

    def clear_chat(self):
        self.reasoning_text.clear()
        self.answer_text.clear()

    def show_ai_response(self, user_input):
        try:
            from API import chat_with_ai
            ai_response, reasoning = chat_with_ai(user_input, timeout=30)
            # 分段显示，保持可读性
            def format_paragraphs(text):
                # 先将####转为换行，再按段落分隔
                text = text.replace('####', '\n')
                return '\n\n'.join([p.strip() for p in text.split('\n') if p.strip()])
            # 分别填充分析和解答内容
            self.reasoning_text.setText(format_paragraphs(reasoning))
            self.answer_text.setText(format_paragraphs(ai_response))
        except Exception as e:
            self.reasoning_text.setText("")
            self.answer_text.setText(f"AI回复异常：{str(e)}。请稍后重试。")

    def open_ai_application_question_page(self):
        from ai_application_question import AIApplicationQuestion
        from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QSizePolicy
        self.ai_app_window = QMainWindow(self)
        self.ai_app_window.setWindowTitle("AI布置应用题")
        self.ai_app_window.resize(1024, 768)  # 设置初始大小
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许部件自由扩展
        self.ai_app_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)  # 设置边距
        layout.setSpacing(20)  # 设置组件间距
        ThemeManager.create_gradient_background(self.ai_app_window, self.current_theme)
        self.ai_app = AIApplicationQuestion()
        self.ai_question, self.ai_answer = self.ai_app.generate_question_and_answer()
        # 创建一个容器来包装题目标签
        question_container = QWidget()
        question_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        question_layout = QVBoxLayout(question_container)
        self.ai_question_label = QLabel(f"题目：{self.ai_question}")
        self.ai_question_label.setWordWrap(True)  # 允许文字换行
        self.ai_question_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #1565c0;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
            }
        """)
        question_layout.addWidget(self.ai_question_label)
        layout.addWidget(question_container)
        # 创建答案输入区域
        answer_container = QWidget()
        answer_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        answer_layout = QVBoxLayout(answer_container)
        self.ai_answer_entry = QLineEdit()
        self.ai_answer_entry.setPlaceholderText("请输入你的答案")
        self.ai_answer_entry.setStyleSheet("""
            QLineEdit {
                font-size: 22px;
                padding: 15px;
                margin: 10px;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QLineEdit:focus {
                border-color: #2196f3;
                background-color: white;
            }
        """)
        answer_layout.addWidget(self.ai_answer_entry)
        layout.addWidget(answer_container)
        # 创建按钮容器
        button_container = QWidget()
        button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button_layout = QHBoxLayout(button_container)
        submit_btn = QPushButton("提交答案")
        submit_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #4a90e2;
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5f9e;
            }
        """)
        submit_btn.clicked.connect(self.check_ai_application_answer)
        button_layout.addWidget(submit_btn)
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #888;
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """)
        back_btn.clicked.connect(self.ai_app_window.close)
        button_layout.addWidget(back_btn)
        layout.addWidget(button_container)
        # 创建结果标签容器
        result_container = QWidget()
        result_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        result_layout = QVBoxLayout(result_container)
        self.ai_result_label = QLabel("")
        self.ai_result_label.setWordWrap(True)  # 允许文字换行
        self.ai_result_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #1b5e20;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
            }
        """)
        result_layout.addWidget(self.ai_result_label)
        layout.addWidget(result_container)
        self.ai_app_window.show()

    def check_ai_application_answer(self):
        user_ans = self.ai_answer_entry.text().strip()
        if not user_ans:
            QMessageBox.warning(self, "提示", "请输入答案！")
            return
        self.ai_result_label.setText(f"标准答案：{self.ai_answer}")
