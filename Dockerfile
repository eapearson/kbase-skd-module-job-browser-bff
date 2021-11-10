FROM alpine:3.14 as builder
LABEL org.opencontainers.image.authors="KBase Developer"

# The build stage needs just enough to run the KBase SDK tools.

# Hack to get packages to install over https behind proxy.
RUN sed -i 's/https\:\/\//http\:\/\//g' /etc/apk/repositories

# update system and system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache apache-ant bash git linux-headers make openjdk8 python3 python3-dev py3-setuptools python2

RUN mkdir -p /kb && \
    git clone --depth=1 https://github.com/kbase/kb_sdk /kb/kb_sdk && \
    cd /kb/kb_sdk && \
    make

COPY ./ /kb/module

RUN mkdir -p /kb/module/work/cache && \
    chmod -R a+rw /kb/module && \
    cd /kb/module && \
    PATH=$PATH:/kb/kb_sdk/bin && \
    KB_SDK_COMPILE_REPORT_FILE=/kb/compile_report.json \
    make all

# Final image

FROM alpine:3.14
LABEL org.opencontainers.image.authors="KBase Developer"

# Hack to get packages to install over https behind proxy.
RUN sed -i 's/https\:\/\//http\:\/\//g' /etc/apk/repositories

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 py3-pip python3-dev py3-setuptools \
    uwsgi uwsgi-http uwsgi-python3

# install python dependencies for the service runtime.

COPY --from=builder /kb /kb
WORKDIR /kb/module

RUN addgroup --system kbmodule && \
    adduser --system --ingroup kbmodule kbmodule && \
    chown -R kbmodule:kbmodule /kb/module && \
    chmod -R a+rw /kb/module/work && \
    chmod +x /kb/module/scripts/entrypoint.sh

USER kbmodule

RUN python3 -m venv venv && \
    source venv/bin/activate && \
    python3 -m pip install --upgrade pip && \
    pip install wheel==0.37.0 && \
    pip install -r requirements.txt

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
