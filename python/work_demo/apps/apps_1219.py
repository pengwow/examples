# 使用kafka读取topic数据,是否使用group读取编写函数demo
from kafka import KafkaConsumer
import json
import time


def consume_kafka_topic(bootstrap_servers, topic, group_id=None, auto_offset_reset='latest',
                         enable_auto_commit=False, consumer_timeout_ms=10000):
    """
    使用Kafka消费者读取topic数据，支持使用或不使用consumer group
    
    参数:
        bootstrap_servers (str or list): Kafka服务器地址，如 'localhost:9092' 或 ['kafka1:9092', 'kafka2:9092']
        topic (str): 要消费的topic名称
        group_id (str, optional): 消费者组ID，如果提供则使用group模式，否则不使用group
        auto_offset_reset (str, optional): 当没有初始偏移量或当前偏移量不再存在时的重置策略
            - 'latest': 从最新消息开始消费
            - 'earliest': 从头开始消费
            默认值为 'latest'
        enable_auto_commit (bool, optional): 是否自动提交偏移量，默认False
        consumer_timeout_ms (int, optional): 消费者超时时间（毫秒），超时后停止消费，默认10秒
    
    返回:
        list: 消费到的消息列表，每个元素包含topic、partition、offset、key、value等信息
    
    异常:
        KafkaError: Kafka相关错误
        Exception: 其他未知错误
    """
    try:
        # 配置消费者参数
        consumer_config = {
            'bootstrap_servers': bootstrap_servers,
            'auto_offset_reset': auto_offset_reset,
            'enable_auto_commit': enable_auto_commit,
            'consumer_timeout_ms': consumer_timeout_ms,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')) if x else None,
            'key_deserializer': lambda x: x.decode('utf-8') if x else None
        }
        
        # 如果提供了group_id，则添加到配置中
        if group_id is not None:
            consumer_config['group_id'] = group_id
        
        # 创建消费者实例
        consumer = KafkaConsumer(**consumer_config)
        
        # 订阅topic
        consumer.subscribe([topic])
        
        print(f"{'使用Group ID' if group_id else '不使用Group ID'}消费Kafka主题: {topic}")
        print(f"Kafka服务器: {bootstrap_servers}")
        print(f"消费模式: {auto_offset_reset}")
        print("开始消费消息...")
        
        consumed_messages = []
        
        # 开始消费消息
        for message in consumer:
            # 格式化消息信息
            msg_info = {
                'topic': message.topic,
                'partition': message.partition,
                'offset': message.offset,
                'key': message.key,
                'value': message.value,
                'timestamp': message.timestamp
            }
            
            consumed_messages.append(msg_info)
            
            # 打印消费到的消息
            print(f"\n消费到消息:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Key: {message.key}")
            print(f"  Value: {message.value}")
            print(f"  Timestamp: {message.timestamp}")
            
        # 关闭消费者
        consumer.close()
        
        print(f"\n消费完成，共消费 {len(consumed_messages)} 条消息")
        return consumed_messages
        
    except Exception as e:
        print(f"消费消息时发生错误: {str(e)}")
        raise


def consume_kafka_topic_group_mode(bootstrap_servers, topic, group_id, **kwargs):
    """
    使用消费者组模式消费Kafka topic数据（简化版）
    
    参数:
        bootstrap_servers (str or list): Kafka服务器地址
        topic (str): 要消费的topic名称
        group_id (str): 消费者组ID
        **kwargs: 其他传递给consume_kafka_topic的参数
    
    返回:
        list: 消费到的消息列表
    """
    return consume_kafka_topic(bootstrap_servers, topic, group_id=group_id, **kwargs)


def consume_kafka_topic_no_group_mode(bootstrap_servers, topic, **kwargs):
    """
    不使用消费者组模式消费Kafka topic数据（简化版）
    
    参数:
        bootstrap_servers (str or list): Kafka服务器地址
        topic (str): 要消费的topic名称
        **kwargs: 其他传递给consume_kafka_topic的参数
    
    返回:
        list: 消费到的消息列表
    """
    return consume_kafka_topic(bootstrap_servers, topic, group_id=None, **kwargs)


# 示例用法
if __name__ == "__main__":
    # Kafka服务器地址
    bootstrap_servers = ['localhost:9092']
    
    # 要消费的topic名称
    topic = 'test_topic'
    
    print("=" * 60)
    print("Kafka消费示例")
    print("=" * 60)
    
    # 示例1: 使用消费者组模式消费
    print("\n1. 使用消费者组模式消费:")
    print("-" * 40)
    try:
        # 使用group_id='test_group'，从最新消息开始消费
        messages1 = consume_kafka_topic_group_mode(
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            group_id='test_group',
            auto_offset_reset='latest',
            consumer_timeout_ms=5000
        )
    except Exception as e:
        print(f"错误: {str(e)}")
        print("请确保Kafka服务器正在运行且topic存在")
    
    # 示例2: 不使用消费者组模式消费
    print("\n2. 不使用消费者组模式消费:")
    print("-" * 40)
    try:
        # 不使用group_id，从头开始消费
        messages2 = consume_kafka_topic_no_group_mode(
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000
        )
    except Exception as e:
        print(f"错误: {str(e)}")
        print("请确保Kafka服务器正在运行且topic存在")
    
    print("\n" + "=" * 60)
    print("示例执行完成")
    print("=" * 60)
