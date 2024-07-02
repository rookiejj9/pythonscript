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
        host="sg-cdb-efwgl4tn.sql.tencentcdb.com",
        port="63997",
        user="gd_ceshi_360",
        password="Aq36Dyb7kxUu8S",
        database="master360",
    )

    curses = connection.cursor()
    curses.execute(
        "SELECT ip FROM `cm_static_ip_pool` where `status` = 1")
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
    testport = 6305
    username = "LgdTbNfg2A3iL8sK9pRx"
    password = "B51xRfL4yG9aC3hS6pN2"

    proxy = f'socks5://{username}:{password}@{testip}:{testport}'

    # 设置代理的地址和端口
    proxies = {
        'http': proxy,
        'https': proxy,
    }

    # 你的目标URL
    url = 'https://ipip.922proxy.com/ip_info'

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
    :return:
    """
    ipfalse_first = ipdata_action()
    print("第二次检查开始>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
    print(f"打印第一次链接失败的IP{ipfalse_first}", flush=True)
    false2test = []
    for ip in ipfalse_first:
        if socks_connet(ip) is not None:
            false2test.append(ip)

    print(f"打印第二次检查结果{false2test}")
    return false2test


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

    #打印处理后的IP
    print(ip_count)
    msg = []
    for key, num in ip_count.items():
        msg.append(f"{key}X号段有{num}(个)不可用！")
    #打印代发消息
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
        msg = f"360预警：{msg_action(discountiplsit)}"

        url = "https://oapi.dingtalk.com/robot/send?access_token=8ecd6e0718977d701c67c8f22a5adffdf88543a6fd1732ed54bd387d8f478fdb"

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
    schedule.every().day.at("09:50").do(send_erro)
    schedule.every().day.at("13:50").do(send_erro)
    schedule.every().day.at("17:50").do(send_erro)

    print("检车是否符合定时条件>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)
