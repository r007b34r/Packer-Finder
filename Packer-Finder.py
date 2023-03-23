import requests
import re
from tqdm import tqdm

print("欢迎使用Packer-Finder")

# 1.等待用户输入文件名
filename = input("请输入文件名：")

# 2.读取文件名内所有url
with open(filename, "r") as f:
    urls = f.readlines()

# 3.需要程序实现能够识别所有url所有可能的前端打包器特征，比如webpack等
patterns = ["webpack", "vue", "react", "angular"]

# 4.自动访问所有url并且定位前端打包器特征，如果找到某一个目标url存在前端打包器特征，在程序里打印："发现该url存在前端打包器特征，url是:然后这里把前端打包器特征存在的url展示出来
hit_urls = []
for url in tqdm(urls):
    url = url.strip()
    try:
        response = requests.get(url)
        for pattern in patterns:
            if re.search(pattern, response.text):
                print(f"发现该url存在前端打包器特征，url是:{url}")
                hit_urls.append(url)
                break
    except:
        pass

# 5.最后单独保存所有具备前端打包器特征的url到一个新的txt文件里，一行一个url，文件名是hit.txt
with open("hit.txt", "w") as f:
    for url in hit_urls:
        f.write(url + "\n")