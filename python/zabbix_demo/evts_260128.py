#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 使用zabbix包,从zabbix获取某个资源的监控指标数据时序数据,编写函数参数是ip,端口,指标名称,开始时间,结束时间,返回值是指标数据时序数据,兼容zabbix不同版本

"""
Zabbix监控指标时序数据获取模块

本模块提供了从Zabbix服务器获取监控指标时序数据的功能，
兼容不同版本的Zabbix API。
"""

import time
import logging
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入zabbix-api包
try:
    from pyzabbix import ZabbixAPI, ZabbixAPIException
except ImportError:
    logger.error("pyzabbix包未安装，请运行: pip install pyzabbix")
    raise

def get_zabbix_metric_data(ip: str, port: int, metric_name: str, 
                           start_time: int, end_time: int, 
                           username: str = "Admin", 
                           password: str = "zabbix") -> List[Dict[str, Any]]:
    """
    从Zabbix获取指定监控指标的时序数据
    
    Args:
        ip: Zabbix服务器IP地址
        port: Zabbix服务器端口
        metric_name: 监控指标名称（如：system.cpu.load[all,avg1]）
        start_time: 开始时间戳（秒）
        end_time: 结束时间戳（秒）
        username: Zabbix登录用户名，默认为Admin
        password: Zabbix登录密码，默认为zabbix
    
    Returns:
        时序数据列表，每个元素包含时间戳和值
        格式: [{"timestamp": 1609459200, "value": 0.5}, ...]
    
    Raises:
        Exception: 当获取数据失败时
    """
    zapi = None
    try:
        # 构建Zabbix API URL
        zabbix_url = f"http://{ip}:{port}/zabbix"
        logger.info(f"连接到Zabbix服务器: {zabbix_url}")
        
        # 初始化Zabbix API连接
        zapi = ZabbixAPI(zabbix_url)
        zapi.login(username, password)
        logger.info("Zabbix API登录成功")
        
        # 获取Zabbix版本信息，用于兼容性处理
        zabbix_version = zapi.api_version()
        logger.info(f"Zabbix版本: {zabbix_version}")
        
        # 1. 根据IP地址查找主机
        logger.info(f"根据IP {ip} 查找主机")
        hosts = zapi.host.get(
            output=["hostid", "name"],
            filter={"ip": ip}
        )
        
        if not hosts:
            # 尝试使用ip作为host参数查找
            hosts = zapi.host.get(
                output=["hostid", "name"],
                filter={"host": ip}
            )
        
        if not hosts:
            raise Exception(f"未找到IP为 {ip} 的主机")
        
        host_id = hosts[0]["hostid"]
        logger.info(f"找到主机ID: {host_id}")
        
        # 2. 根据主机ID和指标名称查找监控项
        logger.info(f"查找指标: {metric_name}")
        items = zapi.item.get(
            output=["itemid", "name", "key_", "value_type"],
            hostids=[host_id],
            search={"key_": metric_name}
        )
        
        if not items:
            raise Exception(f"在主机 {ip} 上未找到指标: {metric_name}")
        
        item_id = items[0]["itemid"]
        logger.info(f"找到监控项ID: {item_id}")
        
        # 3. 获取时序数据
        logger.info(f"获取时间范围 [{start_time}, {end_time}] 的数据")
        
        # 构建历史数据查询参数
        history_params = {
            "output": "extend",
            "history": items[0]["value_type"],  # 根据监控项类型确定历史表
            "itemids": [item_id],
            "time_from": start_time,
            "time_till": end_time
        }
        
        # 处理不同Zabbix版本的API差异
        if zabbix_version >= "5.0.0":
            # Zabbix 5.0+ 使用history.get API
            history_data = zapi.history.get(**history_params)
        else:
            # 早期版本可能需要调整参数
            history_data = zapi.history.get(**history_params)
        
        logger.info(f"获取到 {len(history_data)} 条时序数据")
        
        # 4. 格式化返回数据
        result = []
        for data in history_data:
            # 确保值的类型正确
            value = data.get("value")
            if value:
                try:
                    # 尝试转换为数字类型
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # 如果转换失败，保持字符串类型
                    pass
            
            result.append({
                "timestamp": int(data.get("clock", 0)),
                "value": value
            })
        
        # 按时间戳排序
        result.sort(key=lambda x: x["timestamp"])
        
        return result
        
    except ZabbixAPIException as e:
        logger.error(f"Zabbix API错误: {str(e)}")
        raise Exception(f"Zabbix API错误: {str(e)}")
    except Exception as e:
        logger.error(f"获取Zabbix监控数据失败: {str(e)}")
        raise
    finally:
        if zapi:
            try:
                zapi.logout()
                logger.info("Zabbix API登出成功")
            except:
                pass


