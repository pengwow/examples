#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工单入仓人工确认功能demo

功能描述：
1. 每月5-10日执行当年01-01至今的工单入仓确认操作
2. 有变化的工单需人工确认后入仓，无变化的工单直接入仓
3. 事件工单入终态，问题工单和变更工单入全量
4. 入仓后的数据如果再次发生变化，需要继续确认，确认后还要推送到仓库中
5. 只保留一个副本，每次入仓成功后删除原有副本
6. 模拟入仓为生成json数据
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any


class WorkOrder:
    """
    工单类，包含工单关键字段
    
    属性：
        id: 工单ID
        sn: 工单编号
        status: 工单状态
        create_time: 创建时间
        update_time: 更新时间
    """
    
    def __init__(self, id: str, sn: str, status: str, create_time: datetime, update_time: datetime):
        self.id = id
        self.sn = sn
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将工单对象转换为字典格式
        
        返回：
            Dict[str, Any]: 工单字典
        """
        return {
            "id": self.id,
            "sn": self.sn,
            "status": self.status,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkOrder":
        """
        从字典创建工单对象
        
        参数：
            data: 工单字典
        
        返回：
            WorkOrder: 工单对象
        """
        return cls(
            id=data["id"],
            sn=data["sn"],
            status=data["status"],
            create_time=datetime.strptime(data["create_time"], "%Y-%m-%d %H:%M:%S"),
            update_time=datetime.strptime(data["update_time"], "%Y-%m-%d %H:%M:%S")
        )


# 常量定义
HISTORY_FILE = "work_order_history.json"  # 历史数据文件路径
WAREHOUSE_FILE = "warehouse_data.json"  # 入仓数据文件路径
CURRENT_YEAR = datetime.now().year  # 当前年份
YEAR_START_DATE = datetime(CURRENT_YEAR, 1, 1)  # 当年开始日期


def load_history() -> Dict[str, Any]:
    """
    读取历史数据
    
    返回：
        Dict[str, Any]: 历史数据字典，包含work_orders字段
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 确保返回的是字典，即使文件内容是null
                if data is None:
                    return {"work_orders": {}}
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取历史数据失败: {e}")
            return {"work_orders": {}}
    else:
        return {"work_orders": {}}



def save_history(history_data: Dict[str, Any]) -> None:
    """
    保存历史数据
    
    参数：
        history_data: 历史数据字典
    """
    try:
        # 保存前先删除旧文件
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        print(f"历史数据已保存到 {HISTORY_FILE}")
    except IOError as e:
        print(f"保存历史数据失败: {e}")



def generate_sample_work_orders() -> List[WorkOrder]:
    """
    生成模拟工单数据
    
    返回：
        List[WorkOrder]: 工单列表
    """
    work_orders = []
    current_time = datetime.now()
    
    # 生成事件工单（EVENT-前缀）
    for i in range(5):
        # 随机生成创建时间和更新时间
        create_time = current_time - timedelta(days=30-i*5, hours=i*2)
        # 部分工单有更新
        if i % 2 == 0:
            update_time = create_time + timedelta(hours=1)
        else:
            update_time = create_time
        
        # 事件工单状态（终态：closed，非终态：open）
        status = "closed" if i % 3 == 0 else "open"
        
        work_orders.append(WorkOrder(
            id=f"WO-{current_time.year}-{1000+i}",
            sn=f"EVENT-{current_time.year}-{i+1}",
            status=status,
            create_time=create_time,
            update_time=update_time
        ))
    
    # 生成问题工单（PROBLEM-前缀）
    for i in range(5):
        create_time = current_time - timedelta(days=25-i*4, hours=i*3)
        # 部分工单有更新
        if i % 2 == 1:
            update_time = create_time + timedelta(hours=2)
        else:
            update_time = create_time
        
        work_orders.append(WorkOrder(
            id=f"WO-{current_time.year}-{2000+i}",
            sn=f"PROBLEM-{current_time.year}-{i+1}",
            status="active" if i % 2 == 0 else "resolved",
            create_time=create_time,
            update_time=update_time
        ))
    
    # 生成变更工单（CHANGE-前缀）
    for i in range(5):
        create_time = current_time - timedelta(days=20-i*3, hours=i*4)
        # 部分工单有更新
        if i % 3 == 0:
            update_time = create_time + timedelta(hours=3)
        else:
            update_time = create_time
        
        work_orders.append(WorkOrder(
            id=f"WO-{current_time.year}-{3000+i}",
            sn=f"CHANGE-{current_time.year}-{i+1}",
            status="planned" if i % 2 == 0 else "implemented",
            create_time=create_time,
            update_time=update_time
        ))
    
    print(f"生成了 {len(work_orders)} 条模拟工单数据")
    return work_orders



