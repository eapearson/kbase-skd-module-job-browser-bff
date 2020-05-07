SERVICE = jobbrowserbff
SERVICE_CAPS = JobBrowserBFF
SPEC_FILE = JobBrowserBFF.spec
URL = https://kbase.us/services/jobbrowserbff
DIR = $(shell pwd)
LIB_DIR = lib
SCRIPTS_DIR = scripts
TEST_DIR = test
LBIN_DIR = bin
WORK_DIR = /kb/module/work/tmp
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE_CAPS)_async_job.sh
STARTUP_SCRIPT_NAME = start_server.sh
TEST_SCRIPT_NAME = run_tests.sh

.PHONY: test

# These tasks are should be run within the service docker container.

default: compile

all: compile build build-startup-script build-executable-script build-test-script

# install: compile build build-startup-script build-executable-script build-test-script

compile:
	kb-sdk compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--pysrvname $(SERVICE_CAPS).$(SERVICE_CAPS)Server \
		--pyimplname $(SERVICE_CAPS).$(SERVICE_CAPS)Impl;
	# repair the impl file
	@echo "Reparing impl file..."
	@bash ./scripts/fix-impl.sh

build:
	@chmod +x $(SCRIPTS_DIR)/entrypoint.sh

build-executable-script:
	@echo "Building executable script..."
	@mkdir -p $(LBIN_DIR)
	@echo '#!/bin/bash' > $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	@echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	@echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	@echo 'python3 -u $$script_dir/../$(LIB_DIR)/$(SERVICE_CAPS)/$(SERVICE_CAPS)Server.py $$1 $$2 $$3' >> $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)
	@chmod +x $(LBIN_DIR)/$(EXECUTABLE_SCRIPT_NAME)

build-startup-script:
	@echo "Building startup script..."
	@mkdir -p $(LBIN_DIR)
	@echo '#!/bin/bash' > $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	@echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	@echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	@echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	# NB: Using the fixed _Server not the sdk generated one.
	@echo 'uwsgi --master --processes 5 --threads 5 --http :5000 --uid kbmodule --wsgi-file $$script_dir/../$(LIB_DIR)/$(SERVICE_CAPS)/$(SERVICE_CAPS)_JSONRPCServer.py' >> $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)
	@chmod +x $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME)

build-test-script:
	@echo "Building test script..."
	@echo '#!/bin/bash' > $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'script_dir=$$(dirname "$$(readlink -f "$$0")")' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'export KB_DEPLOYMENT_CONFIG=$$script_dir/../deploy.cfg' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'export KB_AUTH_TOKEN=`cat /kb/module/work/token`' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'echo "Removing temp files..."' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'rm -rf $(WORK_DIR)/*' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'echo "...done removing temp files."' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'export PYTHONPATH=$$script_dir/../$(LIB_DIR):$$PATH:$$PYTHONPATH' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'cd $$script_dir/../$(TEST_DIR)/enabled' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'echo "Starting mock servers..."' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'python3 -m MockServers.run_server --port 5001 --host "localhost" &' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'echo "...done"' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'echo "Running tests..."' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@echo 'python3 -m nose --with-coverage --cover-package=$(SERVICE_CAPS) --cover-package=biokbase --cover-html --cover-html-dir=/kb/module/work/test_coverage --nocapture  --nologcapture .' >> $(TEST_DIR)/$(TEST_SCRIPT_NAME)
	@chmod +x $(TEST_DIR)/$(TEST_SCRIPT_NAME)

test:
	@if [ ! -f /kb/module/work/token ]; then echo -e '\nOutside a docker container please run "kb-sdk test" rather than "make test"\n' && exit 1; fi
	@pwd
	@ls test
	@bash $(TEST_DIR)/$(TEST_SCRIPT_NAME)

clean:
	@rm -rfv $(LBIN_DIR)

# These tasks are designed to be run within the local development environment.
# Local development is facilitated by building and running the service image locally.

dev-image:
	@echo "> Creating local image for development or testing"
	@bash local-scripts/build-docker-image-dev.sh	

run-dev-image:
	@echo "> Running the already-built docker image"
	@bash local-scripts/run-docker-image-dev.sh

run-dev-mongo:
	@echo "> Running local mongo container for testing/development"
	@bash local-scripts/start-mongo-for-tests.sh

# Convenience for running tests (which are run inside the service container) when 
# kb_sdk is located one directory above.
run-tests:
	@echo "> Running tests via sdk"
	PATH="${PATH}":`pwd`/../kb_sdk/bin && kb-sdk test

# For testing the generation of a compilation report.
# This module uses a different Dockerfile that the kb_sdk generates.
run-local-report:
	@echo "> Running the already-built docker image"
	@bash local-scripts/run-docker-image-dev-report.sh