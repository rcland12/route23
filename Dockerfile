FROM python:3.14-alpine

LABEL maintainer="Russell Land"
LABEL project="route23"

ENV USER=route23
ENV UID=1000
ENV GID=1000
ENV HOME=/home/route23

RUN addgroup -g 1000 -S ${USER} && \
    adduser -u 1000 -S ${USER} -G ${USER}

COPY --chown=${UID}:${GID} ./src/main.py ${HOME}/main.py

USER 1000
WORKDIR ${HOME}

ENV TORRENT_DIR=/torrents
ENV STATE_FILE=/data/states/route23_state.json
ENV DOWNLOAD_DIR=/downloads
ENV BATCH_SIZE=20
ENV ROTATION_DAYS=14
ENV FORCE_ROTATION=false
ENV DELETE_DATA=false
ENV SHOW_STATUS=false
ENV LOG_LEVEL=INFO

ENTRYPOINT ["python", "main.py"]