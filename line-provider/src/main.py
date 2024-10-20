from fastapi import FastAPI
from .routers import router_events
from .producer import router_producer, send_events_to_rabbitmq
from .rabbitmq_config import RabbitMQClient
from fastapi_utils.tasks import repeat_every


app = FastAPI()
app.include_router(router_events)
app.include_router(router_producer)

rabbitmq_client = RabbitMQClient()


@app.on_event("startup")
async def startup_event():
    await rabbitmq_client.consume("to-line-provider")


@app.on_event("startup")
@repeat_every(seconds=10)  # Периодическая задача раз в 30 секунд
async def process_outbox():
    await send_events_to_rabbitmq()


@app.on_event("shutdown")
async def shutdown_event():
    await rabbitmq_client.close()