def get_zabbix_mysql_metrics(ip: str, port: int, 
                            username: str = "Admin", 
                            password: str = "zabbix") -> Dict[str, List[str]]:
    """
    查询Zabbix中MySQL相关的监控指标，特别是TPS相关指标
    
    Args:
        ip: Zabbix服务器IP地址
        port: Zabbix服务器端口
        username: Zabbix登录用户名，默认为Admin
        password: Zabbix登录密码，默认为zabbix
    
    Returns:
        包含不同类型MySQL指标的字典
        格式: {
            "tps_related": ["mysql.status[Com_commit]", ...],
            "io_related": ["mysql.status[Innodb_data_reads]", ...],
            "thread_related": ["mysql.status[Threads_connected]", ...],
            "all_mysql_metrics": ["mysql.status[...]", ...]
        }
    
    Raises:
        Exception: 当查询失败时
    """
    zapi = None
    try:
        # 构建Zabbix API URL
        zabbix_url = f"http://{ip}:{port}/zabbix"
        logger.info(f"连接到Zabbix服务器: {zabbix_url}")
        
        # 初始化Zabbix API连接
        zapi = ZabbixAPI(zabbix_url)
        zapi.login(username, password)
        logger.info("Zabbix API登录成功")
        
        # 获取所有MySQL相关的监控项
        logger.info("查询MySQL相关监控项")
        items = zapi.item.get(
            output=["key_", "name"],
            search={"key_": "mysql."}
        )
        
        logger.info(f"找到 {len(items)} 个MySQL相关监控项")
        
        # 分类整理指标
        tps_related = []
        io_related = []
        thread_related = []
        all_mysql_metrics = []
        
        # TPS相关的关键词
        tps_keywords = ["Com_commit", "Com_rollback", "Questions", "Queries", "transactions"]
        # IO相关的关键词
        io_keywords = ["Innodb_data_read", "Innodb_data_write", "Innodb_os_log_write", "ibuf", "buffer_pool"]
        # 线程相关的关键词
        thread_keywords = ["Threads_", "thread"]
        
        for item in items:
            key = item.get("key_")
            if key:
                all_mysql_metrics.append(key)
                
                # 分类指标
                key_lower = key.lower()
                if any(keyword.lower() in key_lower for keyword in tps_keywords):
                    tps_related.append(key)
                elif any(keyword.lower() in key_lower for keyword in io_keywords):
                    io_related.append(key)
                elif any(keyword.lower() in key_lower for keyword in thread_keywords):
                    thread_related.append(key)
        
        # 如果没有找到TPS相关指标，添加一些常见的默认指标
        if not tps_related:
            tps_related = [
                "mysql.status[Com_commit]",
                "mysql.status[Com_rollback]",
                "mysql.status[Questions]",
                "mysql.status[Queries]"
            ]
        
        return {
            "tps_related": tps_related,
            "io_related": io_related,
            "thread_related": thread_related,
            "all_mysql_metrics": all_mysql_metrics
        }
        
    except ZabbixAPIException as e:
        logger.error(f"Zabbix API错误: {str(e)}")
        raise Exception(f"Zabbix API错误: {str(e)}")
    except Exception as e:
        logger.error(f"查询MySQL指标失败: {str(e)}")
        raise
    finally:
        if zapi:
            try:
                zapi.logout()
                logger.info("Zabbix API登出成功")
            except:
                pass


