FROM alpine:3.11 as builder
MAINTAINER KBase Developer

# The build stage needs just enough to run the KBase SDK tools.

# update system and system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache apache-ant bash git linux-headers make openjdk8 python3 python3-dev py3-setuptools python2

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

FROM alpine:3.11
MAINTAINER KBase Developer

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 python3-dev py3-setuptools \
    uwsgi uwsgi-http uwsgi-python3
#   py3-yaml py3-cffi py3-coverage py3-jinja2 

# install python dependencies for the service runtime.
RUN pip3 install --upgrade pip && \
    pip3 install wheel==0.34.2 && \
    pip3 install \
    cachetools==4.1.0 \
    cffi==1.14.0 \
    coverage==5.1.0 \
    jinja2==2.11.2 \
    jsonrpcbase==0.2.0 \
    ndg-httpsclient==0.5.1 \
    nose2==0.9.2 \
    nose2-cov==1.0a4 \
    python-dateutil==2.8.1 \
    pytz==2020.1 \
    requests==2.23.0 \
    toml==0.10.1 \
    jsonschema==3.2.0 \
    pymongo==3.10.1 \
    pyyaml==5.3.1

RUN pip3 install \
    https://github.com/rogerbinns/apsw/releases/download/3.31.1-r1/apsw-3.31.1-r1.zip \
    --global-option=fetch \
    --global-option=--version \
    --global-option=3.31.1\
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
