import cv2
import numpy as np
from PIL import Image
import os


def read_image(image_path):
    """
    读取图像文件
    
    参数:
        image_path: 图像文件路径
        
    返回:
        numpy数组格式的图像数据
    """
    # 规范化路径，确保Windows路径正确处理
    image_path = os.path.normpath(image_path)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    # 使用OpenCV读取图像
    image = cv2.imread(image_path)
    
    # 如果读取失败，尝试使用PIL读取
    if image is None:
        try:
            pil_image = Image.open(image_path)
            image = np.array(pil_image)
            # 如果是RGB格式，转换为BGR（OpenCV默认格式）
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise IOError(f"无法读取图像文件: {e}")
    
    return image


def save_image(image, save_path):
    """
    保存图像到文件
    
    参数:
        image: numpy数组格式的图像数据
        save_path: 保存路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    
    # 保存图像
    result = cv2.imwrite(save_path, image)
    
    if not result:
        # 如果OpenCV保存失败，尝试使用PIL保存
        try:
            # 如果是BGR格式，转换为RGB（PIL默认格式）
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)
            pil_image.save(save_path)
        except Exception as e:
            raise IOError(f"无法保存图像文件: {e}")


def convert_to_grayscale(image):
    """
    将彩色图像转换为灰度图像
    
    参数:
        image: 彩色图像
        
    返回:
        灰度图像
    """
    # 检查图像是否已经是灰度图
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image
    
    # 转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image


def extract_bit_plane(image, bit_position):
    """
    提取图像的指定位平面
    
    参数:
        image: 输入图像
        bit_position: 位平面位置 (0-7，0表示最低有效位，7表示最高有效位)
        
    返回:
        指定位平面的二值图像
    """
    if bit_position < 0 or bit_position > 7:
        raise ValueError("位平面位置必须在0-7之间")
    
    # 确保图像为灰度图
    if len(image.shape) == 3:
        image = convert_to_grayscale(image)
    
    # 提取位平面
    bit_plane = (image >> bit_position) & 1
    
    # 转换为二值图像（0和255）
    bit_plane = bit_plane * 255
    
    return bit_plane.astype(np.uint8)


def combine_bit_planes(bit_planes):
    """
    将多个位平面组合成一个图像
    
    参数:
        bit_planes: 位平面列表，索引对应位平面位置（0-7）
        
    返回:
        组合后的图像
    """
    if len(bit_planes) != 8:
        raise ValueError("需要提供8个位平面")
    
    # 初始化结果图像
    result = np.zeros_like(bit_planes[0], dtype=np.uint8)
    
    # 组合位平面
    for i, plane in enumerate(bit_planes):
        # 将二值图像（0和255）转换回位值（0和1）
        bit_value = (plane > 0).astype(np.uint8)
        # 将位值左移到对应位置并添加到结果中
        result |= (bit_value << i)
    
    return result


def calculate_sobel_gradient(image):
    """
    计算图像的Sobel梯度幅值
    
    参数:
        image: 输入图像
        
    返回:
        Sobel梯度幅值图像
    """
    # 确保图像为灰度图
    if len(image.shape) == 3:
        image = convert_to_grayscale(image)
    
    # 计算x和y方向的梯度
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    # 计算梯度幅值
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # 归一化到0-255范围
    grad_magnitude = cv2.normalize(grad_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    return grad_magnitude.astype(np.uint8)


def apply_gaussian_blur(image, kernel_size=5):
    """
    对图像应用高斯模糊
    
    参数:
        image: 输入图像
        kernel_size: 高斯核大小，必须是奇数
        
    返回:
        模糊后的图像
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # 确保核大小为奇数
    
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return blurred


def add_gaussian_noise(image, mean=0, sigma=25):
    """
    向图像添加高斯噪声
    
    参数:
        image: 输入图像
        mean: 噪声的均值
        sigma: 噪声的标准差
        
    返回:
        添加噪声后的图像
    """
    # 创建与图像大小相同的高斯噪声
    noise = np.random.normal(mean, sigma, image.shape).astype(np.int16)
    
    # 添加噪声到图像
    noisy_image = image.astype(np.int16) + noise
    
    # 裁剪值到0-255范围
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    return noisy_image


def crop_image(image, x, y, width, height):
    """
    裁剪图像
    
    参数:
        image: 输入图像
        x, y: 裁剪区域左上角坐标
        width, height: 裁剪区域宽度和高度
        
    返回:
        裁剪后的图像
    """
    # 确保裁剪区域在图像范围内
    img_height, img_width = image.shape[:2]
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    width = max(1, min(width, img_width - x))
    height = max(1, min(height, img_height - y))
    
    # 裁剪图像
    cropped = image[y:y+height, x:x+width]
    return cropped


def resize_image(image, width, height, interpolation=cv2.INTER_LINEAR):
    """
    调整图像大小
    
    参数:
        image: 输入图像
        width, height: 目标宽度和高度
        interpolation: 插值方法
        
    返回:
        调整大小后的图像
    """
    resized = cv2.resize(image, (width, height), interpolation=interpolation)
    return resized


def split_color_channels(image):
    """
    分离彩色图像的颜色通道
    
    参数:
        image: 彩色图像
        
    返回:
        包含B、G、R通道的元组
    """
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("输入必须是彩色图像")
    
    # 分离通道
    b, g, r = cv2.split(image)
    return b, g, r


def merge_color_channels(b, g, r):
    """
    合并颜色通道为彩色图像
    
    参数:
        b, g, r: 蓝、绿、红通道
        
    返回:
        合并后的彩色图像
    """
    merged = cv2.merge([b, g, r])
    return merged