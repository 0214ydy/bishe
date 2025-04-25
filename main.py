#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """程序入口函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("图像隐写与抗攻击性研究")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 进入应用程序主循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()