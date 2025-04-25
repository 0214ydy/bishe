import numpy as np
import cv2
from scipy import signal


def calculate_psnr(original, modified):
    """
    计算峰值信噪比(PSNR)，评估图像质量
    
    参数:
        original: 原始图像
        modified: 修改后的图像
        
    返回:
        PSNR值，单位为dB
    """
    if original.shape != modified.shape:
        raise ValueError("输入图像尺寸不匹配")
    
    # 确保图像为uint8类型
    if original.dtype != np.uint8:
        original = np.clip(original, 0, 255).astype(np.uint8)
    if modified.dtype != np.uint8:
        modified = np.clip(modified, 0, 255).astype(np.uint8)
    
    # 计算均方误差(MSE)
    mse = np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')  # 如果图像完全相同
    
    # 计算PSNR
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


def calculate_ssim(original, modified, win_size=11, sigma=1.5):
    """
    计算结构相似性指数(SSIM)，评估图像结构相似度
    
    参数:
        original: 原始图像
        modified: 修改后的图像
        win_size: 窗口大小
        sigma: 高斯滤波器标准差
        
    返回:
        SSIM值，范围为[-1, 1]，值越大表示相似度越高
    """
    if original.shape != modified.shape:
        raise ValueError("输入图像尺寸不匹配")
    
    # 确保图像为灰度图
    if len(original.shape) == 3:
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    if len(modified.shape) == 3:
        modified = cv2.cvtColor(modified, cv2.COLOR_BGR2GRAY)
    
    # 确保图像为float类型
    original = original.astype(np.float64)
    modified = modified.astype(np.float64)
    
    # 创建高斯窗口
    gaussian_window = cv2.getGaussianKernel(win_size, sigma)
    window = np.outer(gaussian_window, gaussian_window.transpose())
    
    # 常数，防止分母为零
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    
    # 计算均值
    mu1 = signal.convolve2d(original, window, mode='valid')
    mu2 = signal.convolve2d(modified, window, mode='valid')
    
    # 计算方差和协方差
    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2
    
    sigma1_sq = signal.convolve2d(original ** 2, window, mode='valid') - mu1_sq
    sigma2_sq = signal.convolve2d(modified ** 2, window, mode='valid') - mu2_sq
    sigma12 = signal.convolve2d(original * modified, window, mode='valid') - mu1_mu2
    
    # 计算SSIM
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    
    return np.mean(ssim_map)


def calculate_ber(original_bits, extracted_bits):
    """
    计算比特错误率(BER)，评估隐写信息的提取准确性
    
    参数:
        original_bits: 原始嵌入的比特序列
        extracted_bits: 提取出的比特序列
        
    返回:
        BER值，范围为[0, 1]，值越小表示提取越准确
    """
    if len(original_bits) != len(extracted_bits):
        raise ValueError("输入比特序列长度不匹配")
    
    # 确保输入为numpy数组
    if not isinstance(original_bits, np.ndarray):
        original_bits = np.array(original_bits)
    if not isinstance(extracted_bits, np.ndarray):
        extracted_bits = np.array(extracted_bits)
    
    # 计算错误比特数
    error_bits = np.sum(original_bits != extracted_bits)
    
    # 计算BER
    ber = error_bits / len(original_bits)
    return ber


def evaluate_image_quality(original, stego):
    """
    综合评估图像质量，计算PSNR和SSIM
    
    参数:
        original: 原始图像
        stego: 含密图像
        
    返回:
        包含PSNR和SSIM值的字典
    """
    psnr_value = calculate_psnr(original, stego)
    ssim_value = calculate_ssim(original, stego)
    
    return {
        'psnr': psnr_value,
        'ssim': ssim_value
    }


def calculate_ber_text(original_text, extracted_text):
    """
    计算文本数据的比特错误率(BER)，评估隐写信息的提取准确性
    
    参数:
        original_text: 原始嵌入的文本
        extracted_text: 提取出的文本
        
    返回:
        BER值，范围为[0, 1]，值越小表示提取越准确
    """
    # 如果输入为None，返回1.0（最大错误率）
    if original_text is None or extracted_text is None:
        return 1.0
    
    # 确保输入为字符串
    if not isinstance(original_text, str):
        original_text = str(original_text)
    if not isinstance(extracted_text, str):
        extracted_text = str(extracted_text)
    
    # 计算最小长度，避免索引越界
    min_length = min(len(original_text), len(extracted_text))
    
    if min_length == 0:
        return 1.0  # 如果任一字符串为空，返回最大错误率
    
    # 计算错误字符数
    error_count = sum(1 for i in range(min_length) if original_text[i] != extracted_text[i])
    
    # 如果提取文本比原始文本短，将剩余字符视为错误
    if len(original_text) > min_length:
        error_count += len(original_text) - min_length
    
    # 计算BER
    ber = error_count / len(original_text)
    return ber