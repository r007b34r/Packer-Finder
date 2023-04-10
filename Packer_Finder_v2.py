import urllib.parse
import logging
import re
from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple
import requests
from tqdm import tqdm
from loguru import logger

# 关闭 requests 库的 SSL 验证
requests.packages.urllib3.disable_warnings()

logger.add("packer-finder.log", rotation="500 MB", compression="zip")

# 读取文件名内的所有URL地址
def read_urls(filename: str) -> List[str]:
    with open(filename, "r") as f:
        return [line.strip() for line in f]

# 检查一个URL地址是否有效
def is_valid_url(url: str) -> bool:
    # 使用正则表达式进行 URL 格式验证
    regex = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9_](?:[A-Z0-9_-]{0,61}[A-Z0-9_])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # 域名
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(regex.match(url))

# 检查一个URL地址是否包含前端打包器特征
def check_url(url: str) -> Tuple[str, str]:
    try:
        # 发送GET请求并等待响应
        response = session.get(url, timeout=5, verify=False)
        # 对所有可能的特征进行匹配
        for pattern in patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                # 匹配到特征，返回URL地址和匹配的特征
                logger.info(f"发现该url存在前端打包器特征，url是:{url}，特征是：{pattern}")
                return url, pattern
    except requests.exceptions.RequestException as e:
        # 请求发生异常，记录错误日志并返回空字符串
        logger.error(f"访问URL {url} 失败：{e}")
    return "", ""

if __name__ == '__main__':
    print("欢迎使用Packer-Finder")
    print("请选择输入类型：")
    print("1. 文件")
    print("2. URL列表")

    # 读取用户的选择
    choice = input("请输入选择的数字：")

    # 如果用户选择了文件输入
    if choice == "1":
        filename = input("请输入文件名：")
        urls = read_urls(filename)
    # 如果用户选择了URL列表输入
    elif choice == "2":
        urls = []
        while True:
            url = input("请输入URL地址（直接回车退出）：")
            if not url:
                break
            if is_valid_url(url):
                urls.append(url)
            else:
                # 如果URL地址无效，记录警告日志
                logger.warning(f"无效的URL地址：{url}")
    else:
        # 如果用户选择无效，记录错误日志并退出
        logger.error("无效的选择")
        exit(1)

        # 所有可能的前端打包器特征
    patterns = ["webpack", "vue", "react", "angular", "parcel", "gulp", "grunt", "rollup", "babel", "browserify", "next.js", "nuxt.js", "svelte"]

    # 创建 requests Session 对象
    session = requests.Session()

    # 使用多进程自动访问所有URL地址并检查是否包含前端打包器特征
    hit_urls = []
    with ProcessPoolExecutor() as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        # 遍历所有线程的结果
        for future in tqdm(future_to_url):
            try:
                # 获取线程的结果
                hit_url, hit_pattern = future.result()
                if hit_url:
                    hit_urls.append(hit_url)
                    # 记录找到前端打包器特征的URL地址和特征
                    logger.info(f"URL地址 {hit_url} 包含前端打包器特征 {hit_pattern}")
            except requests.exceptions.Timeout as e:
                # 请求超时，记录错误日志
                logger.error(f"访问URL {future_to_url[future]} 超时，自动跳过：{e}")
            except Exception as e:
                # 处理线程结果失败，记录错误日志
                logger.error(f"处理URL {future_to_url[future]} 失败，自动跳过：{e}")

    # 将所有包含前端打包器特征的URL地址保存到文件中
    output_filename = input("请输入要保存结果的文件名：")
    with open(output_filename, "w") as f:
        for url in hit_urls:
            f.write(url + "\n")
    # 显示保存结果的文件路径
    logger.info(f"URL地址已保存到文件：{output_filename}")
