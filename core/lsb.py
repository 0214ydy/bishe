#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Tuple, Union, List


class LSBSteganography:
    """基础LSB隐写算法实现"""
    
    @staticmethod
    def embed(cover_image: np.ndarray, secret_data: str) -> np.ndarray:
        """在载体图像中嵌入秘密信息
        
        Args:
            cover_image: 载体图像，numpy数组格式
            secret_data: 要嵌入的秘密信息字符串
        
        Returns:
            包含秘密信息的图像（numpy数组）
        """
        # 将秘密信息转换为二进制字符串
        binary_data = ''.join(format(ord(char), '08b') for char in secret_data)
        # 添加结束标记
        binary_data += '00000000'
        
        # 检查载体图像容量是否足够
        data_len = len(binary_data)
        if len(cover_image.flatten()) < data_len:
            raise ValueError("载体图像容量不足以嵌入所有秘密信息")
        
        # 创建输出图像的副本
        stego_image = cover_image.copy()
        
        # 获取图像尺寸
        height, width = cover_image.shape[:2]
        
        # 嵌入数据
        data_index = 0
        for i in range(height):
            for j in range(width):
                if data_index < data_len:
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
                else:
                    break
            if data_index >= data_len:
                break
        
        return stego_image
    
    @staticmethod
    def extract(stego_image: np.ndarray) -> str:
        """从含密图像中提取秘密信息
        
        Args:
            stego_image: 含密图像，numpy数组格式
        
        Returns:
            提取的秘密信息字符串
        """
        # 获取图像尺寸
        height, width = stego_image.shape[:2]
        
        # 提取二进制数据
        binary_data = ""
        for i in range(height):
            for j in range(width):
                # 对于灰度图像
                if len(stego_image.shape) == 2:
                    # 提取最低有效位
                    binary_data += str(stego_image[i, j] & 1)
                # 对于彩色图像
                elif len(stego_image.shape) == 3:
                    for k in range(3):  # RGB三个通道
                        binary_data += str(stego_image[i, j, k] & 1)
                
                # 每8位检查一次是否到达结束标记
                if len(binary_data) % 8 == 0:
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
    def get_embedding_capacity(cover_image: np.ndarray) -> int:
        """计算载体图像的嵌入容量（以字节为单位）
        
        Args:
            cover_image: 载体图像，numpy数组格式
        
        Returns:
            可嵌入的最大字节数
        """
        if len(cover_image.shape) == 2:  # 灰度图
            return cover_image.size // 8
        elif len(cover_image.shape) == 3:  # 彩色图
            return (cover_image.shape[0] * cover_image.shape[1] * 3) // 8
        else:
            return 0

