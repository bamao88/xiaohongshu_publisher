import os
import time
import json
import traceback
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

from xhs.liulanqi import get_driver


def xiaohongshu_login(driver):

    cookies_file = "cookies/xiaohongshu.json"
    """小红书登录函数"""
    print("开始加载cookie")
    with open(cookies_file) as f:
        cookies = json.loads(f.read())
        driver.get("https://creator.xiaohongshu.com/creator/post")
        driver.implicitly_wait(10)
        driver.delete_all_cookies()
        time.sleep(2)
        # 遍历并添加cookie
        print("加载cookie")
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie["expiry"]
            driver.add_cookie(cookie)
        time.sleep(2)
        # 刷新
        print("开始刷新")
        driver.refresh()
        driver.get("https://creator.xiaohongshu.com/publish/publish")
        time.sleep(2)


def _find_first(driver, selectors, timeout=30):
    """Return the first element found by trying selectors in order.
    selectors: list of (By, value)
    Fails fast if none appear within timeout.
    """
    def _probe(d):
        for by, val in selectors:
            els = d.find_elements(by, val)
            if els:
                return els[0]
        return False

    return WebDriverWait(driver, timeout).until(_probe)


def click_publish_tab(driver, tab_name="上传图文", timeout=15):
    """点击发布 Tab（图文/视频）

    Args:
        driver: WebDriver实例
        tab_name: Tab名称，"上传图文" 或 "上传视频"
        timeout: 超时时间（秒）
    """
    # 等待上传内容区域可见
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.upload-content"))
    )

    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            # 查找所有 Tab
            tabs = driver.find_elements(By.CSS_SELECTOR, "div.creator-tab")

            for tab in tabs:
                # 检查是否可见
                if not tab.is_displayed():
                    continue

                # 检查文本是否匹配
                if tab.text.strip() == tab_name:
                    # 尝试移除可能的遮挡物
                    try:
                        driver.execute_script("""
                            var popovers = document.querySelectorAll('div.d-popover');
                            popovers.forEach(function(el) { el.remove(); });
                        """)
                        time.sleep(0.3)
                    except:
                        pass

                    # 点击 Tab
                    try:
                        tab.click()
                        print(f"已点击 {tab_name} Tab")
                        time.sleep(1)
                        return True
                    except:
                        # 如果普通点击失败，使用 JavaScript 点击
                        driver.execute_script("arguments[0].click();", tab)
                        print(f"已通过 JS 点击 {tab_name} Tab")
                        time.sleep(1)
                        return True

            time.sleep(0.2)
        except Exception as e:
            print(f"查找 Tab 时出错: {e}")
            time.sleep(0.2)

    raise Exception(f"未找到 {tab_name} Tab")


def upload_images(driver, image_paths, timeout=60):
    """上传多张图片

    Args:
        driver: WebDriver实例
        image_paths: 图片路径列表（绝对路径）
        timeout: 超时时间（秒）
    """
    # 验证文件路径
    valid_paths = []
    for path in image_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            valid_paths.append(abs_path)
            print(f"有效图片: {abs_path}")
        else:
            print(f"图片不存在: {abs_path}")

    if not valid_paths:
        raise Exception("没有有效的图片路径")

    # 查找上传输入框
    try:
        # 优先使用 .upload-input
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-input"))
        )
        print("使用 .upload-input 选择器")
    except:
        # 回退到 input[type="file"]
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )
        print("使用 input[type='file'] 选择器")

    # 一次性上传所有图片
    upload_input.send_keys("\n".join(valid_paths))
    print(f"已上传 {len(valid_paths)} 张图片")

    # 等待上传完成
    wait_for_images_uploaded(driver, len(valid_paths), timeout)


def wait_for_images_uploaded(driver, expected_count, timeout=60):
    """等待图片上传完成

    Args:
        driver: WebDriver实例
        expected_count: 期望的图片数量
        timeout: 超时时间（秒）
    """
    start_time = time.time()
    check_interval = 0.5

    print(f"等待 {expected_count} 张图片上传完成...")

    while time.time() - start_time < timeout:
        try:
            # 检查已上传的图片
            uploaded_images = driver.find_elements(
                By.CSS_SELECTOR,
                ".img-preview-area .pr"
            )

            current_count = len(uploaded_images)
            if current_count > 0:
                print(f"已上传 {current_count}/{expected_count} 张图片")

            if current_count >= expected_count:
                print("所有图片上传完成！")
                return True
        except Exception as e:
            pass

        time.sleep(check_interval)

    raise Exception(f"图片上传超时（{timeout}秒）")


