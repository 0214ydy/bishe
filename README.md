steganography_project/
├── core/                  # 核心算法模块
│   ├── __init__.py
│   ├── lsb.py             # 基础LSB算法实现
│   ├── sobel_adaptive.py  # Sobel梯度自适应嵌入算法
│   └── attack_simulator.py # 攻击模拟器（压缩/滤波/裁剪/噪声）
│
├── ui/                    # UI相关文件
│   ├── main_window.py     # 主窗口类
│   ├── widgets.py         # 自定义控件（如图表区域）
│   └── resources.qrc      # 资源文件（图标等）
│
├── utils/                 # 工具模块
│   ├── image_utils.py     # 图像处理工具
│   ├── metrics.py         # 评估指标计算（PSNR/SSIM/BER）
│   └── logger.py          # 日志记录
│
├── tests/                 # 测试数据集
│   ├── original_images/
│   └── stego_images/
│
├── results/               # 结果输出
│   ├── ber_curves/
│   └── comparison_charts/
│
├── main.py                # 程序入口
└── requirements.txt       # 依赖库列表


本科毕业设计课题是数字图像隐写与抗攻击性质的研究，项目总体框架是

1.核心目标

• 实现基础 ：经典LSB隐写算法（灰度图/彩色图）

• 创新改进 ：基于Sobel梯度的轻量化纹理自适应嵌入策略

抗攻击实验 ：验证改进算法在压缩、滤波、裁剪、噪声攻击下的数据恢复效果

2.技术路线图

载体图像 → 纹理区域检测（Sobel梯度） → 自适应嵌入（纹理区优先） → 含密图像

含密图像 → 攻击处理（压缩/滤波/裁剪/噪声） → 信息提取 → 对比分析（BER/PSNR/SSIM）

3. 主界面布局

模块 功能描述

文件操作 导入载体图像（BMP/PNG）、保存含密图像、导出实验数据（CSV / 图片）

隐写控制 输入秘密信息（文本 / 文件）、选择嵌入策略（普通 LSB / 纹理自适应）、设置梯度阈值

攻击选择 滑动条调节攻击参数（如 JPEG 质量、噪声比例）、一键施加攻击（攻击类型下拉菜单）

可视化 显示原始图 / 含密图 / 攻击后图、位平面可视化（LSB 平面）、BER 曲线动态绘制

评估报告 自动生成 PSNR、SSIM、BER 数据表格，支持导出对比图

