#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from typing import Tuple, Union, List, Dict, Any
import os
import tempfile


class AttackSimulator:
    """图像攻击模拟器
    
    实现四种常见的图像攻击方法：
    1. JPEG压缩攻击
    2. 高斯滤波攻击
    3. 图像裁剪攻击
    4. 高斯噪声攻击
    
    每种攻击都支持参数调节，并提供统一的接口供UI调用
    """
    
    @staticmethod
    def jpeg_compression(image: np.ndarray, quality: int = 75) -> np.ndarray:
        """JPEG压缩攻击
        
        Args:
            image: 输入图像，numpy数组格式
            quality: JPEG压缩质量，范围1-100，值越小压缩越强
        
        Returns:
            经过JPEG压缩后的图像
        """
        if quality < 1 or quality > 100:
            raise ValueError("JPEG压缩质量必须在1-100范围内")
        
        # 创建临时文件用于JPEG压缩
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 保存为JPEG格式
            cv2.imwrite(temp_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            # 读取压缩后的图像
            compressed_image = cv2.imread(temp_path)
            
            # 确保图像尺寸一致
            if compressed_image.shape != image.shape:
                compressed_image = cv2.resize(compressed_image, (image.shape[1], image.shape[0]))
                
            return compressed_image
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @staticmethod
    def gaussian_blur(image: np.ndarray, kernel_size: int = 3, sigma: float = 1.0) -> np.ndarray:
        """高斯滤波攻击
        
        Args:
            image: 输入图像，numpy数组格式
            kernel_size: 高斯核大小，必须为奇数
            sigma: 高斯核标准差
        
        Returns:
            经过高斯滤波后的图像
        """
        if kernel_size % 2 == 0:
            kernel_size += 1  # 确保核大小为奇数
        
        # 应用高斯滤波
        blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
        return blurred_image
    
    @staticmethod
    def crop_attack(image: np.ndarray, crop_ratio: float = 0.9) -> np.ndarray:
        """图像裁剪攻击
        
        Args:
            image: 输入图像，numpy数组格式
            crop_ratio: 裁剪比例，范围0-1，表示保留的图像比例
        
        Returns:
            经过裁剪并恢复原始尺寸的图像
        """
        if crop_ratio <= 0 or crop_ratio >= 1:
            raise ValueError("裁剪比例必须在0-1范围内")
        
        height, width = image.shape[:2]
        
        # 计算裁剪区域
        crop_height = int(height * crop_ratio)
        crop_width = int(width * crop_ratio)
        
        # 计算裁剪起始点（居中裁剪）
        start_y = (height - crop_height) // 2
        start_x = (width - crop_width) // 2
        
        # 裁剪图像
        cropped_image = image[start_y:start_y+crop_height, start_x:start_x+crop_width].copy()
        
        # 恢复原始尺寸
        restored_image = cv2.resize(cropped_image, (width, height))
        
        return restored_image
    
    @staticmethod
    def gaussian_noise(image: np.ndarray, mean: float = 0, sigma: float = 10.0) -> np.ndarray:
        """高斯噪声攻击
        
        Args:
            image: 输入图像，numpy数组格式
            mean: 高斯噪声均值
            sigma: 高斯噪声标准差，值越大噪声越强
        
        Returns:
            添加高斯噪声后的图像
        """
        # 创建与图像相同形状的高斯噪声
        noise = np.random.normal(mean, sigma, image.shape).astype(np.float32)
        
        # 添加噪声到图像
        noisy_image = image.astype(np.float32) + noise
        
        # 裁剪到有效范围
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        
        return noisy_image
    
    @staticmethod
    def apply_attack(image: np.ndarray, attack_type: str, params: Dict[str, Any] = None) -> np.ndarray:
        """应用指定类型的攻击
        
        Args:
            image: 输入图像，numpy数组格式
            attack_type: 攻击类型，可选值：'jpeg', 'blur', 'crop', 'noise'
            params: 攻击参数字典
        
        Returns:
            经过攻击后的图像
        """
        if params is None:
            params = {}
        
        if attack_type == 'jpeg':
            quality = params.get('quality', 75)
            return AttackSimulator.jpeg_compression(image, quality)
        
        elif attack_type == 'blur':
            kernel_size = params.get('kernel_size', 3)
            sigma = params.get('sigma', 1.0)
            return AttackSimulator.gaussian_blur(image, kernel_size, sigma)
        
        elif attack_type == 'crop':
            crop_ratio = params.get('crop_ratio', 0.9)
            return AttackSimulator.crop_attack(image, crop_ratio)
        
        elif attack_type == 'noise':
            mean = params.get('mean', 0)
            sigma = params.get('sigma', 10.0)
            return AttackSimulator.gaussian_noise(image, mean, sigma)
        
        else:
            raise ValueError(f"不支持的攻击类型: {attack_type}")