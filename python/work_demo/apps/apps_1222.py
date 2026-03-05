# 有一个变量A={"cr": [], "pr":[], "in":[]}
# 变量A进行遍历,每个key对应的value是需要推送到kafka中的,反之一次推送失败,需要分批推送,最大每次100条,这个是变量可以配置
# 比如
# for _key,_value in A.items():
#     _topic = f"topic_{_key}"
#     for i in range(0, len(_value), 100):
#         kafka.send(_topic, _value[i:i+100])

import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def batch_send_to_kafka(
    data_dict: Dict[str, List[Any]],
    kafka_producer,
    max_batch_size: int = 100
) -> None:
    """
    分批将数据发送到Kafka
    
    参数:
        data_dict: 数据字典，键为topic后缀，值为要发送的数据列表
        kafka_producer: Kafka生产者实例，需要实现send和flush方法
        max_batch_size: 每批次最大发送数量，默认100
    """
    for _key, _value in data_dict.items():
        _topic = f"topic_{_key}"
        logger.info(f"处理topic {_topic}，共 {len(_value)} 条数据")
        
        if not _value:
            logger.info(f"topic {_topic} 没有数据需要发送")
            continue
        
        # 分批发送
        for i in range(0, len(_value), max_batch_size):
            batch = _value[i:i+max_batch_size]
            batch_start = i + 1
            batch_end = min(i + max_batch_size, len(_value))
            logger.info(f"发送topic {_topic} 的第 {batch_start}-{batch_end} 条数据")
            
            try:
                # KafkaProducer.send不支持批量发送，需要循环发送单条消息
                for message in batch:
                    kafka_producer.send(_topic, message)
                
                # 调用flush确保消息被立即发送，避免消息积压
                kafka_producer.flush()
                
                logger.info(f"成功发送topic {_topic} 的第 {batch_start}-{batch_end} 条数据")
            except Exception as e:
                logger.error(f"发送topic {_topic} 的第 {batch_start}-{batch_end} 条数据失败: {str(e)}")


# 模拟Kafka生产者类，用于测试
def generate_test_data():
    """
    生成测试数据
    """
    test_data = {
        'user_event': [{'user_id': i, 'event_type': 'login', 'timestamp': f'2024-01-01 12:00:{i:02d}'} for i in range(250)],
        'order_event': [{'order_id': i, 'amount': 100 + i, 'status': 'completed'} for i in range(50)],
        'product_event': []  # 空数据测试
    }
    return test_data


class MockKafkaProducer:
    """
    模拟Kafka生产者，用于测试批量发送功能
    """
    def __init__(self):
        self.sent_messages = {}
        self.flushed_topics = []
        
    def send(self, topic, message):
        """
        模拟发送消息到Kafka
        """
        if topic not in self.sent_messages:
            self.sent_messages[topic] = []
        self.sent_messages[topic].append(message)
        logger.debug(f"Mock发送消息到topic {topic}: {message}")
        
    def flush(self):
        """
        模拟刷新消息，确保所有消息被发送
        """
        current_topics = list(self.sent_messages.keys())
        self.flushed_topics.extend(current_topics)
        logger.debug(f"Mock刷新topic: {', '.join(current_topics)}")
        
    def get_stats(self):
        """
        获取发送统计信息
        """
        stats = {topic: len(messages) for topic, messages in self.sent_messages.items()}
        return {
            'sent_messages': stats,
            'flushed_count': len(self.flushed_topics),
            'total_messages': sum(stats.values())
        }


# 使用示例
if __name__ == "__main__":
    # 生成测试数据
    test_data = generate_test_data()
    
    # 创建模拟Kafka生产者
    mock_producer = MockKafkaProducer()
    
    # 调用批量发送函数
    batch_send_to_kafka(test_data, mock_producer, max_batch_size=100)
    
    # 输出发送统计信息
    stats = mock_producer.get_stats()
    print("\n=== 发送统计信息 ===")
    print(f"总发送消息数: {stats['total_messages']}")
    print(f"总刷新次数: {stats['flushed_count']}")
    print("各Topic发送消息数:")
    for topic, count in stats['sent_messages'].items():
        print(f"  - {topic}: {count} 条")
    
    # 示例数据
    A = {
        "cr": [f"cr_data_{i}" for i in range(250)],  # 250条数据
        "pr": [f"pr_data_{i}" for i in range(50)],   # 50条数据
        "in": [f"in_data_{i}" for i in range(150)]    # 150条数据
    }
    
    print("\n=== 测试原始数据格式 ===")
    # 创建Kafka生产者实例
    kafka_producer = MockKafkaProducer()
    
    # 调用分批发送函数
    batch_send_to_kafka(A, kafka_producer, max_batch_size=100)
    
    # 输出发送统计信息
    stats = kafka_producer.get_stats()
    print("\n=== 原始数据格式发送统计信息 ===")
    print(f"总发送消息数: {stats['total_messages']}")
    print(f"总刷新次数: {stats['flushed_count']}")
    print("各Topic发送消息数:")
    for topic, count in stats['sent_messages'].items():
        print(f"  - {topic}: {count} 条")