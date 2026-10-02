FROM python:3.14-alpine

LABEL maintainer="Russell Land"
LABEL project="route23"

ENV USER=route23
ENV UID=1000
ENV GID=1000
ENV HOME=/home/route23

RUN apk add --no-cache openssh-client && \
    addgroup -g 1000 -S ${USER} && \
    adduser -u 1000 -S ${USER} -G ${USER}

COPY --chown=${UID}:${GID} ./src/main.py ${HOME}/main.py

USER 1000
WORKDIR ${HOME}

HEALTHCHECK --interval=30s --timeout=5s --start-period=1s --retries=1 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "main.py"]