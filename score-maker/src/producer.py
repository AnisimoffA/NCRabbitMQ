from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy import select
from .database import async_session_maker
from .models import OutboxMessageModel
from .rabbitmq_config import RabbitMQClient


rabbitmq_client = RabbitMQClient()

router_producer = APIRouter(
    prefix="/kafka_producer",
    tags=["Producer"]
)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        return session


@router_producer.post('/create_message')
async def send_events_to_rabbitmq():
    try:
        async with await get_session() as session:
            result = await session.execute(
                select(OutboxMessageModel).
                where(OutboxMessageModel.status == 'in process')
            )
            events = result.scalars().all()
            for event in events:
                await rabbitmq_client.publish("to-line-provider", event.data)

                event.status = 'successfully sent'
                event.processed_on = datetime.now(timezone.utc)
                await session.commit()
    except Exception as e:
        print(e)
