import requests


def socks_connet(ip, port):
    """
    :param ip:
    :param port:
    :return:
    """

    proxy = f'socks5://{ip}:{port}'

    # 设置代理的地址和端口
    proxies = {
        'http': proxy,
        'https': proxy,
    }

    # 你的目标URL
    url = 'https://ipinfo.io/'

    try:
        response = requests.post(url=url, proxies=proxies, timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)
        print(f"{ip}ip链接失败！", flush=True)
    else:
        print(f"{response.text}", flush=True)


socks_connet('first.proxys5.net', '6250')
