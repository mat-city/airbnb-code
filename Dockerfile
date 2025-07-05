FROM python:3.9

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

RUN pip3 install --no-cache-dir --upgrade \
    pip

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common

WORKDIR /home/appuser/app

COPY . /home/appuser/app

RUN pip install -r requirements.txt

RUN chmod +x /home/appuser/app/run.sh

USER appuser

EXPOSE 8501

ENTRYPOINT ["./run.sh"]
