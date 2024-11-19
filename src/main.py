import wxauto
import time
import win32gui
import win32con
import pyperclip

def click_and_wait(wx, x, y, wait_time=1):
    """点击指定坐标并等待"""
    wx.ClickOnWindow(x, y)
    time.sleep(wait_time)

def add_tag(wx, tag_name="仅三天可见"):
    """添加标签"""
    # 点击右键菜单
    wx.ClickOnWindow(200, 100, right_click=True)
    time.sleep(0.5)
    
    # 点击"标签"选项
    wx.ClickOnWindow(250, 280)
    time.sleep(0.5)
    
    # 点击"新建标签"
    wx.ClickOnWindow(250, 400)
    time.sleep(0.5)
    
    # 输入标签名
    pyperclip.copy(tag_name)
    wx.SendKeys('^v')  # Ctrl+V
    time.sleep(0.5)
    
    # 点击确定
    wx.ClickOnWindow(400, 400)
    time.sleep(0.5)

try:
    # 连接到已经登录的微信
    wx = wxauto.WeChat()
    print("初始化成功")
    time.sleep(2)
    
    # 获取好友列表
    friends = wx.GetAllFriends()
    print(f"获取到 {len(friends)} 个好友")
    
    # 遍历好友列表
    for friend_data in friends:
        try:
            # 获取好友昵称，优先使用备注名
            friend_name = friend_data['remark'] if friend_data['remark'] else friend_data['nickname']
            print(f"\n正在检查好友: {friend_name}")
            
            # 点击联系人
            wx.ChatWith(friend_name)
            time.sleep(1)
            
            # 点击右上角菜单
            click_and_wait(wx, 880, 30)
            
            # 点击朋友圈按钮
            click_and_wait(wx, 780, 160, 2)
            
            # 获取当前窗口的文本
            moments_text = wx.GetWindowText()
            
            # 检查是否仅三天可见
            if "仅三天可见" in moments_text:
                print(f"{friend_name} 开启了仅三天可见")
                
                # 返回聊天界面
                win32gui.PostMessage(wx.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
                time.sleep(1)
                
                # 检查现有标签
                current_tags = friend_data['tags'] or []
                if "仅三天可见" not in current_tags:
                    print(f"正在为 {friend_name} 添加标签")
                    add_tag(wx)
                    print(f"已为 {friend_name} 添加标签")
                else:
                    print(f"{friend_name} 已有相关标签")
            else:
                print(f"{friend_name} 朋友圈正常可见")
                # 返回聊天界面
                win32gui.PostMessage(wx.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
                time.sleep(1)
            
        except Exception as e:
            print(f"处理 {friend_name} 时出错: {str(e)}")
            continue
    
    print("\n处理完成")

except Exception as e:
    print(f"发生错误: {str(e)}")