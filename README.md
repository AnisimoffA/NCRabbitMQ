score-maker: uvicorn src.main:app --reload --port 8001 --env-file .env.dev
line-provider: uvicorn src.main:app --reload --port 8000 --env-file .env.dev
dev:  docker-compose -f docker-compose.dev.yml up --build   
prod: docker-compose -f docker-compose.prod.yml up --build

kill ports: lsof -P | grep ':8000' | awk '{print $2}' | xargs kill -9   

