FROM alpine:3.13 as builder
MAINTAINER KBase Developer

# The build stage needs just enough to run the KBase SDK tools.

# update system and system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache apache-ant bash git linux-headers make openjdk8 python3 python3-dev py3-setuptools py3-pip python2 rust cargo

RUN mkdir -p /kb && \
    git clone --depth=1 --branch=make-python-pep8-compliant https://github.com/eapearson/kb_sdk /kb/kb_sdk && \
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

FROM alpine:3.13
MAINTAINER KBase Developer

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 python3-dev py3-setuptools py3-pip  \
    uwsgi uwsgi-http uwsgi-python3  \
    rust cargo
#   py3-yaml py3-cffi py3-coverage py3-jinja2 

# install python dependencies for the service runtime.
RUN pip install --upgrade pip && \
    pip install wheel==0.34.2 && \
    pip install \
    cachetools==4.2.2 \
    cffi==1.14.5 \
    coverage==5.5.0 \
    jinja2==2.11.3 \
    jsonrpcbase==0.2.0 \
    ndg-httpsclient==0.5.1 \
    nose2==0.10.0 \
    nose2-cov==1.0a4 \
    python-dateutil==2.8.1 \
    pytz==2021.1 \
    requests==2.25.1 \
    toml==0.10.2 \
    jsonschema==3.2.0 \
    pymongo==3.11.3 \
    pyyaml==5.4.1

RUN pip install \
    https://github.com/rogerbinns/apsw/releases/download/3.35.4-r1/apsw-3.35.4-r1.zip \
    --global-option=fetch \
    --global-option=--version \
    --global-option=3.35.4\
    --global-option=--all \
    --global-option=build \
    --global-option=--enable-all-extensions

COPY --from=builder /kb /kb


RUN addgroup --system kbmodule && \
    adduser --system --ingroup kbmodule kbmodule && \
    chown -R kbmodule:kbmodule /kb/module && \
    chmod a+rw /kb/module/work/cache && \
    chmod +x /kb/module/scripts/entrypoint.sh

WORKDIR /kb/module

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
