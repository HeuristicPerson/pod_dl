FROM python:3.9-alpine


# Defining the workdir
#=======================================================================================================================
WORKDIR /app


# Copying needed files
#=======================================================================================================================
COPY pod_dl pod_dl
COPY configs configs
COPY scripts/run.sh .


# Installation of packages
#=======================================================================================================================
RUN apk add --update --no-cache curl=7.80.0-r0 ffmpeg=4.4.1-r2 && \
    pip install --no-cache-dir -r /app/pod_dl/python-deps.txt && \
    rm -f /app/pod_dl/python-deps.txt

# Supercronic installation
#-------------------------
ARG SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64
ARG SUPERCRONIC=supercronic-linux-amd64
ARG SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]
RUN curl -fsSLO "$SUPERCRONIC_URL" && \
    echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - && \
    chmod +x "$SUPERCRONIC" && \
    mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" && \
    ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic


# Environment variables
#=======================================================================================================================

# Env. variables for script customization
#----------------------------------------
ENV UID=1000 \
    GID=1000 \
    CRON_HOURS=6 \
    POD_DL_DEBUG=True \
    POD_DL_MAX_SYNC=5 \
    POD_DL_MAX_ARCH=10 \
    POD_DL_TRANSC_SERV=yes \
    POD_DL_TRANSC_FORC=no \
    POD_DL_TRANSC_FREQ=22050 \
    POD_DL_TRANSC_BITR=96 \
    POD_DL_SCR_CMD=""\
    POD_DL_SCR_MSG=""


# Creation of appuser and giving proper permissions to files and dirs
#=======================================================================================================================
RUN addgroup -g $GID appuser && \
    adduser -D -u $UID -G appuser appuser && \
    chown -R appuser:appuser /app && \
    mkdir /podcasts && \
    chown appuser:appuser /podcasts && \
    chmod 700 /podcasts && \
    chmod 500 /app/pod_dl/sync.py && \
    chmod 500 /app/run.sh


# Volumes
#=======================================================================================================================
VOLUME /podcasts


# Running the container
#=======================================================================================================================
USER appuser
CMD ["/app/run.sh"]