import os
import sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import ipaddress
import json
import socket
import psutil



def is_private_ip(ip):
    """检查 IPv4/IPv6 是否为私有地址"""
    ip_obj = ipaddress.ip_address(ip)

    # IPv4: 过滤私有地址和 CGNAT 地址（100.64.0.0/10）
    if ip_obj.version == 4 and (ip_obj.is_private or ip_obj in ipaddress.IPv4Network("100.64.0.0/10")):
        return True

    # IPv6: 过滤本地链路地址（fe80::/10）和私有 IPv6 地址（fd00::/8）
    if ip_obj.version == 6 and (ip_obj.is_link_local or ip_obj.is_private):
        return True

    return False



def get_active_public_ips():
    active_interfaces = []
    net_io = psutil.net_io_counters(pernic=True)  # 获取网卡流量信息

    for iface, stats in net_io.items():
        if stats.bytes_sent > 0 or stats.bytes_recv > 0:  # 只保留有流量的网卡
            active_interfaces.append(iface)

    network_info_list = []

    for interface, addrs in psutil.net_if_addrs().items():
        if interface not in active_interfaces:  # 只获取有流量的网卡
            continue

        ipv4_list, ipv6_list = [], []

        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4
                if not is_private_ip(addr.address):  # 排除私有地址
                    ipv4_list.append(addr.address)
            elif addr.family == socket.AF_INET6:  # IPv6
                ipv6_address = addr.address.split("%")[0]  # 移除 zone ID
                if not is_private_ip(ipv6_address):  # 过滤 fe80:: 和 fd00::
                    ipv6_list.append(ipv6_address)

        # 仅存储真正的公网 IP（防止空结果）
        if ipv4_list or ipv6_list:
            network_info_list.append({
                "interface_name": interface,
                "ipv4": ipv4_list if ipv4_list else "",  # 取第一个 IPv4，如果没有则为空
                "ipv6": ipv6_list if ipv6_list  else ""# 保留所有 IPv6 地址
            })

    return {"network_info": network_info_list}



def get_network_info():
    # 获取当前正在使用的公网 IP（JSON 格式）
    active_public_ips = get_active_public_ips()
    json_output = json.dumps(active_public_ips, indent=4, ensure_ascii=False)
    if json_output:
        return json_output
    else:
        return False



def format_info(data):
    network_info = get_network_info()
    network_info = json.loads(network_info)

    network_info = network_info["network_info"][0]
    interface_name = network_info["interface_name"]
    ipv4 = network_info["ipv4"] if network_info["ipv4"] else None
    ipv6 = network_info["ipv6"] if network_info["ipv6"] else None
    return interface_name, ipv4, ipv6
