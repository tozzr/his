FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app/

# CMD ["fastapi", "run", "app/main.py", "--port", "80"]
# If running behind a proxy like Nginx or Traefik add --proxy-headers
CMD ["fastapi", "run", "main.py", "--port", "80", "--proxy-headers"]
