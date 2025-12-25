import uuid
import pika
import json


class RMServiceRpcClient(object):
    """RPC клиент для взаимодействия с RM сервисом через RabbitMQ (embedding)"""
    
    def __init__(self, settings) -> None:
        """Инициализирует RPC клиент с настройками RabbitMQ"""
        self.connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            virtual_host='/',
            credentials=pika.PlainCredentials(
                username=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD
            ),
            heartbeat=30,
            blocked_connection_timeout=2
        )
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        # Declare a private exclusive callback queue for RPC replies
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
    def on_response(self, ch, method, props, body):
        """Обрабатывает ответ от ML сервиса"""
        if self.corr_id == props.correlation_id:
            try:
                self.response = json.loads(body)
            except Exception:
                self.response = None

    def call(self, message: str) -> dict:
        """Выполняет RPC вызов к RM сервису"""
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rm_task_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps({"text": message})
        )
        while self.response is None:
            self.connection.process_data_events(time_limit=1)
        return self.response