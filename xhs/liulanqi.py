# Copied from
# https://github.com/menhuan/notes/blob/master/python/douyin/upload_xiaohongshu.py

import datetime
from operator import index
import traceback
from selenium import webdriver

from time import sleep

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium
from selenium import webdriver
import pathlib
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import json
import os
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
import sys



def get_driver():
    """
    创建WebDriver实例

    策略优先级:
    1. 系统标准Chrome + undetected-chromedriver (推荐，避免被检测)
    2. Chrome for Testing + undetected-chromedriver (备选)
    3. 标准Selenium ChromeDriver (fallback)
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    import subprocess
    import platform
    import os

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    home_dir = os.path.expanduser("~")

    # 清除代理环境变量，避免干扰浏览器启动
    for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
        os.environ.pop(proxy_var, None)

    # 系统标准 Chrome 路径
    system_chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    # Selenium 缓存的 chromedriver 路径
    cached_chromedriver = os.path.expanduser("~/.cache/selenium/chromedriver/mac-arm64/142.0.7444.175/chromedriver")

    # 策略1: 使用系统标准Chrome + undetected-chromedriver (推荐)
    try:
        if platform.system() == 'Darwin' and os.path.exists(system_chrome_path):
            chrome_version = subprocess.check_output([system_chrome_path, '--version']).decode().strip()
            print(f"检测到系统Chrome: {chrome_version}")

            import undetected_chromedriver as uc
            print("尝试使用undetected-chromedriver + 系统标准Chrome...")

            options = uc.ChromeOptions()
            options.binary_location = system_chrome_path  # 明确指定标准 Chrome 路径
            options.add_argument('--no-proxy-server')  # 禁用代理

            # 如果有缓存的 chromedriver，使用它避免网络下载
            driver_path = cached_chromedriver if os.path.exists(cached_chromedriver) else None
            driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                driver_executable_path=driver_path
            )

            print("✅ 系统标准Chrome启动成功")
            driver.maximize_window()
            print("开始运行浏览器")
            return driver

    except Exception as uc_error:
        print(f"系统Chrome启动失败: {str(uc_error)[:200]}")
        print("尝试Chrome for Testing...")

    # Chrome for Testing路径 (备选)
    cft_chrome_path = os.path.join(home_dir, "chrome-for-testing", "latest-chrome",
                                    "Google Chrome for Testing.app", "Contents", "MacOS",
                                    "Google Chrome for Testing")
    cft_chromedriver_path = os.path.join(home_dir, "chrome-for-testing", "latest-chromedriver", "chromedriver")

    # 策略2: 使用Chrome for Testing (备选)
    if os.path.exists(cft_chrome_path) and os.path.exists(cft_chromedriver_path):
        try:
            # 获取版本信息
            chrome_version = subprocess.check_output([cft_chrome_path, '--version']).decode().strip()
            driver_version = subprocess.check_output([cft_chromedriver_path, '--version']).decode().strip()
            print(f"检测到Chrome for Testing: {chrome_version}")
            print(f"检测到ChromeDriver: {driver_version}")

            import undetected_chromedriver as uc
            print("尝试使用undetected-chromedriver + Chrome for Testing...")

            options = uc.ChromeOptions()
            options.binary_location = cft_chrome_path

            driver = uc.Chrome(
                driver_executable_path=cft_chromedriver_path,
                options=options,
                use_subprocess=True
            )

            print("✅ Chrome for Testing启动成功")
            driver.maximize_window()
            print("开始运行浏览器")
            return driver

        except Exception as cft_error:
            print(f"Chrome for Testing失败: {str(cft_error)[:200]}")
            print("尝试标准Selenium...")

    # 策略3: 标准Selenium ChromeDriver (fallback)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = system_chrome_path  # 明确指定标准 Chrome
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument(f'user-agent={agent}')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--no-proxy-server')  # 禁用代理

    max_retries = 3
    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ 标准ChromeDriver启动成功")
            driver.maximize_window()
            print("开始运行浏览器")
            return driver
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"ChromeDriver启动失败,重试 {attempt + 1}/{max_retries}...")
                print(f"错误: {str(e)[:100]}")
                time.sleep(2)
            else:
                print(f"所有尝试都失败了")
                print(f"完整错误: {str(e)}")
                raise e