# Pinned by digest; Dependabot bumps it.
FROM python:3.14-alpine@sha256:2e740b2c28a426e74f11396c05e38afb3191acced75045b8d62df573c1dc8ce8

LABEL maintainer="Russell Land"
LABEL project="route23"

ENV USER=route23
ENV UID=1000
ENV GID=1000
ENV HOME=/home/route23

# main.py uses only the standard library, so pip (and the libraries it
# vendors, which carry most of the image's CVEs) is removed.
RUN apk add --no-cache openssh-client && \
    pip uninstall -y pip && \
    rm -rf /usr/local/lib/python3.14/ensurepip && \
    addgroup -g 1000 -S ${USER} && \
    adduser -u 1000 -S ${USER} -G ${USER}

COPY --chown=${UID}:${GID} ./src/main.py ${HOME}/main.py

USER 1000
WORKDIR ${HOME}

HEALTHCHECK --interval=30s --timeout=5s --start-period=1s --retries=1 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "main.py"]