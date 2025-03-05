import concurrent.futures
import requests

with open('', 'r') as file:
    lines = file.readlines()

wrapped_lines = ['{}'.format('https://' + line.strip()) for line in lines]


def fetch_url(data):
    """

    :param data: 外部的url
    :return:
    """

    testip = "geo.iproyal.com"
    testport = "32325"

    proxy = f'socks5://{testip}:{testport}'

    # 设置代理的地址和端口
    proxies = {
        'http': proxy,
        'https': proxy,
    }

    try:
        response = requests.get(url=data, proxies=proxies, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"{e}！", flush=True)
    else:
        print(f"{response.status_code}", flush=True)


if __name__ == "__main__":
    # 要访问的网址列表
    url = wrapped_lines

    # 指定最大并行进程数为4
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # 提交任务，每个任务访问一个网址
        executor.map(fetch_url, url)
