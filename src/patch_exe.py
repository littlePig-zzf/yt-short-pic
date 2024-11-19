import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
import cv2
from PIL import Image

# 设置控制台编码为 UTF-8
if sys.platform.startswith('win'):
    # Windows 系统下设置控制台编码
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# 确保 stdout 使用 utf-8 编码
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, IOError):
    # 对于不支持 reconfigure 的 Python 版本，使用其他方式设置编码
    if hasattr(sys.stdout, 'encoding'):
        if sys.stdout.encoding != 'utf-8':
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    pass

def sanitize_folder_name(name, max_length=20):
    """处理文件夹名称，只保留数字和字母"""
    # 只保留字母数字字符
    name = ''.join(c for c in name if c.isalnum())
    return name[:max_length]

def extract_frames(video_path, output_dir, interval=6):
    """从视频中每隔指定秒数提取一帧并保存"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"[+] 创建目录: {output_dir}")
        
        test_file = os.path.join(output_dir, 'test.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("[+] 输出目录可写")
        except Exception as e:
            print(f"[!] 警告：输出目录可能没有写入权限: {str(e)}")
            return 0
            
        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"❌ 错误：无法打开视频文件: {video_path}")
            return 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"📊 视频信息 - FPS: {fps}, 总帧数: {total_frames}")
        
        frame_interval = int(fps * interval)
        print(f"⏱️ 每 {interval} 秒提取一帧（间隔 {frame_interval} 帧）")
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                try:
                    # 使用简单的文件名
                    output_path = os.path.join(output_dir, f'frame_{saved_count:03d}.jpg')
                    
                    # 转换 BGR 到 RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 使用 PIL 保存图片
                    img = Image.fromarray(frame_rgb)
                    img.save(output_path, quality=95)
                    
                    if os.path.exists(output_path):
                        print(f'✅ 成功保存第 {saved_count} 帧')
                        print(f"📊 文件大小: {os.path.getsize(output_path)} 字节")
                    else:
                        print(f'❌ 保存失败: {output_path}')
                except Exception as e:
                    print(f"保存图片时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                saved_count += 1
            frame_count += 1
            
    except Exception as e:
        print(f"处理视频时出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        
    return saved_count

def process_videos_in_folder(input_folder, output_base_folder, interval=6.0, log_callback=print):
    """处理指定文件夹中的所有视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    total_frames = 0
    processed_videos = 0
    
    for filename in os.listdir(input_folder):
        if any(filename.lower().endswith(ext) for ext in video_extensions):
            video_path = os.path.join(input_folder, filename)
            
            # 使用简化的文件夹名称
            video_name = os.path.splitext(filename)[0]
            safe_video_name = sanitize_folder_name(video_name)
            output_dir = os.path.join(output_base_folder, safe_video_name)
            
            log_callback(f"\n处理视频: {filename}")
            log_callback(f"输出目录: {output_dir}")
            
            # 传递间隔参数
            frames_saved = extract_frames(video_path, output_dir, interval)
            total_frames += frames_saved
            processed_videos += 1
    
    return total_frames, processed_videos

class VideoFrameExtractor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("视频帧提取工具")
        self.window.geometry("600x400")
        
        # 创建输入控件
        self.create_widgets()
        
    def create_widgets(self):
        # 输入文件夹选择
        tk.Label(self.window, text="视频文件夹路径:").pack(pady=5)
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(fill=tk.X, padx=20)
        self.input_path = tk.Entry(self.input_frame)
        self.input_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self.input_frame, text="浏览", command=self.select_input).pack(side=tk.RIGHT, padx=5)
        
        # 输出文件夹选择
        tk.Label(self.window, text="帧保存文件夹路径:").pack(pady=5)
        self.output_frame = tk.Frame(self.window)
        self.output_frame.pack(fill=tk.X, padx=20)
        self.output_path = tk.Entry(self.output_frame)
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self.output_frame, text="浏览", command=self.select_output).pack(side=tk.RIGHT, padx=5)
        
        # 间隔设置
        tk.Label(self.window, text="截图间隔(秒):").pack(pady=5)
        self.interval = tk.Entry(self.window)
        self.interval.insert(0, "6.0")
        self.interval.pack()
        
        # 处理按钮
        tk.Button(self.window, text="开始处理", command=self.start_process).pack(pady=20)
        
        # 日志显示
        self.log_text = tk.Text(self.window, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    def select_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, folder)
            
    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update()
        
    def start_process(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()
        
        try:
            interval = float(self.interval.get())
            if interval <= 0:
                messagebox.showerror("错误", "间隔时间必须大于0秒")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        if not os.path.exists(input_folder):
            messagebox.showerror("错误", f"输入文件夹不存在: {input_folder}")
            return
            
        self.log("开始处理视频...")
        total_frames, processed_videos = process_videos_in_folder(input_folder, output_folder, interval)
        self.log(f"\n处理完成!\n处理的视频数量: {processed_videos}\n总共保存的帧数: {total_frames}")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    # 修改主程序入口
    app = VideoFrameExtractor()
    app.run()