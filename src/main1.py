import wxauto
import json
import time
import win32gui
import win32con
import pyperclip

try:
    # 连接到已经登录的微信（确保微信已经登录）
    wx = wxauto.WeChat()
    
    # 等待一下确保微信窗口被正确识别
    time.sleep(2)
    
    # 点击通讯录按钮
    # wx.GetWxContact()
    # time.sleep(1)
    
    # 获取所有好友列表
    friends = wx.GetAllFriends()
    print("获取到的好友列表:", friends)
    
    # 存储好友信息的字典
    friend_info = {}
    
    # 遍历会话列表
    for friend_data in friends:
        try:
            # 获取好友昵称，优先使用备注名
            friend_name = friend_data['remark'] if friend_data['remark'] else friend_data['nickname']
            print(f"正在检查好友: {friend_name}")
            
            # 点击联系人
            wx.ChatWith(friend_name)
            time.sleep(1)
            
            # 点击右上角菜单（使用相对坐标）
            wx.ClickOnWindow(880, 30)
            time.sleep(1)
            
            # 点击朋友圈按钮
            wx.ClickOnWindow(780, 160) 
            time.sleep(2)
            
            # 获取当前窗口的文本
            moments_text = wx.GetWindowText()
            
            # 准备标签列表
            tags_list = friend_data['tags'] if friend_data['tags'] else []
            
            if "仅三天可见" in moments_text:
                # 如果是仅三天可见，添加到标签列表
                if "仅三天可见" not in tags_list:
                    tags_list.append("仅三天可见")
                
                friend_info[friend_name] = {
                    "昵称": friend_data['nickname'],
                    "备注": friend_data['remark'],
                    "朋友圈状态": "仅三天可见",
                    "原始标签": friend_data['tags'],
                    "当前标签": tags_list
                }
            else:
                friend_info[friend_name] = {
                    "昵称": friend_data['nickname'],
                    "备注": friend_data['remark'],
                    "朋友圈状态": "正常可见",
                    "原始标签": friend_data['tags'],
                    "当前标签": tags_list
                }
                
            # 按ESC返回
            win32gui.PostMessage(wx.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
            time.sleep(1)
            
        except Exception as e:
            print(f"处理 {friend_name} 时出错: {str(e)}")
            friend_info[friend_name] = {
                "昵称": friend_data['nickname'],
                "备注": friend_data['remark'],
                "朋友圈状态": "检查失败",
                "原始标签": friend_data['tags'],
                "当前标签": friend_data['tags'] if friend_data['tags'] else []
            }
    
    # 保存结果
    with open('friend_info.json', 'w', encoding='utf-8') as f:
        json.dump(friend_info, f, ensure_ascii=False, indent=4)
    
    print("检查完成，结果已保存到 friend_info.json")

except Exception as e:
    print(f"发生错误: {str(e)}")