def input_tags_improved(driver, content_elem, tags):
    """改进的标签输入（模拟参考仓库的逻辑）

    Args:
        driver: WebDriver实例
        content_elem: 内容编辑器元素
        tags: 标签列表
    """
    if not tags:
        return

    time.sleep(1)

    # 移动到内容末尾
    for _ in range(20):
        content_elem.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.01)

    # 换行准备输入标签
    content_elem.send_keys(Keys.ENTER)
    content_elem.send_keys(Keys.ENTER)
    time.sleep(1)

    # 逐个输入标签
    for tag in tags:
        tag = tag.lstrip("#")

        # 输入 # 号
        content_elem.send_keys("#")
        time.sleep(0.2)

        # 逐字符输入标签
        for char in tag:
            content_elem.send_keys(char)
            time.sleep(0.05)

        time.sleep(1)

        # 尝试点击联想选项
        try:
            topic_container = driver.find_element(
                By.CSS_SELECTOR,
                "#creator-editor-topic-container"
            )
            first_item = topic_container.find_element(By.CSS_SELECTOR, ".item")
            first_item.click()
            print(f"已选择标签联想: {tag}")
            time.sleep(0.2)
        except:
            # 如果没有联想选项，输入空格
            content_elem.send_keys(" ")
            print(f"直接输入标签: {tag}")

        time.sleep(0.5)


def publish_xiaohongshu_image(driver, scripts, publish_time="2025-01-12 16:00", image_paths=None):
    """发布小红书图文笔记

    Args:
        driver: WebDriver实例
        scripts: 包含笔记信息的字典
        publish_time: 发布时间
        image_paths: 图片路径列表（1-9张）
    """
    if not image_paths or len(image_paths) == 0:
        raise ValueError("图片路径不能为空")
    if len(image_paths) > 9:
        raise ValueError("最多支持9张图片")

    time.sleep(3)

    # 1. 点击"上传图文" Tab
    click_publish_tab(driver, "上传图文")

    # 2. 上传图片
    upload_images(driver, image_paths)

    # 3. 填写标题（使用参考仓库的选择器）
    content = scripts["content"]
    title_text = content.get("title")

    # 尝试使用 div.d-input input 选择器
    try:
        title_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.d-input input"))
        )
    except:
        # 回退到原来的选择器
        title_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="填写标题会有更多赞哦～"]'))
        )

    title_input.clear()
    driver.execute_script("arguments[0].value = arguments[1];", title_input, title_text)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", title_input)

    time.sleep(1)

    # 4. 填写正文
    content_elem = _find_first(
        driver,
        [
            (By.CSS_SELECTOR, 'div.ql-editor'),
            (By.CSS_SELECTOR, 'div[contenteditable="true"]'),
            (By.XPATH, '//div[@contenteditable="true"]')
        ],
    )
    info = content["script"]
    driver.execute_script("arguments[0].innerText = arguments[1];", content_elem, info)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", content_elem)

    time.sleep(1)

    # 5. 输入标签（使用改进版本）
    tags = scripts.get("tags", [])
    input_tags_improved(driver, content_elem, tags)

    # 6. 定时发布
    schedule_button = driver.find_element(
        By.XPATH,
        '//span[contains(@class, "el-radio__label") and text()="定时发布"]'
    )
    time.sleep(2)
    print("点击定时发布")
    driver.execute_script("arguments[0].click();", schedule_button)

    time.sleep(5)

    # 找到时间输入框并输入时间
    input_time = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="选择日期和时间"]'))
    )
    driver.execute_script('arguments[0].removeAttribute("readonly");', input_time)
    input_time.clear()
    input_time.send_keys(Keys.CONTROL, 'a')
    input_time.send_keys(Keys.DELETE)
    time.sleep(0.5)
    input_time.send_keys(publish_time)
    input_time.send_keys(Keys.TAB)
    time.sleep(1)

    # 7. 点击发布按钮（图文）
    # 尝试使用参考仓库的选择器
    try:
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.submit div.d-button-content"
            ))
        )
    except:
        # 回退到原来的选择器
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//span[contains(@class, "d-text") and text()="定时发布"]'
            ))
        )

    submit_button.click()
    print("已点击发布按钮")
    time.sleep(3)

    print("图文笔记发布完成！")


