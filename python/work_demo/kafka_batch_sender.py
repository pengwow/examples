import logging
from typing import Dict, List, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('kafka_batch_sender')


def send_to_kafka_in_batches(
    data_dict: Dict[str, List[Any]],
    kafka_producer: KafkaProducer,
    max_batch_size: int = 100,
    retry_count: int = 3,
    retry_delay: float = 1.0
) -> Dict[str, Dict[str, int]]:
    """
    将数据字典中的每个列表分批发送到对应的Kafka主题
    
    参数:
        data_dict: 数据字典，键为主题后缀，值为需要发送的数据列表
        kafka_producer: KafkaProducer实例
        max_batch_size: 每批次最大发送条数，默认为100
        retry_count: 发送失败重试次数，默认为3
        retry_delay: 重试间隔（秒），默认为1.0
    
    返回:
        Dict: 统计信息，包含每个主题的发送成功数和失败数
    """
    statistics = {}
    
    # 遍历数据字典
    for key, value_list in data_dict.items():
        topic = f"topic_{key}"
        statistics[topic] = {"success": 0, "failed": 0}
        
        # 检查列表是否为空
        if not value_list:
            logger.info(f"Topic {topic} 没有需要发送的数据")
            continue
        
        # 计算总批次数
        total_items = len(value_list)
        total_batches = (total_items + max_batch_size - 1) // max_batch_size
        logger.info(f"Topic {topic} 开始发送 {total_items} 条数据，共 {total_batches} 批次")
        
        # 分批发送
        for i in range(0, total_items, max_batch_size):
            batch_items = value_list[i:i+max_batch_size]
            batch_start = i + 1
            batch_end = min(i + max_batch_size, total_items)
            logger.debug(f"Topic {topic} 发送第 {i//max_batch_size + 1}/{total_batches} 批次，数据范围 {batch_start}-{batch_end}")
            
            # 发送当前批次
            success = False
            for retry in range(retry_count):
                try:
                    # 发送批次中的每个数据项
                    for item in batch_items:
                        # 将数据转换为JSON（如果不是字符串）
                        if not isinstance(item, str):
                            item = json.dumps(item, ensure_ascii=False)
                        
                        # 发送到Kafka
                        kafka_producer.send(topic, value=item.encode('utf-8'))
                    
                    # 确认所有消息已发送
                    kafka_producer.flush()
                    
                    # 发送成功
                    success = True
                    statistics[topic]["success"] += len(batch_items)
                    logger.debug(f"Topic {topic} 第 {i//max_batch_size + 1} 批次发送成功，共 {len(batch_items)} 条")
                    break
                except KafkaError as e:
                    logger.error(f"Topic {topic} 第 {i//max_batch_size + 1} 批次发送失败（重试 {retry+1}/{retry_count}）: {str(e)}")
                    if retry < retry_count - 1:
                        time.sleep(retry_delay)
            
            # 所有重试都失败
            if not success:
                statistics[topic]["failed"] += len(batch_items)
                logger.error(f"Topic {topic} 第 {i//max_batch_size + 1} 批次发送失败，已达到最大重试次数")
    
    return statistics


def create_kafka_producer(bootstrap_servers: List[str], **kwargs) -> KafkaProducer:
    """
    创建KafkaProducer实例
    
    参数:
        bootstrap_servers: Kafka服务器列表
        **kwargs: 其他KafkaProducer参数
    
    返回:
        KafkaProducer: 配置好的KafkaProducer实例
    """
    # 默认配置
    default_config = {
        'bootstrap_servers': bootstrap_servers,
        'acks': 'all',  # 确保所有副本都确认接收
        'retries': 3,   # 发送失败时的重试次数
        'batch_size': 16384,  # 16KB
        'linger_ms': 1,
        'buffer_memory': 33554432,  # 32MB
        'key_serializer': lambda x: x.encode('utf-8') if x else None,
        'value_serializer': lambda x: x  # 我们在send_to_kafka_in_batches中处理序列化
    }
    
    # 合并配置
    config = {**default_config, **kwargs}
    
    return KafkaProducer(**config)


if __name__ == "__main__":
    # 示例用法
    try:
        # 创建KafkaProducer实例
        producer = create_kafka_producer(['localhost:9092'])
        
        # 示例数据
        A = {
            "cr": [f"cr_data_{i}" for i in range(250)],  # 250条数据
            "pr": [f"pr_data_{i}" for i in range(50)],   # 50条数据
            "in": [f"in_data_{i}" for i in range(150)]    # 150条数据
        }
        
        # 发送数据
        result = send_to_kafka_in_batches(
            data_dict=A,
            kafka_producer=producer,
            max_batch_size=100,  # 每次最多发送100条
            retry_count=3,       # 失败重试3次
            retry_delay=1.0      # 重试间隔1秒
        )
        
        # 打印结果
        print("\n发送结果统计:")
        for topic, stats in result.items():
            print(f"{topic}: 成功 {stats['success']} 条, 失败 {stats['failed']} 条")
            
    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
    finally:
        # 关闭KafkaProducer
        if 'producer' in locals():
            producer.close()