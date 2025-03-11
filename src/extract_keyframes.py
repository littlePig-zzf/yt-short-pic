import os
import subprocess
import sys
from pathlib import Path

# 路径
# /Users/zzf/youtube/311

def ensure_ffmpeg():
    """检查是否安装了ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        print("❌ 未检测到ffmpeg，请先安装ffmpeg")
        print("可以使用以下命令安装：")
        print("brew install ffmpeg")
        return False

def extract_keyframes(video_path, output_dir):
    """使用ffmpeg提取视频关键帧"""
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        print(f"[+] 创建目录: {output_dir}")

        # 构建ffmpeg命令
        cmd = [
            'ffmpeg',
            '-i', str(video_path),  # 输入文件
            '-vf', 'select=eq(pict_type\,I)',  # 只选择I帧（关键帧）
            '-vsync', 'vfr',  # 可变帧率
            '-frame_pts', '1',  # 在文件名中包含时间戳
            '-f', 'image2',  # 输出为图片序列
            '-qscale:v', '2',  # 高质量（1-31，1最好）
            os.path.join(output_dir, 'keyframe_%d.jpg')  # 输出文件模式
        ]

        # 运行ffmpeg命令
        print(f"[+] 开始提取关键帧...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ 提取关键帧失败: {result.stderr}")
            return 0

        # 计算提取的帧数
        frames = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
        print(f"✅ 成功提取 {frames} 个关键帧")
        return frames

    except Exception as e:
        print(f"处理视频时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def process_videos_in_folder(input_folder, output_base_folder):
    """处理指定文件夹中的所有视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    total_frames = 0
    processed_videos = 0
    
    # 获取所有视频文件
    video_files = [
        f for f in os.listdir(input_folder) 
        if any(f.lower().endswith(ext) for ext in video_extensions)
    ]
    
    if not video_files:
        print("❌ 未找到任何视频文件")
        return 0, 0

    print(f"[+] 找到 {len(video_files)} 个视频文件")
    
    for filename in video_files:
        video_path = os.path.join(input_folder, filename)
        
        # 创建输出目录（使用视频文件名）
        video_name = os.path.splitext(filename)[0]
        output_dir = os.path.join(output_base_folder, video_name)
        
        print(f"\n处理视频: {filename}")
        print(f"输出目录: {output_dir}")
        
        frames_saved = extract_keyframes(video_path, output_dir)
        total_frames += frames_saved
        processed_videos += 1
    
    return total_frames, processed_videos

if __name__ == "__main__":
    try:
        print("[*] 视频关键帧提取工具启动中...")
        
        # 检查ffmpeg是否安装
        if not ensure_ffmpeg():
            sys.exit(1)
            
        print("-" * 50)
        
        # 获取输入输出路径
        input_folder = input("[>] 请输入视频文件夹路径: ").strip('"').strip()
        output_base_folder = input("[>] 请输入帧保存文件夹路径: ").strip('"').strip()
        
        if not os.path.exists(input_folder):
            print(f"❌ 错误：输入文件夹不存在: {input_folder}")
        else:
            print(f"\n🚀 开始处理文件夹: {input_folder}")
            print(f"📂 输出基础目录: {output_base_folder}")
            
            total_frames, processed_videos = process_videos_in_folder(input_folder, output_base_folder)
            
            print(f"\n✅ 处理完成!")
            print(f"📊 处理的视频数量: {processed_videos}")
            print(f"🖼️ 总共提取的关键帧数: {total_frames}")
            
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n🔚 按回车键退出...") 