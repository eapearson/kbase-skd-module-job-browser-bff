# Using on macOS

## SDK

git clone https://github.com/kbase/kb_sdk
cd kb_sdk
jenv versions

* system (set by /Users/erikpearson/.jenv/version)
  1.8
  1.8.0.222
  openjdk64-1.8.0.222


jenv local 1.8
jenv shell 1.8
jenv enable-plugin export (just needs setting once)
exec $SHELL -l

make

## Create service

export PATH=$PATH:`pwd`/../kb_sdk/bin


kb-sdk init -l python -u eapearson JobBrowserBFF

cd JobBrowserBFF

make

kb-sdk test

modify test_local/test.cfg

appdev -> ci

add ci testtoken


kb-sdk test

should pass

A. start populating the spec file

add implementation

loop back to A.

Oh, add some clients that i've been using in python dynamic services:

GenericClient.py
DynamicServiceClient.py
ServiceUtils.py
Errors.py