#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor

import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class ImageViewer(QWidget):
    """图像查看器控件，用于显示图像和相关信息"""
    
    def __init__(self, title="图像查看器"):
        super().__init__()
        
        # 设置控件属性
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # 创建滚动区域用于图像显示
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 图像标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        self.image_label.setMinimumSize(280, 280)
        self.image_label.setText("无图像")
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # 信息标签
        self.info_label = QLabel("尺寸: -- x -- | 格式: --")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # 初始化图像数据
        self.image = None
        self.pixmap = None
    
    def set_image(self, image):
        """设置图像
        
        Args:
            image: 可以是QImage、QPixmap、numpy数组或文件路径
        """
        if image is None:
            self.clear()
            return
        
        # 根据输入类型处理图像
        if isinstance(image, QImage):
            self.image = image
            self.pixmap = QPixmap.fromImage(image)
        elif isinstance(image, QPixmap):
            self.pixmap = image
            self.image = image.toImage()
        elif isinstance(image, np.ndarray):
            # 将numpy数组转换为QImage
            height, width = image.shape[:2]
            if len(image.shape) == 2:  # 灰度图
                qimage = QImage(image.data, width, height, width, QImage.Format_Grayscale8)
            else:  # 彩色图
                qimage = QImage(image.data, width, height, width * 3, QImage.Format_RGB888)
            self.image = qimage
            self.pixmap = QPixmap.fromImage(qimage)
        elif isinstance(image, str):  # 文件路径
            self.pixmap = QPixmap(image)
            self.image = self.pixmap.toImage()
        
        # 更新图像显示
        self.image_label.setPixmap(self.pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        
        # 更新信息标签
        width = self.image.width()
        height = self.image.height()
        self.info_label.setText(f"尺寸: {width} x {height} | 格式: {self._get_format_name()}")
    
    def clear(self):
        """清除图像"""
        self.image_label.clear()
        self.image_label.setText("无图像")
        self.info_label.setText("尺寸: -- x -- | 格式: --")
        self.image = None
        self.pixmap = None
    
    def _get_format_name(self):
        """获取图像格式名称"""
        if self.image is None:
            return "--"
        
        format_map = {
            QImage.Format_RGB32: "RGB32",
            QImage.Format_ARGB32: "ARGB32",
            QImage.Format_RGB888: "RGB888",
            QImage.Format_Grayscale8: "灰度"
        }
        
        return format_map.get(self.image.format(), "未知")
    
    def resizeEvent(self, event):
        """重写大小调整事件，确保图像正确缩放"""
        if self.pixmap and not self.pixmap.isNull():
            self.image_label.setPixmap(self.pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        super().resizeEvent(event)


class BitPlaneViewer(QWidget):
    """位平面可视化控件，用于显示图像的位平面"""
    
    def __init__(self):
        super().__init__()
        
        # 设置控件属性
        self.setMinimumSize(400, 400)
        
        # 创建布局
        layout = QGridLayout(self)
        
        # 创建8个位平面图像查看器（0-7位）
        self.bit_viewers = []
        for i in range(8):
            viewer = ImageViewer(f"位平面 {i}")
            row, col = i // 4, i % 4
            layout.addWidget(viewer, row, col)
            self.bit_viewers.append(viewer)
        
        # 初始化图像数据
        self.image = None
    
    def set_image(self, image):
        """设置图像并分解位平面
        
        Args:
            image: 可以是QImage、QPixmap、numpy数组或文件路径
        """
        # 首先将图像转换为numpy数组
        if isinstance(image, QImage):
            self.image = self._qimage_to_numpy(image)
        elif isinstance(image, QPixmap):
            self.image = self._qimage_to_numpy(image.toImage())
        elif isinstance(image, np.ndarray):
            self.image = image
        elif isinstance(image, str):  # 文件路径
            pixmap = QPixmap(image)
            self.image = self._qimage_to_numpy(pixmap.toImage())
        else:
            return
        
        # 如果是彩色图像，转换为灰度图
        if len(self.image.shape) == 3:
            gray = np.dot(self.image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            gray = self.image
        
        # 分解位平面并显示
        for bit in range(8):
            # 提取第bit位平面
            bit_plane = ((gray >> bit) & 1) * 255
            self.bit_viewers[bit].set_image(bit_plane)
    
    def clear(self):
        """清除所有位平面"""
        for viewer in self.bit_viewers:
            viewer.clear()
        self.image = None
    
    def _qimage_to_numpy(self, qimage):
        """将QImage转换为numpy数组"""
        width = qimage.width()
        height = qimage.height()
        
        # 转换为合适的格式
        if qimage.format() != QImage.Format_RGB32:
            qimage = qimage.convertToFormat(QImage.Format_RGB32)
        
        # 获取图像数据
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        return arr[..., :3]  # 返回RGB部分，丢弃Alpha通道


class MetricsChart(QWidget):
    """指标图表控件，用于显示评估指标的图表"""
    
    def __init__(self, x_label="X轴", y_label="Y轴", title="图表"):
        super().__init__()
        
        # 设置控件属性
        self.setMinimumSize(400, 300)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # 添加子图
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(title)
        self.ax.grid(True)
        
        # 初始化数据
        self.x_data = []
        self.y_data = []
        self.line = None
    
    def update_data(self, x_data, y_data):
        """更新图表数据
        
        Args:
            x_data: X轴数据列表
            y_data: Y轴数据列表
        """
        self.x_data = x_data
        self.y_data = y_data
        
        # 清除当前图表
        self.ax.clear()
        
        # 绘制新数据
        self.line, = self.ax.plot(self.x_data, self.y_data, 'b-o')
        
        # 设置轴标签和网格
        self.ax.set_xlabel(self.ax.get_xlabel())
        self.ax.set_ylabel(self.ax.get_ylabel())
        self.ax.set_title(self.ax.get_title())
        self.ax.grid(True)
        
        # 刷新画布
        self.canvas.draw()
    
    def add_data_point(self, x, y):
        """添加单个数据点（add_point方法的别名）
        
        Args:
            x: X坐标
            y: Y坐标
        """
        return self.add_point(x, y)
        self.x_data.append(x)
        self.y_data.append(y)
        self.update_data(self.x_data, self.y_data)
    
    def clear(self):
        """清除图表数据"""
        self.x_data = []
        self.y_data = []
        self.ax.clear()
        self.ax.set_xlabel(self.ax.get_xlabel())
        self.ax.set_ylabel(self.ax.get_ylabel())
        self.ax.set_title(self.ax.get_title())
        self.ax.grid(True)
        self.canvas.draw()
        
    def has_data(self):
        """检查图表是否包含数据
        
        返回:
            bool: 如果图表包含数据返回True，否则返回False
        """
        return len(self.x_data) > 0 and len(self.y_data) > 0

    def export_to_csv(self, file_path):
        """导出数据到CSV文件"""
        import csv
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['X轴数据', 'Y轴数据'])
            for x, y in zip(self.x_data, self.y_data):
                writer.writerow([x, y])

    def export_to_image(self, file_path):
            """导出图表为图像文件"""
            self.figure.savefig(file_path)
