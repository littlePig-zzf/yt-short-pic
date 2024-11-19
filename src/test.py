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

# 使用示例
video_path = r'D:\CRVideoMate Output\开头\1.mp4'  # 使用原始字符串
output_dir = 'frames'  # 输出目录名

# 检查视频文件是否存在
if not os.path.exists(video_path):
    print(f"错误：视频文件不存在: {video_path}")
else:
    print(f"开始处理视频: {video_path}")
    extract_frames(video_path, output_dir)
