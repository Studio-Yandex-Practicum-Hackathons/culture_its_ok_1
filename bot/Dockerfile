FROM python:3.10

ENV WORKDIR /app
ENV USER bot
ENV AM_I_IN_A_DOCKER_CONTAINER YES

WORKDIR $WORKDIR

COPY . .

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    pip install --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]