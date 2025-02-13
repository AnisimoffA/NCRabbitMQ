from aio_pika import connect, Message, Connection, IncomingMessage, Channel
from .config import (RABBITMQ_HOST,
                     RABBITMQ_PORT,
                     RABBITMQ_USER,
                     RABBITMQ_PASSWORD)
import asyncio
import json
from .utils import ScoreDBMethods


class RabbitMQClient:
    def __init__(self):
        self.amqp_url = (f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}"
                         f"@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")
        self.connection: Connection = None
        self.consume_task: asyncio.Task = None
        self.channel: Channel = None

    async def connect(self):
        if not self.connection:
            self.connection = await connect(self.amqp_url)
            self.channel = await self.connection.channel()

    async def on_message(self, message: IncomingMessage):
        async with message.process():
            body_str = message.body.decode('utf-8')
            message_data = json.loads(body_str)
            event = message_data.get('event')
            status = message_data.get('status')
            data = message_data.get('data')

            print(event, status, data)

            if event == "score_update":
                if status == "error":
                    row_id = data['row_id']
                    await ScoreDBMethods.delete_from_score(row_id)

    async def publish(self, queue_name: str, message_content: json):
        await self.connect()
        queue = await self.channel.declare_queue(queue_name)
        await self.channel.default_exchange.publish(
            Message(message_content.encode()),
            routing_key=queue.name,
        )

    async def consume(self, queue_name: str):
        await self.connect()
        queue = await self.channel.declare_queue(queue_name)
        await queue.consume(self.on_message, no_ack=False)

    async def start_consume(self, queue_name: str):
        self.consume_task = asyncio.create_task(self.consume(queue_name))

    async def close(self):
        if self.consume_task:
            self.consume_task.cancel()
            try:
                await self.consume_task
            except asyncio.CancelledError:
                pass
            except Exception:
                print("Unexpected exception has occurred")
        if self.connection:
            await self.connection.close()
