import requests
import threading
import mysql.connector
import schedule
import json
import time
import re


false = []
lock = threading.Lock()


def connect_mysql():
    """
    链接数据库方法，返回可操作的游标对象
    :return:可操作的ip列表
    """

    connection = mysql.connector.connect(
        host="",
        port="",
        user="",
        password="",
        database="",
    )

    curses = connection.cursor()
    curses.execute(
        "SELECT ip FROM `` where `status` = 1")
    ipdata = curses.fetchall()
    curses.close()

    iplist = []
    for ip in ipdata:
        iplist.append(ip[0])

    return iplist


def socks_connet(ip):
    """
    socks代理连接方法
    :param ip
    :return:url，proxies
    """
    testip = ip
    testport = 
    username = ""
    password = ""

    proxy = f'socks5://{username}:{password}@{testip}:{testport}'

    # 设置代理的地址和端口
    proxies = {
        'http': proxy,
        'https': proxy,
    }

    # 你的目标URL
    url = ''

    try:
        response = requests.post(url=url, proxies=proxies, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"{ip}ip链接失败！", flush=True)
        return ip
    else:
        print(f"{response.text}", flush=True)


def worker(datalist):
    """
    在每个线程中执行sockes函数操作
    """
    # 单线程列表，相对来说是局部变量
    lock_rsult = []
    # 声明全局变量false
    global false

    for ip in datalist:
        if socks_connet(ip) is not None:
            lock_rsult.append(ip)

    # 设置锁，保证多线程对false的修改不会因为竞争而导致数据问题
    with lock:
        print("Acquired lock")
        false.extend(lock_rsult)
        print("Extended list:", false)


def ipdata_action():
    """
    分割数据为多线程做准备
    :return:
    """
    global false
    iplist = connect_mysql()
    num_threads = 30
    chunck_size = len(iplist) // num_threads
    threads = []

    for i in range(num_threads):
        start_index = i * chunck_size
        end_index = (i + 1) * chunck_size if i < num_threads - 1 else len(iplist)
        thread_data = iplist[start_index:end_index]

        thread = threading.Thread(target=worker, args=(thread_data,))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    with lock:
        final_list = false.copy()

    false.clear()
    print(f'打印清除后的false的值{false}')
    print(
        "第一次检查已结束>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
    print(f"函数内打印第一次链接失败的IP{final_list}", flush=True)

    return final_list


def false_ip_action():
    """
    对链接失败的IP再次重新链接
    :return: 最终检查结果
    """
    # 初始失败的IP列表
    ipfalse = ipdata_action()
    print(f"打印初始链接失败的IP: {ipfalse}", flush=True)

    # 检查次数
    check_times = 3
    for i in range(1, check_times + 1):
        print(f"\n第{i}次检查开始" + ">" * 100, flush=True)

        if not ipfalse:
            print("所有IP均已成功连接，提前结束检查。", flush=True)
            return ipfalse

        # 临时存储本轮检查通过的IP
        temp_pass_ips = []
        for ip in ipfalse:
            if socks_connet(ip) is not None:
                temp_pass_ips.append(ip)
        # 更新失败的IP列表为本轮检查通过的IP
        ipfalse = temp_pass_ips
        print(f"打印第{i}次检查结果: {ipfalse}")

    return ipfalse


def timejob():
    """
    定时任务
    :return:
    """
    test_finally_false_ip = false_ip_action()

    return test_finally_false_ip


def msg_action(iplist):
    """
    IP预警格式处理
    :param iplist:
    :return:
    """
    pattern = re.compile(r'^(\d+\.\d+\.\d+\.)\d+')
    ip_count = {}
    # 遍历IP列表，统计每个号段IP数量
    for ip_address in iplist:
        match = pattern.match(ip_address)
        if match:
            subnet = match.group(1)
            ip_count[subnet] = ip_count.get(subnet, 0) + 1

    # 对出现次数小于10的IP显示全部信息
    for subnet, count in ip_count.items():
        if count <= 10:
            ip_count[subnet] = []
            for ip in iplist:
                if subnet in ip:
                    ip_count[subnet].append(ip)

    # 打印处理后的IP
    print(ip_count)
    msg = []
    for key, num in ip_count.items():
        msg.append(f"{key}X号段有{num}(个)不可用！")
    # 打印代发消息
    print(msg)

    return msg


def send_erro():
    """
    360发送IP无法连接的预警信息
    :return:
    """
    falseip = timejob()
    discountiplsit = list(set(falseip))
    print(f"打印要发送的信息{discountiplsit}")
    if len(discountiplsit) != 0:
        msg = f"360预警：{msg_action(discountiplsit)},测试链接为：，请手动提取IP并更换链接进行测试"

        url = ""

        data = {
            "msgtype": "text",
            "text": {
                "content": f"{msg}"
            },
            "at": {
                "atMobiles": "",
                "isAtAll": "false",
            }
        }

        data_string = json.dumps(data)

        respose = requests.post(url=url, data=data_string, headers={'Content-Type': 'application/json'})
        print(respose.text)

    # else:
    #     msg = "360预警:测试360静态IP池全部IP可以链接"


if __name__ == "__main__":
    print("定时任务开始>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
    schedule.every().day.at("09:00").do(send_erro)
    schedule.every().day.at("13:30").do(send_erro)
    schedule.every().day.at("17:00").do(send_erro)

    print("检车是否符合定时条件>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)
