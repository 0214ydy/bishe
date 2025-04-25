#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSlider, QLineEdit, QFileDialog,
    QGroupBox, QTabWidget, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QSplitter, QScrollArea, QStatusBar, QToolBar,
    QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage, QAction

from ui.widgets import ImageViewer, BitPlaneViewer, MetricsChart

import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    """主窗口类"""
    
    #设置中文字体   
    plt.rcParams['font.sans-serif'] = ['SimHei']
    #解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self):
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("图像隐写与抗攻击性研究")
        self.resize(1200, 800)
        
        # 初始化UI组件
        self._init_ui()
        
        # 初始化菜单栏和工具栏
        self._init_menu_bar()
        self._init_tool_bar()
        
        # 初始化状态栏
        self._init_status_bar()
        
        # 连接信号和槽
        self._connect_signals_slots()
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. 文件操作区
        file_group = self._create_file_operation_group()
        left_layout.addWidget(file_group)
        
        # 2. 隐写控制面板
        stego_group = self._create_steganography_control_group()
        left_layout.addWidget(stego_group)
        
        # 3. 攻击选择区
        attack_group = self._create_attack_selection_group()
        left_layout.addWidget(attack_group)
        
        # 4. 评估报告区
        metrics_group = self._create_metrics_group()
        left_layout.addWidget(metrics_group)
        
        # 添加弹性空间
        left_layout.addStretch(1)
        
        # 创建右侧可视化区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # 5. 图像可视化区
        visual_tabs = self._create_visualization_tabs()
        right_layout.addWidget(visual_tabs)
        
        # 创建分割器，使左右面板可调整大小
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])  # 设置初始大小比例
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
    
    def _create_file_operation_group(self):
        """创建文件操作区"""
        group = QGroupBox("文件操作")
        layout = QGridLayout(group)
        
        # 载体图像选择
        self.btn_load_cover = QPushButton("导入载体图像")
        self.lbl_cover_path = QLabel("未选择文件")
        self.lbl_cover_path.setWordWrap(True)
        
        # 保存含密图像
        self.btn_save_stego = QPushButton("保存含密图像")
        self.btn_save_stego.setEnabled(False)
        
        # 导出实验数据
        self.btn_export_data = QPushButton("导出实验数据")
        self.cmb_export_format = QComboBox()
        self.cmb_export_format.addItems(["CSV", "PNG"])
        self.btn_export_data.setEnabled(False)
        
        # 添加到布局
        layout.addWidget(QLabel("载体图像:"), 0, 0)
        layout.addWidget(self.btn_load_cover, 0, 1)
        layout.addWidget(self.lbl_cover_path, 1, 0, 1, 2)
        
        layout.addWidget(QLabel("含密图像:"), 2, 0)
        layout.addWidget(self.btn_save_stego, 2, 1)
        
        layout.addWidget(QLabel("导出格式:"), 3, 0)
        layout.addWidget(self.cmb_export_format, 3, 1)
        layout.addWidget(self.btn_export_data, 4, 0, 1, 2)
        
        return group
    
    def _create_steganography_control_group(self):
        """创建隐写控制面板"""
        group = QGroupBox("隐写控制")
        layout = QGridLayout(group)
        
        # 秘密信息输入
        self.txt_secret = QTextEdit()
        self.txt_secret.setPlaceholderText("在此输入要隐藏的文本信息...")
        self.btn_load_secret_file = QPushButton("从文件加载")
        
        # 嵌入策略选择
        self.cmb_embed_method = QComboBox()
        self.cmb_embed_method.addItems(["普通LSB", "纹理自适应LSB"])
        
        # 梯度阈值设置（仅用于纹理自适应模式）
        self.lbl_threshold = QLabel("梯度阈值:")
        self.spn_threshold = QSpinBox()
        self.spn_threshold.setRange(0, 255)
        self.spn_threshold.setValue(30)
        self.spn_threshold.setEnabled(False)  # 初始禁用，仅在选择纹理自适应时启用
        
        # 嵌入/提取按钮
        self.btn_embed = QPushButton("嵌入信息")
        self.btn_embed.setEnabled(False)
        self.btn_extract = QPushButton("提取信息")
        self.btn_extract.setEnabled(False)
        
        # 添加到布局
        layout.addWidget(QLabel("秘密信息:"), 0, 0, 1, 2)
        layout.addWidget(self.txt_secret, 1, 0, 1, 2)
        layout.addWidget(self.btn_load_secret_file, 2, 0, 1, 2)
        
        layout.addWidget(QLabel("嵌入策略:"), 3, 0)
        layout.addWidget(self.cmb_embed_method, 3, 1)
        
        layout.addWidget(self.lbl_threshold, 4, 0)
        layout.addWidget(self.spn_threshold, 4, 1)
        
        layout.addWidget(self.btn_embed, 5, 0)
        layout.addWidget(self.btn_extract, 5, 1)
        
        return group
    
    def _create_attack_selection_group(self):
        """创建攻击选择区"""
        group = QGroupBox("攻击选择")
        layout = QGridLayout(group)
        
        # 攻击类型选择
        self.cmb_attack_type = QComboBox()
        self.cmb_attack_type.addItems(["JPEG压缩", "高斯滤波", "图像裁剪", "高斯噪声"])
        
        # 攻击参数设置
        self.lbl_attack_param = QLabel("压缩质量:")
        self.sld_attack_param = QSlider(Qt.Horizontal)
        self.sld_attack_param.setRange(0, 100)
        self.sld_attack_param.setValue(75)
        self.lbl_attack_value = QLabel("75")
        
        # 应用攻击按钮
        self.btn_apply_attack = QPushButton("应用攻击")
        self.btn_apply_attack.setEnabled(False)
        
        # 添加到布局
        layout.addWidget(QLabel("攻击类型:"), 0, 0)
        layout.addWidget(self.cmb_attack_type, 0, 1, 1, 2)
        
        layout.addWidget(self.lbl_attack_param, 1, 0)
        layout.addWidget(self.sld_attack_param, 1, 1)
        layout.addWidget(self.lbl_attack_value, 1, 2)
        
        layout.addWidget(self.btn_apply_attack, 2, 0, 1, 3)
        
        return group
    
    def _create_metrics_group(self):
        """创建评估报告区"""
        group = QGroupBox("评估报告")
        layout = QGridLayout(group)
        
        # 图像质量指标
        self.lbl_psnr = QLabel("PSNR: --")
        self.lbl_ssim = QLabel("SSIM: --")
        self.lbl_ber = QLabel("BER: --")
        
        # 添加到布局
        layout.addWidget(self.lbl_psnr, 0, 0)
        layout.addWidget(self.lbl_ssim, 1, 0)
        layout.addWidget(self.lbl_ber, 2, 0)
        
        return group
    
    def _create_visualization_tabs(self):
        """创建可视化标签页"""
        tabs = QTabWidget()
        
        # 图像显示标签页
        image_tab = QWidget()
        image_layout = QGridLayout(image_tab)
        
        # 创建三个图像查看器：原始图、含密图、攻击后图
        self.original_viewer = ImageViewer("原始载体图像")
        self.stego_viewer = ImageViewer("含密图像")
        self.attacked_viewer = ImageViewer("攻击后图像")
        
        # 添加到布局
        image_layout.addWidget(self.original_viewer, 0, 0)
        image_layout.addWidget(self.stego_viewer, 0, 1)
        image_layout.addWidget(self.attacked_viewer, 1, 0, 1, 2)
        
        # 位平面可视化标签页
        bitplane_tab = QWidget()
        bitplane_layout = QVBoxLayout(bitplane_tab)
        self.bitplane_viewer = BitPlaneViewer()
        bitplane_layout.addWidget(self.bitplane_viewer)
        
        # BER曲线标签页
        ber_tab = QWidget()
        ber_layout = QVBoxLayout(ber_tab)
        self.ber_chart = MetricsChart("攻击参数", "BER值", "BER曲线")
        ber_layout.addWidget(self.ber_chart)
        
        # 添加标签页
        tabs.addTab(image_tab, "图像显示")
        tabs.addTab(bitplane_tab, "位平面可视化")
        tabs.addTab(ber_tab, "BER曲线")
        
        return tabs
    
    def _init_menu_bar(self):
        """初始化菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        open_action = QAction("打开载体图像", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("保存含密图像", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        export_action = QAction("导出数据", self)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # 操作菜单
        operation_menu = menu_bar.addMenu("操作")
        
        embed_action = QAction("嵌入信息", self)
        operation_menu.addAction(embed_action)
        
        extract_action = QAction("提取信息", self)
        operation_menu.addAction(extract_action)
        
        operation_menu.addSeparator()
        
        attack_action = QAction("应用攻击", self)
        operation_menu.addAction(attack_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        help_menu.addAction(about_action)
        
        # 连接菜单动作
        open_action.triggered.connect(self._on_load_cover_clicked)
        save_action.triggered.connect(self._on_save_stego_clicked)
        export_action.triggered.connect(self._on_export_data_clicked)
        exit_action.triggered.connect(self.close)
        
        embed_action.triggered.connect(self._on_embed_clicked)
        extract_action.triggered.connect(self._on_extract_clicked)
        attack_action.triggered.connect(self._on_apply_attack_clicked)
        
        about_action.triggered.connect(self._show_about_dialog)
    
    def _init_tool_bar(self):
        """初始化工具栏"""
        tool_bar = self.addToolBar("工具栏")
        tool_bar.setMovable(False)
        
        # 添加工具栏按钮
        open_action = QAction("打开", self)
        open_action.triggered.connect(self._on_load_cover_clicked)
        tool_bar.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._on_save_stego_clicked)
        tool_bar.addAction(save_action)
        
        tool_bar.addSeparator()
        
        embed_action = QAction("嵌入", self)
        embed_action.triggered.connect(self._on_embed_clicked)
        tool_bar.addAction(embed_action)
        
        extract_action = QAction("提取", self)
        extract_action.triggered.connect(self._on_extract_clicked)
        tool_bar.addAction(extract_action)
        
        tool_bar.addSeparator()
        
        attack_action = QAction("攻击", self)
        attack_action.triggered.connect(self._on_apply_attack_clicked)
        tool_bar.addAction(attack_action)
    
    def _init_status_bar(self):
        """初始化状态栏"""
        status_bar = self.statusBar()
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
    
    def _connect_signals_slots(self):
        """连接信号和槽"""
        # 文件操作
        self.btn_load_cover.clicked.connect(self._on_load_cover_clicked)
        self.btn_save_stego.clicked.connect(self._on_save_stego_clicked)
        self.btn_export_data.clicked.connect(self._on_export_data_clicked)
        self.btn_load_secret_file.clicked.connect(self._on_load_secret_file_clicked)
        
        # 隐写控制
        self.cmb_embed_method.currentIndexChanged.connect(self._on_embed_method_changed)
        self.btn_embed.clicked.connect(self._on_embed_clicked)
        self.btn_extract.clicked.connect(self._on_extract_clicked)
        
        # 攻击选择
        self.cmb_attack_type.currentIndexChanged.connect(self._on_attack_type_changed)
        self.sld_attack_param.valueChanged.connect(self._on_attack_param_changed)
        self.btn_apply_attack.clicked.connect(self._on_apply_attack_clicked)
    
    # 槽函数 - 文件操作
    def _on_load_cover_clicked(self):
        """加载载体图像"""
        self.status_label.setText("选择载体图像...")
        
        # 打开文件对话框选择图像
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择载体图像",
            "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.tif)"
        )
        
        if not file_path:
            self.status_label.setText("已取消选择载体图像")
            return
        
        try:
            # 导入图像处理工具
            from utils.image_utils import read_image
            
            # 读取图像
            self.cover_image = read_image(file_path)
            
            # 更新UI
            self.lbl_cover_path.setText(file_path)
            self.original_viewer.set_image(self.cover_image)
            self.bitplane_viewer.set_image(self.cover_image)
            
            # 启用相关按钮
            self.btn_embed.setEnabled(True)
            self.status_label.setText("载体图像加载成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载图像: {str(e)}")
            self.status_label.setText("载体图像加载失败")
            return
    
    def _on_save_stego_clicked(self):
        """保存含密图像"""
        # 检查是否有含密图像
        if not hasattr(self, 'stego_image') or self.stego_image is None:
            QMessageBox.warning(self, "警告", "没有可用的含密图像")
            return
        
        # 打开文件对话框选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存含密图像",
            "",
            "PNG图像 (*.png);;BMP图像 (*.bmp);;所有文件 (*.*)"
        )
        
        if not file_path:
            self.status_label.setText("已取消保存含密图像")
            return
        
        try:
            # 导入图像处理工具
            from utils.image_utils import save_image
            
            # 保存图像
            save_image(self.stego_image, file_path)
            
            self.status_label.setText(f"含密图像已保存至: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存图像失败: {str(e)}")
            self.status_label.setText("含密图像保存失败")
            return
    
    def _on_export_data_clicked(self):
        """导出实验数据"""
        # 检查是否有数据可导出
        if not hasattr(self, 'ber_chart') or not self.ber_chart.has_data():
            QMessageBox.warning(self, "警告", "没有可导出的实验数据")
            return
        
        export_format = self.cmb_export_format.currentText()
        self.status_label.setText(f"导出数据为{export_format}格式...")
        
        # 打开文件对话框选择保存路径
        file_filter = "CSV文件 (*.csv)" if export_format == "CSV" else "PNG图像 (*.png)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出实验数据",
            "",
            file_filter
        )
        
        if not file_path:
            self.status_label.setText("已取消导出数据")
            return
        
        try:
            # 根据选择的格式导出数据
            if export_format == "CSV":
                self.ber_chart.export_to_csv(file_path)
            else:  # PNG
                self.ber_chart.export_to_image(file_path)
            
            self.status_label.setText(f"实验数据已导出至: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败: {str(e)}")
            self.status_label.setText("数据导出失败")
            return
    
    def _on_load_secret_file_clicked(self):
        """从文件加载秘密信息"""
        self.status_label.setText("加载秘密信息文件...")
        
        # 打开文件对话框选择文本文件
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择秘密信息文件",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if not file_path:
            self.status_label.setText("已取消加载秘密信息文件")
            return
        
        try:
            # 读取文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                secret_data = f.read()
            
            # 更新文本框
            self.txt_secret.setText(secret_data)
            
            self.status_label.setText("秘密信息文件加载成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载秘密信息文件失败: {str(e)}")
            self.status_label.setText("秘密信息文件加载失败")
            return
    
    # 槽函数 - 隐写控制
    def _on_embed_method_changed(self, index):
        """嵌入方法改变"""
        # 纹理自适应模式下启用梯度阈值设置
        self.spn_threshold.setEnabled(index == 1)
        self.status_label.setText(f"已选择{self.cmb_embed_method.currentText()}嵌入方法")
    
    def _on_embed_clicked(self):
        """嵌入信息"""
        # 检查是否已加载载体图像
        if not hasattr(self, 'cover_image') or self.cover_image is None:
            QMessageBox.warning(self, "警告", "请先加载载体图像")
            return
        
        # 获取秘密信息
        secret_data = self.txt_secret.toPlainText()
        if not secret_data:
            QMessageBox.warning(self, "警告", "请输入要嵌入的秘密信息")
            return
        
        # 获取嵌入方法和参数
        method = self.cmb_embed_method.currentText()
        threshold = self.spn_threshold.value() if method == "纹理自适应LSB" else None
        
        self.status_label.setText("正在嵌入信息...")
        
        try:
            # 根据选择的方法调用相应的嵌入算法
            if method == "普通LSB":
                from core.lsb import LSBSteganography
                self.stego_image = LSBSteganography.embed(self.cover_image, secret_data)
            else:  # 纹理自适应LSB
                from core.sobel_adaptive import SobelAdaptiveSteganography
                self.stego_image = SobelAdaptiveSteganography.embed(self.cover_image, secret_data, threshold)
            
            # 更新UI显示
            self.stego_viewer.set_image(self.stego_image)
            
            # 计算并显示图像质量指标
            self._update_metrics(self.cover_image, self.stego_image)
            
            # 启用相关按钮
            self.btn_save_stego.setEnabled(True)
            self.btn_extract.setEnabled(True)
            self.btn_apply_attack.setEnabled(True)
            self.btn_export_data.setEnabled(True)
            
            self.status_label.setText("信息嵌入成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"嵌入信息失败: {str(e)}")
            self.status_label.setText("信息嵌入失败")
            return
    
    def _on_extract_clicked(self):
        """提取信息"""
        # 检查是否有含密图像
        if not hasattr(self, 'stego_image') or self.stego_image is None:
            # 如果没有含密图像，检查是否有攻击后的图像
            if hasattr(self, 'attacked_image') and self.attacked_image is not None:
                extract_image = self.attacked_image
            else:
                QMessageBox.warning(self, "警告", "没有可用的含密图像")
                return
        else:
            extract_image = self.stego_image
        
        self.status_label.setText("正在提取信息...")
        
        try:
            # 根据当前选择的方法提取信息
            method = self.cmb_embed_method.currentText()
            
            if method == "普通LSB":
                from core.lsb import LSBSteganography
                extracted_data = LSBSteganography.extract(extract_image)
            else:  # 纹理自适应LSB
                from core.sobel_adaptive import SobelAdaptiveSteganography
                threshold = self.spn_threshold.value()
                extracted_data = SobelAdaptiveSteganography.extract(extract_image, threshold)
            
            # 显示提取的信息
            self.txt_secret.setText(extracted_data)
            
            # 如果是从攻击后的图像提取，计算BER
            if hasattr(self, 'original_secret') and hasattr(self, 'attacked_image'):
                from utils.metrics import calculate_ber_text
                ber = calculate_ber_text(self.original_secret, extracted_data)
                self.lbl_ber.setText(f"BER: {ber:.4f}")
            
            self.status_label.setText("信息提取成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"提取信息失败: {str(e)}")
            self.status_label.setText("信息提取失败")
            return
    
    # 槽函数 - 攻击选择
    def _on_attack_type_changed(self, index):
        """攻击类型改变"""
        attack_types = ["压缩质量:", "滤波半径:", "裁剪比例:", "噪声强度:"]
        self.lbl_attack_param.setText(attack_types[index])
        
        # 根据攻击类型设置滑动条范围和初始值
        if index == 0:  # JPEG压缩
            self.sld_attack_param.setRange(0, 100)
            self.sld_attack_param.setValue(75)
        elif index == 1:  # 高斯滤波
            self.sld_attack_param.setRange(1, 10)
            self.sld_attack_param.setValue(3)
        elif index == 2:  # 图像裁剪
            self.sld_attack_param.setRange(10, 90)
            self.sld_attack_param.setValue(50)
        elif index == 3:  # 高斯噪声
            self.sld_attack_param.setRange(1, 50)
            self.sld_attack_param.setValue(10)
        
        self._on_attack_param_changed(self.sld_attack_param.value())
    
    def _on_attack_param_changed(self, value):
        """攻击参数改变"""
        self.lbl_attack_value.setText(str(value))
    
    def _on_apply_attack_clicked(self):
        """应用攻击"""
        # 检查是否有含密图像
        if not hasattr(self, 'stego_image') or self.stego_image is None:
            QMessageBox.warning(self, "警告", "请先嵌入信息生成含密图像")
            return
        
        # 获取攻击类型和参数
        attack_type = self.cmb_attack_type.currentText()
        attack_param = self.sld_attack_param.value()
        
        self.status_label.setText(f"正在应用{attack_type}攻击，参数值:{attack_param}...")
        
        try:
            # 导入攻击模拟器
            from core.attack_simulator import AttackSimulator
            
            # 根据攻击类型调用相应的攻击方法
            if attack_type == "JPEG压缩":
                self.attacked_image = AttackSimulator.jpeg_compression(self.stego_image, attack_param)
            elif attack_type == "高斯滤波":
                self.attacked_image = AttackSimulator.gaussian_blur(self.stego_image, attack_param)
            elif attack_type == "图像裁剪":
                crop_ratio = attack_param / 100.0  # 转换为0-1范围
                self.attacked_image = AttackSimulator.crop_attack(self.stego_image, crop_ratio)
            elif attack_type == "高斯噪声":
                noise_level = attack_param / 100.0  # 转换为0-1范围
                self.attacked_image = AttackSimulator.gaussian_noise(self.stego_image, noise_level)
            
            # 更新UI显示
            self.attacked_viewer.set_image(self.attacked_image)
            
            # 保存原始秘密信息用于BER计算
            if not hasattr(self, 'original_secret'):
                self.original_secret = self.txt_secret.toPlainText()
            
            # 更新BER曲线
            self._update_ber_chart(attack_type, attack_param)
            
            self.status_label.setText(f"{attack_type}攻击应用成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用攻击失败: {str(e)}")
            self.status_label.setText("攻击应用失败")
            return
    
    def _update_metrics(self, original_image, modified_image):
        """更新图像质量评估指标"""
        try:
            # 导入评估指标计算工具
            from utils.metrics import calculate_psnr, calculate_ssim
            
            # 计算PSNR
            psnr = calculate_psnr(original_image, modified_image)
            self.lbl_psnr.setText(f"PSNR: {psnr:.2f} dB")
            
            # 计算SSIM
            ssim = calculate_ssim(original_image, modified_image)
            self.lbl_ssim.setText(f"SSIM: {ssim:.4f}")
            
            # 重置BER（只有在攻击后才会计算）
            self.lbl_ber.setText("BER: --")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"计算评估指标时出错: {str(e)}")
            self.lbl_psnr.setText("PSNR: --")
            self.lbl_ssim.setText("SSIM: --")
            self.lbl_ber.setText("BER: --")
            self.status_label.setText("评估指标计算失败")
    
    def _update_ber_chart(self, attack_type, param_value):
        """更新BER曲线"""
        try:
            # 提取攻击后图像中的信息
            method = self.cmb_embed_method.currentText()
            
            if method == "普通LSB":
                from core.lsb import LSBSteganography
                extracted_data = LSBSteganography.extract(self.attacked_image)
            else:  # 纹理自适应LSB
                from core.sobel_adaptive import SobelAdaptiveSteganography
                threshold = self.spn_threshold.value()
                extracted_data = SobelAdaptiveSteganography.extract(self.attacked_image, threshold)
            
            # 计算BER
            from utils.metrics import calculate_ber_text
            ber = calculate_ber_text(self.original_secret, extracted_data)
            
            # 更新BER标签
            self.lbl_ber.setText(f"BER: {ber:.4f}")
            
            # 添加数据点到BER曲线
            self.ber_chart.add_data_point(param_value, ber, attack_type)
        except Exception as e:
            print(f"更新BER曲线时出错: {str(e)}")
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "<h3>图像隐写与抗攻击性研究</h3>"
            "<p>本科毕业设计</p>"
            "<p>版本: 1.0.0</p>"
        )