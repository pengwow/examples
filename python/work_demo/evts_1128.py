# python的threading.Thread如何将多线程的返回结果合并后处理
import threading
import queue
import time


def worker(task_id: int, result_queue: queue.Queue) -> None:
    """
    工作线程函数，执行任务并将结果放入队列
    
    :param task_id: 任务ID，用于标识不同的线程任务
    :param result_queue: 结果队列，用于存储线程执行结果
    :return: None
    """
    try:
        print(f"线程 {task_id} 开始执行")
        # 模拟任务执行时间（实际应用中可以替换为真实业务逻辑）
        time.sleep(1)
        # 生成任务结果
        result = f"任务 {task_id} 执行结果: {task_id * 100}"
        # 将结果放入队列
        result_queue.put(result)
        print(f"线程 {task_id} 执行完成，结果已放入队列")
    except Exception as e:
        # 异常处理，将错误信息也放入队列
        error_result = f"任务 {task_id} 执行出错: {str(e)}"
        result_queue.put(error_result)


def main() -> None:
    """
    主函数，演示如何使用多线程并合并结果
    
    :return: None
    """
    # 创建结果队列
    result_queue = queue.Queue()
    
    # 定义线程数量
    thread_count = 5
    
    # 创建线程列表
    threads = []
    
    # 启动线程
    for i in range(thread_count):
        thread = threading.Thread(target=worker, args=(i, result_queue))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 从队列中获取并处理结果
    print("\n所有线程执行完成，开始合并结果：")
    results = []
    while not result_queue.empty():
        result = result_queue.get()
        results.append(result)
    
    # 处理合并后的结果
    print("\n合并后的结果：")
    for result in results:
        print(result)
    
    # 可以对结果进行进一步处理
    print(f"\n共处理了 {len(results)} 个结果")


if __name__ == "__main__":
    main()