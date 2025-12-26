import logging
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KafkaBatchPusher:
    """
    Kafka批量推送器，支持按配置的批量大小推送消息到不同的topic
    """
    
    def __init__(self, kafka_producer, batch_size: int = 100, max_retries: int = 3):
        """
        初始化Kafka批量推送器
        
        参数:
            kafka_producer: Kafka生产者实例，需要实现send方法
            batch_size: 每批次推送的最大消息数，默认100
            max_retries: 推送失败时的最大重试次数，默认3
        """
        self.kafka_producer = kafka_producer
        self.batch_size = batch_size
        self.max_retries = max_retries
    
    def push_messages(self, message_dict: Dict[str, List[Any]]) -> bool:
        """
        推送消息到Kafka
        
        参数:
            message_dict: 消息字典，key为topic后缀，value为消息列表
            
        返回:
            bool: 所有消息是否都成功推送
        """
        all_success = True
        
        for _key, _value in message_dict.items():
            _topic = f"topic_{_key}"
            logger.info(f"准备推送topic {_topic} 的 {len(_value)} 条消息")
            
            if not _value:
                logger.info(f"topic {_topic} 没有消息需要推送")
                continue
            
            # 按批次推送
            for i in range(0, len(_value), self.batch_size):
                batch = _value[i:i+self.batch_size]
                batch_start = i + 1
                batch_end = min(i + self.batch_size, len(_value))
                logger.info(f"推送topic {_topic} 的第 {batch_start}-{batch_end} 条消息")
                
                # 尝试推送，支持重试
                success = self._send_with_retry(_topic, batch)
                if not success:
                    logger.error(f"topic {_topic} 的第 {batch_start}-{batch_end} 条消息推送失败")
                    all_success = False
        
        return all_success
    
    def _send_with_retry(self, topic: str, messages: List[Any]) -> bool:
        """
        尝试发送消息，支持重试
        
        参数:
            topic: Kafka topic
            messages: 消息列表
            
        返回:
            bool: 是否成功发送
        """
        for retry in range(self.max_retries):
            try:
                # 调用kafka生产者的send方法
                # 注意：这里假设kafka_producer.send支持批量发送
                # 如果不支持，需要循环发送单条消息
                self.kafka_producer.send(topic, messages)
                logger.info(f"topic {topic} 的 {len(messages)} 条消息推送成功 (重试 {retry})")
                return True
            except Exception as e:
                logger.error(f"topic {topic} 的消息推送失败 (重试 {retry}): {str(e)}")
                
                # 如果是最后一次重试，返回失败
                if retry == self.max_retries - 1:
                    return False
                
                # 可以在这里添加重试延迟
                # time.sleep(1)  # 延迟1秒后重试
        
        return False


# 使用示例
if __name__ == "__main__":
    # 模拟Kafka生产者
    class MockKafkaProducer:
        def send(self, topic: str, messages: List[Any]):
            logger.info(f"模拟发送 {len(messages)} 条消息到 {topic}")
            # 模拟随机失败
            # if random.random() > 0.8:
            #     raise Exception("模拟Kafka发送失败")
            return True
    
    # 创建消息字典
    messages = {
        "cr": [f"cr_message_{i}" for i in range(250)],
        "pr": [f"pr_message_{i}" for i in range(150)],
        "in": [f"in_message_{i}" for i in range(50)]
    }
    
    # 创建Kafka批量推送器
    kafka_producer = MockKafkaProducer()
    pusher = KafkaBatchPusher(kafka_producer, batch_size=100, max_retries=3)
    
    # 推送消息
    success = pusher.push_messages(messages)
    
    if success:
        logger.info("所有消息推送成功")
    else:
        logger.error("部分消息推送失败")