def example_usage():
    """
    示例用法
    """
    try:
        # 示例参数
        zabbix_ip = "127.0.0.1"
        zabbix_port = 80
        
        # 1. 查询MySQL相关指标（新增功能）
        print("=== 0. 查询MySQL相关指标 ===")
        try:
            mysql_metrics = get_zabbix_mysql_metrics(
                ip=zabbix_ip,
                port=zabbix_port
            )
            
            print(f"找到 {len(mysql_metrics['all_mysql_metrics'])} 个MySQL相关指标")
            
            if mysql_metrics['tps_related']:
                print("\nTPS相关指标:")
                for metric in mysql_metrics['tps_related']:
                    print(f"  - {metric}")
            else:
                print("\n未找到TPS相关指标，使用默认指标")
            
            if mysql_metrics['io_related']:
                print("\nIO相关指标:")
                for metric in mysql_metrics['io_related'][:5]:  # 只显示前5个
                    print(f"  - {metric}")
                if len(mysql_metrics['io_related']) > 5:
                    print(f"  ... 等 {len(mysql_metrics['io_related']) - 5} 个指标")
            
            if mysql_metrics['thread_related']:
                print("\n线程相关指标:")
                for metric in mysql_metrics['thread_related']:
                    print(f"  - {metric}")
        except Exception as e:
            print(f"查询MySQL指标失败: {str(e)}")
            print("使用默认MySQL指标继续")
        
        # 1. CPU负载示例
        print("\n=== 1. CPU负载示例 ===")
        metric = "system.cpu.load[all,avg1]"
        
        # 获取过去1小时的数据
        end = int(time.time())
        start = end - 3600
        
        # 调用函数获取数据
        data = get_zabbix_metric_data(
            ip=zabbix_ip,
            port=zabbix_port,
            metric_name=metric,
            start_time=start,
            end_time=end
        )
        
        print(f"获取到 {len(data)} 条 {metric} 指标数据")
        if data:
            print("前5条数据:")
            for i, item in enumerate(data[:5]):
                print(f"{i+1}. 时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['timestamp']))}, 值: {item['value']}")
        
        # 2. MySQL TPS示例
        print("\n=== 2. MySQL TPS示例 ===")
        # 使用查询到的MySQL指标或默认指标
        try:
            # 优先使用查询到的TPS相关指标
            if 'mysql_metrics' in locals() and mysql_metrics['tps_related']:
                mysql_tps_metrics = mysql_metrics['tps_related']
                print("使用查询到的TPS相关指标")
            else:
                # 默认MySQL TPS指标
                mysql_tps_metrics = [
                    "mysql.status[Com_commit]",  # 提交数
                    "mysql.status[Com_rollback]",  # 回滚数
                    "mysql.status[Questions]"  # 查询数（可作为TPS参考）
                ]
                print("使用默认MySQL TPS指标")
            
            for tps_metric in mysql_tps_metrics:
                try:
                    data = get_zabbix_metric_data(
                        ip=zabbix_ip,
                        port=zabbix_port,
                        metric_name=tps_metric,
                        start_time=start,
                        end_time=end
                    )
                    print(f"获取到 {len(data)} 条 {tps_metric} 指标数据")
                    if data and len(data) > 1:
                        # 计算TPS（每秒事务数）
                        total_transactions = int(data[-1]['value']) - int(data[0]['value'])
                        duration = end - start
                        tps = total_transactions / duration if duration > 0 else 0
                        print(f"估算TPS: {tps:.2f} 事务/秒")
                except Exception as e:
                    print(f"获取 {tps_metric} 失败: {str(e)}")
        except Exception as e:
            print(f"处理MySQL TPS指标失败: {str(e)}")
        
        # 3. MySQL IO示例
        print("\n=== 3. MySQL IO示例 ===")
        # 使用查询到的IO相关指标或默认指标
        try:
            if 'mysql_metrics' in locals() and mysql_metrics['io_related']:
                mysql_io_metrics = mysql_metrics['io_related'][:3]  # 只使用前3个
                print("使用查询到的IO相关指标")
            else:
                # 默认MySQL IO指标
                mysql_io_metrics = [
                    "mysql.status[Innodb_data_reads]",  # InnoDB数据读取次数
                    "mysql.status[Innodb_data_writes]",  # InnoDB数据写入次数
                    "mysql.status[Innodb_os_log_writes]"  # InnoDB日志写入次数
                ]
                print("使用默认MySQL IO指标")
            
            for io_metric in mysql_io_metrics:
                try:
                    data = get_zabbix_metric_data(
                        ip=zabbix_ip,
                        port=zabbix_port,
                        metric_name=io_metric,
                        start_time=start,
                        end_time=end
                    )
                    print(f"获取到 {len(data)} 条 {io_metric} 指标数据")
                    if data:
                        print(f"最新值: {data[-1]['value']}")
                except Exception as e:
                    print(f"获取 {io_metric} 失败: {str(e)}")
        except Exception as e:
            print(f"处理MySQL IO指标失败: {str(e)}")
        
        # 4. MySQL线程池数示例
        print("\n=== 4. MySQL线程池数示例 ===")
        # 使用查询到的线程相关指标或默认指标
        try:
            if 'mysql_metrics' in locals() and mysql_metrics['thread_related']:
                mysql_thread_metrics = mysql_metrics['thread_related']
                print("使用查询到的线程相关指标")
            else:
                # 默认MySQL线程指标
                mysql_thread_metrics = [
                    "mysql.status[Threads_connected]",  # 当前连接线程数
                    "mysql.status[Threads_running]",  # 当前运行线程数
                    "mysql.status[Threads_created]"  # 已创建线程数
                ]
                print("使用默认MySQL线程指标")
            
            for thread_metric in mysql_thread_metrics:
                try:
                    data = get_zabbix_metric_data(
                        ip=zabbix_ip,
                        port=zabbix_port,
                        metric_name=thread_metric,
                        start_time=start,
                        end_time=end
                    )
                    print(f"获取到 {len(data)} 条 {thread_metric} 指标数据")
                    if data:
                        print(f"最新值: {data[-1]['value']}")
                except Exception as e:
                    print(f"获取 {thread_metric} 失败: {str(e)}")
        except Exception as e:
            print(f"处理MySQL线程指标失败: {str(e)}")
    
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    example_usage()
