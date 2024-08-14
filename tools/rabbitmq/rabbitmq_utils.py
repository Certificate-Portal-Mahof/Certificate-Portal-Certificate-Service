import aio_pika

from tools.rabbitmq.rabbitmq_manager import RabbitMQManager


class RabbitMQUtils:

    async def send_message(self, queue_message: bytes, queue_name: str = "certificate_creation"):
        rabbitmq_channel = RabbitMQManager().channel

        queue = await rabbitmq_channel.declare_queue(name=queue_name, durable=True)
        await rabbitmq_channel.default_exchange.publish(
            message=aio_pika.Message(body=queue_message),
            routing_key=queue.name,
        )

        print("Message published to queue:", queue.name)
