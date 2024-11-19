import os
import sys

def setup_tcl():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        tcl_path = os.path.join(base_dir, 'tcl8.6')
        tk_path = os.path.join(base_dir, 'tk8.6')
        os.environ['TCL_LIBRARY'] = tcl_path
        os.environ['TK_LIBRARY'] = tk_path
        print(f"TCL_LIBRARY set to: {tcl_path}")
        print(f"TK_LIBRARY set to: {tk_path}")

setup_tcl()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import os
from pathlib import Path
from patch import extract_frames, sanitize_folder_name

class VideoFrameExtractor(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("视频帧提取工具")
        self.geometry("600x400")
        
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入文件夹选择
        ttk.Label(main_frame, text="视频文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.select_input_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # 输出文件夹选择
        ttk.Label(main_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.select_output_folder).grid(row=1, column=2, padx=5, pady=5)
        
        # 时间间隔设置
        ttk.Label(main_frame, text="截取间隔(秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.interval = tk.StringVar(value="6")
        ttk.Entry(main_frame, textvariable=self.interval, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 开始按钮
        ttk.Button(main_frame, text="开始处理", command=self.start_processing).grid(row=3, column=0, columnspan=3, pady=20)
        
        # 进度显示
        self.progress_var = tk.StringVar(value="准备就绪")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, pady=5)
        
        # 日志显示
        self.log_text = tk.Text(main_frame, height=10, width=60)
        self.log_text.grid(row=6, column=0, columnspan=3, pady=5)
        
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="选择视频所在文件夹")
        if folder:
            self.input_path.set(folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_path.set(folder)
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()
        
    def start_processing(self):
        # 验证输入
        input_folder = self.input_path.get().strip()
        output_folder = self.output_path.get().strip()
        
        try:
            interval = float(self.interval.get())
            if interval <= 0:
                raise ValueError("间隔必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的时间间隔")
            return
            
        if not os.path.exists(input_folder):
            messagebox.showerror("错误", "输入文件夹不存在")
            return
            
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 开始处理
        try:
            # 支持的视频格式
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
            
            # 确保输出文件夹存在
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            # 获取视频文件列表
            video_files = [f for f in os.listdir(input_folder) 
                         if any(f.lower().endswith(ext) for ext in video_extensions)]
            
            if not video_files:
                self.log("未找到视频文件")
                return
                
            # 设置进度条
            self.progress["maximum"] = len(video_files)
            self.progress["value"] = 0
            
            # 处理每个视频
            total_frames = 0
            for i, filename in enumerate(video_files, 1):
                video_path = os.path.join(input_folder, filename)
                video_name = os.path.splitext(filename)[0]
                safe_video_name = sanitize_folder_name(video_name)
                output_dir = os.path.join(output_folder, safe_video_name)
                
                self.progress_var.set(f"正在处理: {filename}")
                self.log(f"\n处理视频 ({i}/{len(video_files)}): {filename}")
                
                frames_saved = extract_frames(video_path, output_dir, interval)
                total_frames += frames_saved
                
                self.progress["value"] = i
                
            self.progress_var.set("处理完成!")
            self.log(f"\n批量处理完成!")
            self.log(f"处理的视频数量: {len(video_files)}")
            self.log(f"总共保存的帧数: {total_frames}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
            self.log(f"错误: {str(e)}")

if __name__ == "__main__":
    app = VideoFrameExtractor()
    app.mainloop() 