def is_in_valid_date_range() -> bool:
    """
    检查当前日期是否在每月5-10日范围内
    
    返回：
        bool: 如果在范围内返回True，否则返回False
    """
    current_day = datetime.now().day
    is_valid = 2 <= current_day <= 10
    print(f"当前日期：{datetime.now().strftime('%Y-%m-%d')}")
    print(f"是否在有效日期范围（每月5-10日）：{'是' if is_valid else '否'}")
    return is_valid



def filter_work_orders(work_orders: List[WorkOrder]) -> List[WorkOrder]:
    """
    筛选当年01-01至今的工单
    
    参数：
        work_orders: 原始工单列表
    
    返回：
        List[WorkOrder]: 筛选后的工单列表
    """
    filtered_orders = []
    for order in work_orders:
        # 检查创建时间或更新时间是否在当年01-01至今
        if order.create_time >= YEAR_START_DATE or order.update_time >= YEAR_START_DATE:
            filtered_orders.append(order)
    
    print(f"原始工单数量：{len(work_orders)}")
    print(f"筛选后（{YEAR_START_DATE.strftime('%Y-%m-%d')}至今）工单数量：{len(filtered_orders)}")
    return filtered_orders



def get_changed_work_orders(current_orders: List[WorkOrder], historical_data: Dict[str, Any]) -> List[WorkOrder]:
    """
    判断哪些工单需要人工确认（变化工单）
    
    规则：
    1. 如果工单不在历史数据中，视为新工单，需要确认
    2. 如果工单在历史数据中，比较update_time和warehouse_time
    3. 当update_time > warehouse_time时，认为工单有变化，需要继续确认
    4. 入仓后的数据如果再次发生变化，需要继续确认，确认后还要推送到仓库中
    
    参数：
        current_orders: 当前工单列表
        historical_data: 历史数据字典
    
    返回：
        List[WorkOrder]: 需要人工确认的工单列表
    """
    changed_orders = []
    historical_orders = historical_data.get("work_orders", {})
    
    for order in current_orders:
        if order.id not in historical_orders:
            # 新工单，需要确认
            changed_orders.append(order)
        else:
            # 检查工单是否有变化
            history_order = historical_orders[order.id]
            try:
                warehouse_time = datetime.strptime(history_order["warehouse_time"], "%Y-%m-%d %H:%M:%S")
                if order.update_time > warehouse_time:
                    # 工单有变化，需要继续确认
                    changed_orders.append(order)
                    print(f"工单 {order.id} 有变化（入仓时间：{warehouse_time}，更新时间：{order.update_time}），需要重新确认")
                else:
                    # 工单无变化，不需要确认
                    print(f"工单 {order.id} 无变化（入仓时间：{warehouse_time}，更新时间：{order.update_time}）")
            except (KeyError, ValueError) as e:
                # 历史数据格式错误，视为需要确认
                changed_orders.append(order)
    
    print(f"需要人工确认的工单数量：{len(changed_orders)}")
    for order in changed_orders:
        print(f"  - 工单ID：{order.id}，状态：{order.status}，更新时间：{order.update_time}")
    
    return changed_orders



def simulate_manual_confirmation(changed_orders: List[WorkOrder]) -> List[Dict[str, Any]]:
    """
    模拟人工确认流程
    
    参数：
        changed_orders: 需要人工确认的工单列表
    
    返回：
        List[Dict[str, Any]]: 确认后的工单字典列表，包含确认字段
    """
    confirmed_orders = []
    current_time = datetime.now()
    
    for order in changed_orders:
        # 模拟人工确认，实际场景中这里会有交互界面
        print(f"\n正在确认工单：{order.id}")
        print(f"  工单类型：{order.sn.split('-')[0]}")
        print(f"  当前状态：{order.status}")
        print(f"  创建时间：{order.create_time}")
        print(f"  更新时间：{order.update_time}")
        
        # 模拟确认操作，实际场景中这里会有确认按钮
        is_confirmed = True  # 这里模拟全部确认通过
        
        if is_confirmed:
            # 为确认的工单添加确认字段
            order_dict = order.to_dict()
            order_dict["confirmed"] = {
                "confirm_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "confirm_user": "admin"
            }
            confirmed_orders.append(order_dict)
            print(f"  确认结果：已确认")
        else:
            print(f"  确认结果：已拒绝")
    
    print(f"\n人工确认完成，共确认 {len(confirmed_orders)} 个工单")
    return confirmed_orders



