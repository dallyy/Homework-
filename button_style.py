# -*- coding: utf-8 -*-

import tkinter as tk
import logging

# 设置日志记录器
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ButtonStyle:
    def __init__(self, master, text, command=None):
        self.master = master
        self.text = text
        self.command = command
        self.label = tk.Label(master)
        self.configure_label()

    def configure_label(self):
        style = {
            'text': self.text,
            'width': 20,
            'height': 1,
            'borderwidth': 0,  # 设置为0以实现圆角效果
            'relief': 'flat',
            'background': '#4a90e2',  # 更现代的蓝色
            'foreground': '#FFFFFF',
            'activebackground': '#357abd',  # 深蓝色用于悬停
            'font': ('Microsoft YaHei', 15, 'bold'),
            'cursor': 'hand2',
            'padx': 15,  # 内部水平填充
            'pady': 8,   # 内部垂直填充
        }
        self.label.config(**style)
        
        # 创建圆角效果的画布
        canvas = tk.Canvas(self.master, width=200, height=40, bg=self.master['bg'], highlightthickness=0)
        canvas.pack(side='left', anchor='center', expand=False, pady=5, padx=10)
        
        # 绘制圆角矩形
        radius = 10  # 圆角半径
        points = [
            radius, 0,  # 左上角起点
            200-radius, 0,  # 右上横线
            200, 0,
            200, radius,  # 右上圆角
            200, 40-radius,  # 右边线
            200, 40,
            200-radius, 40,  # 右下圆角
            radius, 40,  # 下横线
            0, 40,
            0, 40-radius,  # 左下圆角
            0, radius,  # 左边线
            0, 0,
            radius, 0  # 左上圆角
        ]
        
        # 创建圆角矩形
        canvas.create_polygon(points, fill=style['background'], smooth=True)
        
        # 在圆角矩形上添加文字
        canvas.create_text(100, 20, text=self.text, fill=style['foreground'], 
                          font=style['font'])
        
        # 保存canvas引用以便后续更新
        self.canvas = canvas
        
        # 绑定事件到canvas而不是label
        canvas.bind('<Enter>', self.enter_bind, add='+')
        canvas.bind('<Leave>', self.leave_bind, add='+')
        canvas.bind('<Button-1>', self.button_1_bind, add='+')
        canvas.bind('<Double-Button-1>', self.double_button_1_bind, add='+')
        canvas.bind('<FocusIn>', self.focus_in_bind, add='+')
        canvas.bind('<FocusOut>', self.focus_out_bind, add='+')

    def enter_bind(self, event):
        """鼠标进入组件时触发."""
        self.canvas.delete('all')  # 清除原有内容
        
        # 重绘圆角矩形（悬停颜色）
        radius = 10
        points = [
            radius, 0,
            200-radius, 0,
            200, 0,
            200, radius,
            200, 40-radius,
            200, 40,
            200-radius, 40,
            radius, 40,
            0, 40,
            0, 40-radius,
            0, radius,
            0, 0,
            radius, 0
        ]
        self.canvas.create_polygon(points, fill='#357abd', smooth=True)
        
        # 重绘文字
        self.canvas.create_text(100, 20, text=self.text, fill='#FFFFFF', 
                               font=('Microsoft YaHei', 15, 'bold'))

    def leave_bind(self, event):
        """鼠标离开组件时触发."""
        self.canvas.delete('all')  # 清除原有内容
        
        # 重绘圆角矩形（正常颜色）
        radius = 10
        points = [
            radius, 0,
            200-radius, 0,
            200, 0,
            200, radius,
            200, 40-radius,
            200, 40,
            200-radius, 40,
            radius, 40,
            0, 40,
            0, 40-radius,
            0, radius,
            0, 0,
            radius, 0
        ]
        self.canvas.create_polygon(points, fill='#4a90e2', smooth=True)
        
        # 重绘文字
        self.canvas.create_text(100, 20, text=self.text, fill='#FFFFFF', 
                               font=('Microsoft YaHei', 15, 'bold'))

    def button_1_bind(self, event):
        """鼠标按下时触发."""
        try:
            logger.debug(f"Button clicked - Text: {self.text}, Widget: {event.widget}")
            
            # 清除原有内容
            self.canvas.delete('all')
            
            # 重绘圆角矩形（按下颜色）
            radius = 10
            points = [
                radius, 0,
                200-radius, 0,
                200, 0,
                200, radius,
                200, 40-radius,
                200, 40,
                200-radius, 40,
                radius, 40,
                0, 40,
                0, 40-radius,
                0, radius,
                0, 0,
                radius, 0
            ]
            self.canvas.create_polygon(points, fill='#2e5c8a', smooth=True)
            
            # 重绘文字
            self.canvas.create_text(100, 20, text=self.text, fill='#FFFFFF', 
                                   font=('Microsoft YaHei', 15, 'bold'))
            
            if self.command:
                logger.debug(f"Executing command for button: {self.text}")
                self.command()
                
        except Exception as e:
            logger.error(f"Error in button click handler - Button: {self.text}, Error: {str(e)}")
            raise

    def double_button_1_bind(self, event):
        """鼠标双击时的事件."""
        pass

    def focus_in_bind(self, event):
        """组件获得焦点时触发."""
        self.canvas.delete('all')  # 清除原有内容
        
        # 重绘圆角矩形（焦点颜色）
        radius = 10
        points = [
            radius, 0,
            200-radius, 0,
            200, 0,
            200, radius,
            200, 40-radius,
            200, 40,
            200-radius, 40,
            radius, 40,
            0, 40,
            0, 40-radius,
            0, radius,
            0, 0,
            radius, 0
        ]
        self.canvas.create_polygon(points, fill='#357abd', smooth=True)
        
        # 重绘文字
        self.canvas.create_text(100, 20, text=self.text, fill='#FFFFFF', 
                               font=('Microsoft YaHei', 15, 'bold'))

    def focus_out_bind(self, event):
        """组件失去焦点时触发."""
        self.canvas.delete('all')  # 清除原有内容
        
        # 重绘圆角矩形（正常颜色）
        radius = 10
        points = [
            radius, 0,
            200-radius, 0,
            200, 0,
            200, radius,
            200, 40-radius,
            200, 40,
            200-radius, 40,
            radius, 40,
            0, 40,
            0, 40-radius,
            0, radius,
            0, 0,
            radius, 0
        ]
        self.canvas.create_polygon(points, fill='#4a90e2', smooth=True)
        
        # 重绘文字
        self.canvas.create_text(100, 20, text=self.text, fill='#FFFFFF', 
                               font=('Microsoft YaHei', 15, 'bold'))