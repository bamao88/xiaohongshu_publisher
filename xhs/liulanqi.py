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
    1. Chrome for Testing (版本完全匹配，推荐)
    2. undetected-chromedriver (反爬虫检测)
    3. 标准Selenium ChromeDriver (fallback)
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    import subprocess
    import platform
    import os

    agent = 'Mozilla/5.0 (Macintosh; Linux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    home_dir = os.path.expanduser("~")

    # Chrome for Testing路径 (版本匹配，推荐)
    cft_chrome_path = os.path.join(home_dir, "chrome-for-testing", "latest-chrome",
                                    "Google Chrome for Testing.app", "Contents", "MacOS",
                                    "Google Chrome for Testing")
    cft_chromedriver_path = os.path.join(home_dir, "chrome-for-testing", "latest-chromedriver", "chromedriver")

    # 策略1: 使用Chrome for Testing (最稳定，版本完全匹配)
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
            # 使用系统代理设置

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
            print("尝试其他策略...")

    # 策略2: 使用系统Chrome + undetected-chromedriver
    try:
        if platform.system() == 'Darwin':
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            if os.path.exists(chrome_path):
                chrome_version = subprocess.check_output([chrome_path, '--version']).decode().strip()
                print(f"检测到系统Chrome: {chrome_version}")

        import undetected_chromedriver as uc
        print("尝试使用undetected-chromedriver + 系统Chrome...")

        options = uc.ChromeOptions()
        # 使用系统代理设置
        driver = uc.Chrome(options=options, use_subprocess=True)

        print("✅ undetected-chromedriver启动成功")
        driver.maximize_window()
        print("开始运行浏览器")
        return driver

    except Exception as uc_error:
        print(f"undetected-chromedriver失败: {str(uc_error)[:200]}")
        print("尝试标准Selenium...")

    # 策略3: 标准Selenium ChromeDriver (fallback)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 使用系统代理设置
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument(f'user-agent={agent}')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')

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