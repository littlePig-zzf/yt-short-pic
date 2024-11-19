import cv2
import os
import time

def extract_frames(video_path, output_dir, interval=6):
    """
    从视频中每隔指定秒数提取一帧并保存
    
    参数:
        video_path: 视频文件路径
        output_dir: 输出目录路径
        interval: 提取帧的时间间隔(秒)
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"错误：无法打开视频文件: {video_path}")
        return
    
    # 获取视频的FPS(每秒帧数)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"视频FPS: {fps}")
    
    # 计算需要跳过的帧数
    frame_interval = int(fps * interval)
    print(f"每 {interval} 秒提取一帧（间隔 {frame_interval} 帧）")
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
            
        # 每隔指定帧数保存一帧
        if frame_count % frame_interval == 0:
            # 生成输出文件名
            output_path = os.path.join(output_dir, f'frame_{saved_count}.jpg')
            # 保存帧
            cv2.imwrite(output_path, frame)
            print(f'已保存第 {saved_count} 帧到: {output_path}')
            saved_count += 1
            
        frame_count += 1
    
    # 释放资源
    cap.release()
    print(f'完成! 共保存了 {saved_count} 帧')
    return saved_count

def sanitize_folder_name(name, max_length=50):
    """
    处理文件夹名称，确保不会过长且移除首尾空格
    
    参数:
        name: 原始文件夹名称
        max_length: 最大允许长度
    返回:
        处理后的文件夹名称
    """
    # 移除首尾空格
    name = name.strip()
    
    if len(name) <= max_length:
        return name
    
    # 如果文件名过长，保留前max_length个字符并再次移除尾部空格
    return name[:max_length].strip()

def process_videos_in_folder(input_folder, output_base_folder):
    """
    处理指定文件夹中的所有视频文件
    
    参数:
        input_folder: 输入视频文件夹路径
        output_base_folder: 输出基础文件夹路径
    """
    # 支持的视频格式
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    
    # 确保输出基础文件夹存在
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)
    
    # 获取所有视频文件
    total_frames = 0
    processed_videos = 0
    
    for filename in os.listdir(input_folder):
        # 检查文件扩展名
        if any(filename.lower().endswith(ext) for ext in video_extensions):
            # 获取视频文件的完整路径
            video_path = os.path.join(input_folder, filename)
            
            # 处理视频文件名，确保文件夹名称不会过长且没有多余空格
            video_name = os.path.splitext(filename)[0]
            safe_video_name = sanitize_folder_name(video_name)
            output_dir = os.path.join(output_base_folder, safe_video_name)
            
            print(f"\n处理视频: {filename}")
            print(f"输出目录: {output_dir}")
            
            # 处理视频
            frames_saved = extract_frames(video_path, output_dir)
            total_frames += frames_saved
            processed_videos += 1
    
    print(f"\n批量处理完成!")
    print(f"处理的视频数量: {processed_videos}")
    print(f"总共保存的帧数: {total_frames}")

# 使用示例
if __name__ == "__main__":
    # 指定输入视频文件夹和输出基础文件夹
    input_folder = r'D:\CRVideoMate Output\开头1'  # 替换为您的视频文件夹路径
    output_base_folder = r'D:\wx_moments_checker\frames'  # 替换为您想要的输出路径
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误：输入文件夹不存在: {input_folder}")
    else:
        print(f"开始处理文件夹: {input_folder}")
        print(f"输出基础目录: {output_base_folder}")
        process_videos_in_folder(input_folder, output_base_folder)