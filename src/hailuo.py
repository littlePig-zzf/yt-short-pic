import asyncio
import logging
import traceback
from typing import Optional
from playwright.async_api import Page, async_playwright, Browser, Playwright
import os
import shutil

# 常量配置
CONFIG = {
    'BASE_URL': "https://hailuoai.video/",
    'TIMEOUTS': {
        'VIDEO': 300,
        'PAGE': 36000,
        'NETWORK': 30000
    },
    'WAITS': {
        'INTERVAL': 2,
        'IMAGE_UPLOAD': 15
    }
}

class HailuoClient:
    """海螺视频客户端"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.page = self.browser = self.playwright = None
        self.video_id = None
        self.video_generated_event = asyncio.Event()

    async def initialize(self, browser_ws: str) -> None:
        """初始化浏览器连接"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.connect_over_cdp(browser_ws, timeout=CONFIG['TIMEOUTS']['NETWORK'])
            self.page = await self.browser.contexts[0].new_page()
            self.logger.info("浏览器和页面已成功初始化")
            await self._setup_network_listener()
        except Exception as e:
            await self.close()
            raise Exception(f"初始化失败: {str(e)}")

    async def _setup_network_listener(self):
        """设置网络监听"""
        async def on_response(response):
            try:
                if "generate/video" in response.url:
                    data = await response.json()
                    if video_id := data.get('data', {}).get('id'):
                        self.video_id = video_id
                        self.video_generated_event.set()
            except Exception:
                pass
        self.page.on("response", on_response)
        
    async def check_quota(self) -> bool:
        """检查额度是否足够"""
        try:
            # 查找特定元素
            element_40 = await self.page.wait_for_selector('span.select-none.font-light')
            if element_40:
                content = await element_40.text_content()
                # 输出调试信息
                print(f"Quota content: {content}")
                return int(content) > 30  # 返回True表示额度足够
        except Exception as e:
            # 输出异常信息
            print(f"Error checking quota: {e}")
        return False  # 默认返回False表示额度不足

    async def check_queue_status(self) -> bool:
        """检查队列状态"""
        try:
            # 查找包含“Video generation is in progress”或“expected to wait for” 或“Queuing”文本的元素
            elements_video = await self.page.query_selector_all('//*[contains(text(),"Video generation is in progress")]')
            elements_wait = await self.page.query_selector_all('//*[contains(text(),"expected to wait for")]')
            elements_queuing = await self.page.query_selector_all('//*[contains(text(),"Queuing")]')
            
            # 获取出现次数
            count_video = len(elements_video)
            count_wait = len(elements_wait)
            count_queuing = len(elements_queuing)
            
            # 判断出现次数是否等于3
            return (count_video + count_wait+count_queuing) < 3
        except Exception:
            return True

    async def generate_video(self, prompt: str, image_path: Optional[str] = None) -> None:
        """生成视频"""

        if prompt == 'NO_PROMPT':
            return

        if not await self.check_quota():
            return

        if not await self.check_queue_status():
            return

        # 输入提示词和上传图片
        await (await self.page.wait_for_selector('textarea.ant-input.css-o72qen')).fill(prompt)
        if image_path:
            if os.path.isfile(image_path):
                await self._upload_image(image_path)
            else:
                self.logger.error(f"无效的图片路径: {image_path}")
                return

        # 等待图片上传完成
        await self.wait_for_image_upload_to_complete()

        # 点击生成按钮
        await (await self.page.wait_for_selector('div.create-btn-container div.create-btn')).click()

        # 等待视频生成事件完成
        try:
            await asyncio.wait_for(self.video_generated_event.wait(), timeout=CONFIG['TIMEOUTS']['VIDEO'])
            self.video_generated_event.clear()  # 清除事件以便下次使用
        except asyncio.TimeoutError:
            self.logger.error("视频生成超时")

    async def wait_for_image_upload_to_complete(self):
        """等待图片上传完成"""
        try:
            # 等待加载指示器消失
            await self.page.wait_for_selector('img[alt="hai luo ai video light loading"]', state='hidden', timeout=CONFIG['TIMEOUTS']['PAGE'])
            
            # 延迟2秒(避免出现图片没有上传到的情况)
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"等待图片上传完成时出错: {e}")

    async def _upload_image(self, image_path: str) -> None:
        """上传图片"""
        await (await self.page.wait_for_selector('div.relative.cursor-pointer.group')).click()
        await asyncio.sleep(CONFIG['WAITS']['INTERVAL'])

        upload_btn = await self.page.wait_for_selector('div.ant-upload.ant-upload-select')
        async with self.page.expect_file_chooser() as fc:
            await upload_btn.click()
            await (await fc.value).set_files(image_path)
        await asyncio.sleep(CONFIG['WAITS']['IMAGE_UPLOAD'])

    async def close(self) -> None:
        """关闭资源"""
        for resource in [self.page, self.browser, self.playwright]:
            if resource:
                try:
                    await resource.close()
                except Exception:
                    pass
        self.page = self.browser = self.playwright = None

async def process_images_in_folder(ws_address: str, prompt: str, folder_path: str) -> None:
    """处理文件夹内的所有图片生成视频"""
    client = HailuoClient()
    processed_folder = os.path.join(folder_path, "processed")
    
    # 创建已处理图片的文件夹
    os.makedirs(processed_folder, exist_ok=True)
    
    try:
        await client.initialize(ws_address)
        
        # 打开网站
        await client.page.goto(CONFIG['BASE_URL'], timeout=CONFIG['TIMEOUTS']['PAGE'])
        client.logger.info("页面已加载")
        await asyncio.sleep(CONFIG['WAITS']['INTERVAL'])
        
        # 获取文件夹内的所有图片
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        for image_path in image_files:
            # 检查可用额度
            if not await client.check_quota():
                print("没有可用额度了，退出循环")
                break
            
            # 检查队列状态
            while not await client.check_queue_status():
                print("队列满了，等待中...")
                await asyncio.sleep(CONFIG['WAITS']['INTERVAL'])
            
            # 生成视频
            await client.generate_video(prompt, image_path)
            print(f"已处理图片: {image_path}")
            
            # 移动已处理的图片到processed文件夹
            shutil.move(image_path, processed_folder)
        
        print("所有图片处理完成")
    except Exception as e:
        logging.error(f"处理失败: {e}")
    finally:
        await client.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    ws_address = "ws://127.0.0.1:9222/devtools/browser/5af01ed7-72a3-4912-8aa9-7ad120f08ebc"
    prompt = "街道上, 小女孩在走秀的场景, 镜头保持跟拍小女孩走秀的过程, 小女孩走秀的感觉就像一个专业的模特."
    folder_path = "/Users/zzf/Downloads/output/"
    asyncio.run(process_images_in_folder(ws_address, prompt, folder_path))
  