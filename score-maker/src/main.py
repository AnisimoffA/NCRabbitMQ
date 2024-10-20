from redis import Redis
from fastapi import FastAPI
from .routers import router_events
from .producer import router_producer, send_events_to_rabbitmq
from .config import REDIS_HOST, REDIS_PORT
from fastapi_utils.tasks import repeat_every
from .rabbitmq_config import RabbitMQClient


rabbitmq_client = RabbitMQClient()

app = FastAPI()
app.include_router(router_events)
app.include_router(router_producer)


@app.on_event("startup")
async def startup_event():
    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    app.state.redis = redis_client
    await rabbitmq_client.consume("to-line-provider")


@app.on_event("startup")
@repeat_every(seconds=10)  # Периодическая задача раз в 30 секунд
async def process_outbox():
    await send_events_to_rabbitmq()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await rabbitmq_client.close()
