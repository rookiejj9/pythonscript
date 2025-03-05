import concurrent.futures
import requests
import re


def fetch_url(data):
    """
    账密，并发访问网址
    :param data:
    :return:
    """
    # 给定的字符串

    # 正则表达式匹配每个冒号前后的字符
    matches = re.findall(r'([^:]+):([^:]+)', data)

    ipdata = []

    for _ in matches:
        ipdata.append(_[0])
        ipdata.append(_[1])

    port = int(ipdata[1])
    ipdata[1] = port

    testip = ipdata[0]
    testport = ipdata[1]
    username = ipdata[2]
    password = ipdata[3]

    proxy = f'socks5://{username}:{password}@{testip}:{testport}'

    # 设置代理的地址和端口
    proxies = {
        'http': proxy,
        'https': proxy,
    }

    url = ""

    try:
        response = requests.post(url=url, proxies=proxies, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"{e}！", flush=True)
    else:
        print(f"{response.json()}", flush=True)


if __name__ == "__main__":
    # 要访问的网址列表
    data = [""]

    # 指定最大并行进程数为4
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        # 提交任务，每个任务访问一个网址
        executor.map(fetch_url, data)
