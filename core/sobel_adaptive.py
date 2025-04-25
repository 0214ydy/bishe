#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from typing import Tuple, Union, List
from core.lsb import LSBSteganography


class SobelAdaptiveSteganography:
    """基于Sobel梯度的自适应LSB隐写算法实现"""
    
    @staticmethod
    def compute_sobel_gradient(image: np.ndarray) -> np.ndarray:
        """计算图像的Sobel梯度
        
        Args:
            image: 输入图像，numpy数组格式
        
        Returns:
            Sobel梯度图像
        """
        # 如果是彩色图像，转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # 计算x和y方向的梯度
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算梯度幅值
        grad_magnitude = cv2.magnitude(grad_x, grad_y)
        
        # 归一化到0-255范围
        grad_magnitude = cv2.normalize(grad_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        return grad_magnitude
    
    @staticmethod
    def create_embedding_mask(gradient: np.ndarray, threshold: int) -> np.ndarray:
        """根据梯度图创建嵌入掩码
        
        Args:
            gradient: Sobel梯度图像
            threshold: 梯度阈值，大于此值的区域被认为是纹理区域
        
        Returns:
            嵌入掩码，1表示可嵌入区域，0表示不可嵌入区域
        """
        # 创建掩码，梯度大于阈值的区域为1（纹理区域），其他为0
        mask = (gradient > threshold).astype(np.uint8)
        return mask
    
    @staticmethod
    def embed(cover_image: np.ndarray, secret_data: str, threshold: int = 30) -> np.ndarray:
        """使用基于Sobel梯度的自适应策略嵌入秘密信息
        
        Args:
            cover_image: 载体图像，numpy数组格式
            secret_data: 要嵌入的秘密信息字符串
            threshold: 梯度阈值，默认为30
        
        Returns:
            包含秘密信息的图像（numpy数组）
        """
        # 计算Sobel梯度
        gradient = SobelAdaptiveSteganography.compute_sobel_gradient(cover_image)
        
        # 创建嵌入掩码
        mask = SobelAdaptiveSteganography.create_embedding_mask(gradient, threshold)
        
        # 将秘密信息转换为二进制字符串
        binary_data = ''.join(format(ord(char), '08b') for char in secret_data)
        # 添加结束标记
        binary_data += '00000000'
        
        # 检查载体图像容量是否足够
        data_len = len(binary_data)
        available_pixels = np.sum(mask)
        
        if len(cover_image.shape) == 3:  # 彩色图像
            available_capacity = available_pixels * 3  # RGB三个通道
        else:  # 灰度图像
            available_capacity = available_pixels
        
        if available_capacity < data_len:
            # 如果纹理区域容量不足，降低阈值
            new_threshold = threshold
            while available_capacity < data_len and new_threshold > 0:
                new_threshold -= 5
                mask = SobelAdaptiveSteganography.create_embedding_mask(gradient, new_threshold)
                available_pixels = np.sum(mask)
                
                if len(cover_image.shape) == 3:
                    available_capacity = available_pixels * 3
                else:
                    available_capacity = available_pixels
            
            if available_capacity < data_len:
                raise ValueError("载体图像纹理区域容量不足以嵌入所有秘密信息")
        
        # 创建输出图像的副本
        stego_image = cover_image.copy()
        
        # 获取图像尺寸
        height, width = cover_image.shape[:2]
        
        # 嵌入数据
        data_index = 0
        for i in range(height):
            for j in range(width):
                if data_index < data_len and mask[i, j] == 1:  # 只在纹理区域嵌入
                    # 对于灰度图像
                    if len(cover_image.shape) == 2:
                        # 获取像素值
                        pixel = stego_image[i, j]
                        # 修改最低有效位
                        stego_image[i, j] = (pixel & 0xFE) | int(binary_data[data_index])
                        data_index += 1
                    # 对于彩色图像
                    elif len(cover_image.shape) == 3:
                        for k in range(3):  # RGB三个通道
                            if data_index < data_len:
                                pixel = stego_image[i, j, k]
                                stego_image[i, j, k] = (pixel & 0xFE) | int(binary_data[data_index])
                                data_index += 1
                if data_index >= data_len:
                    break
            if data_index >= data_len:
                break
        
        return stego_image
    
    @staticmethod
    def extract(stego_image: np.ndarray, threshold: int = 30) -> str:
        """从含密图像中提取秘密信息
        
        Args:
            stego_image: 含密图像，numpy数组格式
            threshold: 梯度阈值，默认为30
        
        Returns:
            提取的秘密信息字符串
        """
        # 计算Sobel梯度
        gradient = SobelAdaptiveSteganography.compute_sobel_gradient(stego_image)
        
        # 创建嵌入掩码
        mask = SobelAdaptiveSteganography.create_embedding_mask(gradient, threshold)
        
        # 获取图像尺寸
        height, width = stego_image.shape[:2]
        
        # 提取二进制数据
        binary_data = ""
        for i in range(height):
            for j in range(width):
                if mask[i, j] == 1:  # 只从纹理区域提取
                    # 对于灰度图像
                    if len(stego_image.shape) == 2:
                        # 提取最低有效位
                        binary_data += str(stego_image[i, j] & 1)
                    # 对于彩色图像
                    elif len(stego_image.shape) == 3:
                        for k in range(3):  # RGB三个通道
                            binary_data += str(stego_image[i, j, k] & 1)
                    
                    # 每8位检查一次是否到达结束标记
                    if len(binary_data) % 8 == 0 and len(binary_data) >= 8:
                        # 检查最后8位是否为结束标记
                        if binary_data[-8:] == "00000000":
                            # 移除结束标记
                            binary_data = binary_data[:-8]
                            # 转换二进制数据为字符串
                            secret_data = ""
                            for b in range(0, len(binary_data), 8):
                                byte = binary_data[b:b+8]
                                if len(byte) == 8:  # 确保完整的字节
                                    secret_data += chr(int(byte, 2))
                            return secret_data
        
        # 如果没有找到结束标记，尝试解析所有数据
        secret_data = ""
        for b in range(0, len(binary_data), 8):
            byte = binary_data[b:b+8]
            if len(byte) == 8:  # 确保完整的字节
                secret_data += chr(int(byte, 2))
        
        return secret_data
    
    @staticmethod
    def get_embedding_capacity(cover_image: np.ndarray, threshold: int = 30) -> int:
        """计算载体图像的自适应嵌入容量（以字节为单位）
        
        Args:
            cover_image: 载体图像，numpy数组格式
            threshold: 梯度阈值，默认为30
        
        Returns:
            可嵌入的最大字节数
        """
        # 计算Sobel梯度
        gradient = SobelAdaptiveSteganography.compute_sobel_gradient(cover_image)
        
        # 创建嵌入掩码
        mask = SobelAdaptiveSteganography.create_embedding_mask(gradient, threshold)
        
        # 计算可用像素数
        available_pixels = np.sum(mask)
        
        if len(cover_image.shape) == 2:  # 灰度图
            return available_pixels // 8
        elif len(cover_image.shape) == 3:  # 彩色图
            return (available_pixels * 3) // 8
        else:
            return 0