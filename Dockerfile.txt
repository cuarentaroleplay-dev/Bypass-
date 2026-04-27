#Copyright @ISmartCoder
#Updates Channel https://t.me/TheSmartDev
FROM python:3.9-slim-buster

RUN apt update && apt install -y git curl && apt clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["bash", "start.sh"]