def publish_xiaohongshu(driver, scripts, publish_time="2025-01-12 16:00", video_path="output/video.mp4"):
    """发布小红书视频函数
    Args:
        driver: WebDriver实例
        scripts: 包含视频信息的字典
        publish_time: 发布时间
        video_path: 视频文件路径
    """
    time.sleep(3)

    # 1. 点击"上传视频" Tab
    click_publish_tab(driver, "上传视频")

    video_path = os.path.abspath(video_path)
    print("开始上传文件", video_path)
    time.sleep(3)
    # ### 上传视频
    video = driver.find_element("xpath", '//input[@type="file"]')
    video.send_keys(video_path)

    # 填写标题（最多20个字符）- 使用JavaScript避免emoji问题
    content = scripts["content"]
    title_text = content.get("title")
    title_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@placeholder="填写标题会有更多赞哦～"]'))
    )
    title_input.clear()
    # 使用JavaScript设置值，避免ChromeDriver的emoji限制
    driver.execute_script("arguments[0].value = arguments[1];", title_input, title_text)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", title_input)

    time.sleep(1)
    # 填写描述（兼容新版编辑器）
    content_clink = _find_first(
        driver,
        [
            (By.CSS_SELECTOR, 'div.ql-editor[data-placeholder="输入正文描述，真诚有价值的分享予人温暖"]'),
            (By.CSS_SELECTOR, 'div[contenteditable="true"]'),
            (By.XPATH, '//div[@contenteditable="true"]')
        ],
    )
    info = content["script"]
    print(info)
    # 使用JavaScript设置内容，避免emoji问题
    driver.execute_script("arguments[0].innerText = arguments[1];", content_clink, info)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", content_clink) 
    
    time.sleep(3)
    # 标签 - 每个标签单独一行
    for tag in scripts.get("tags", []):
        tag = "#" + tag
        # 保证焦点在编辑器内
        content_clink.click()
        # 先换行，再输入标签
        content_clink.send_keys(Keys.ENTER)
        time.sleep(0.2)
        content_clink.send_keys(tag)
        time.sleep(1)

        # 按回车确认标签（触发联想选择）
        content_clink.send_keys(Keys.ENTER)
        time.sleep(0.3)

    # 定时发布按钮定位
    schedule_button = driver.find_element(
        By.XPATH, 
        '//span[contains(@class, "el-radio__label") and text()="定时发布"]'
    )
    time.sleep(2)
    print("点击定时发布")
    # 使用 JavaScript 执行点击，而不是直接点击
    driver.execute_script("arguments[0].click();", schedule_button)

    time.sleep(5)
    # 找到时间输入框并输入时间
    input_time = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="选择日期和时间"]'))
    )
    # 解除只读并填写时间
    driver.execute_script('arguments[0].removeAttribute("readonly");', input_time)
    input_time.clear()
    input_time.send_keys(Keys.CONTROL, 'a')
    input_time.send_keys(Keys.DELETE)
    time.sleep(0.5)
    input_time.send_keys(publish_time)
    input_time.send_keys(Keys.TAB)
    time.sleep(1)

    # 等待发布按钮变为可点击状态
    publish_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((
            By.XPATH,
            '//span[contains(@class, "d-text") and text()="定时发布"]'
        ))
    )
    # 滚动到按钮位置并使用JavaScript点击，避免被其他元素遮挡
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", publish_button)
    time.sleep(0.5)
    try:
        publish_button.click()
    except Exception:
        # 如果普通点击失败，使用JavaScript点击
        driver.execute_script("arguments[0].click();", publish_button)
    print("已点击定时发布按钮")
    time.sleep(3)  # 等待发布完成

    print("视频发布完成！")

def publish_xhs_content(scripts_data, publish_time=None, media_paths=None, content_type="video"):
    """Publish content to XHS programmatically.

    Args:
        scripts_data (dict): Content data with name, tags, content, etc.
        publish_time (str, optional): Publish time in format "2025-01-12 16:00"
        media_paths (list or str, optional): Path(s) to media file(s)
            - For video: single path string or list with one element
            - For images: list of 1-9 image paths
        content_type (str): Content type, "video" or "image"

    Returns:
        bool: True if successful, False otherwise
    """
    driver = None
    try:
        driver = get_driver()
        xiaohongshu_login(driver=driver)
        print("登录成功")

        print("Content data:", scripts_data)
        print("Content type:", content_type)

        # 处理 media_paths 参数
        if media_paths is None:
            media_paths = ["output/video.mp4"] if content_type == "video" else []
        elif isinstance(media_paths, str):
            media_paths = [media_paths]

        # 根据类型调用不同的发布函数
        if content_type == "image":
            if not media_paths:
                raise ValueError("图文发布需要提供图片路径")
            publish_xiaohongshu_image(driver, scripts_data, publish_time, media_paths)
        elif content_type == "video":
            if not media_paths:
                raise ValueError("视频发布需要提供视频路径")
            publish_xiaohongshu(driver, scripts_data, publish_time, media_paths[0])
        else:
            raise ValueError(f"不支持的内容类型: {content_type}")

        return True

    except Exception as e:
        print(f"发布失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()  # 退出浏览器


def main():
    # 检查是否提供了发布时间参数
    if len(sys.argv) != 2:
        print("使用方法: python publish.py '2025-01-12 16:00'")
        sys.exit(1)
    
    publish_time = sys.argv[1]
    print(publish_time)

    try:
        with open("output/script.json", "r", encoding="utf-8") as f:
            scripts = json.load(f)
        
        success = publish_xhs_content(scripts, publish_time)
        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()