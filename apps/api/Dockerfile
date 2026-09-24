FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "alembic>=1.13" \
    "fastapi>=0.115" \
    "psycopg[binary]>=3.2" \
    "pydantic-settings>=2.6" \
    "sqlalchemy>=2.0" \
    "uvicorn[standard]>=0.32"

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