def warehouse_work_orders(current_orders: List[WorkOrder], confirmed_orders: List[Dict[str, Any]], historical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    工单入仓功能
    
    规则：
    1. 事件工单入终态
    2. 问题工单和变更工单入全量
    3. 入仓后的数据如果再次发生变化，需要继续确认，确认后还要推送到仓库中
    4. 只保留一个副本，每次入仓成功后删除原有副本
    
    参数：
        current_orders: 当前工单列表
        confirmed_orders: 确认后的工单字典列表
        historical_data: 历史数据字典
    
    返回：
        Dict[str, Any]: 更新后的历史数据字典
    """
    # 生成入仓数据
    warehouse_data = {
        "event_terminal": [],  # 事件工单终态
        "problem_full": [],    # 问题工单全量
        "change_full": []      # 变更工单全量
    }
    
    # 处理确认后的工单
    confirmed_ids = [order["id"] for order in confirmed_orders]
    
    for order in current_orders:
        # 检查工单是否已确认
        order_dict = None
        for confirmed_order in confirmed_orders:
            if confirmed_order["id"] == order.id:
                order_dict = confirmed_order
                break
        
        if not order_dict:
            # 未确认的工单不入仓
            continue
        
        # 根据工单类型和状态生成入仓数据
        sn_prefix = order.sn.split("-")[0]
        
        if sn_prefix == "EVENT":
            # 事件工单入终态
            warehouse_data["event_terminal"].append(order_dict)
        elif sn_prefix == "PROBLEM":
            # 问题工单入全量
            warehouse_data["problem_full"].append(order_dict)
        elif sn_prefix == "CHANGE":
            # 变更工单入全量
            warehouse_data["change_full"].append(order_dict)
    
    # 生成入仓文件
    try:
        # 入仓前删除旧文件
        if os.path.exists(WAREHOUSE_FILE):
            os.remove(WAREHOUSE_FILE)
        
        with open(WAREHOUSE_FILE, "w", encoding="utf-8") as f:
            json.dump(warehouse_data, f, ensure_ascii=False, indent=2)
        print(f"\n入仓数据已生成：{WAREHOUSE_FILE}")
        print(f"事件工单终态数量：{len(warehouse_data['event_terminal'])}")
        print(f"问题工单全量数量：{len(warehouse_data['problem_full'])}")
        print(f"变更工单全量数量：{len(warehouse_data['change_full'])}")
    except IOError as e:
        print(f"生成入仓数据失败: {e}")
        return historical_data
    
    # 更新历史数据
    updated_history = historical_data.copy()
    if "work_orders" not in updated_history:
        updated_history["work_orders"] = {}
    
    current_time = datetime.now()
    for order in confirmed_orders:
        updated_history["work_orders"][order["id"]] = {
            "id": order["id"],
            "update_time": order["update_time"],
            "warehouse_time": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    return updated_history



def main():
    """
    主函数，执行工单入仓人工确认流程
    """
    print("=" * 60)
    print("工单入仓人工确认功能启动")
    print("=" * 60)
    
    # 1. 检查当前日期是否在有效范围内
    if not is_in_valid_date_range():
        print("当前日期不在有效范围内，流程终止")
        return
    
    # 2. 生成模拟工单数据
    print("\n" + "-" * 60)
    print("步骤1：生成模拟工单数据")
    print("-" * 60)
    work_orders = generate_sample_work_orders()
    
    # 3. 筛选当年01-01至今的工单
    print("\n" + "-" * 60)
    print("步骤2：筛选当年01-01至今的工单")
    print("-" * 60)
    filtered_orders = filter_work_orders(work_orders)
    
    # 4. 读取历史数据
    print("\n" + "-" * 60)
    print("步骤3：读取历史数据")
    print("-" * 60)
    history_data = load_history()
    
    # 5. 判断哪些工单需要人工确认
    print("\n" + "-" * 60)
    print("步骤4：判断需要人工确认的工单")
    print("-" * 60)
    changed_orders = get_changed_work_orders(filtered_orders, history_data)
    
    # 6. 模拟人工确认流程
    print("\n" + "-" * 60)
    print("步骤5：模拟人工确认流程")
    print("-" * 60)
    confirmed_orders = simulate_manual_confirmation(changed_orders)
    
    # 7. 执行工单入仓操作
    print("\n" + "-" * 60)
    print("步骤6：执行工单入仓操作")
    print("-" * 60)
    updated_history = warehouse_work_orders(filtered_orders, confirmed_orders, history_data)
    
    # 8. 保存更新后的历史数据
    print("\n" + "-" * 60)
    print("步骤7：保存更新后的历史数据")
    print("-" * 60)
    save_history(updated_history)
    
    print("\n" + "=" * 60)
    print("工单入仓人工确认流程完成")
    print("=" * 60)



if __name__ == "__main__":
    main()
