#------------------------------------------------------------------------------
# run-docker-image-dev.sh
#------------------------------------------------------------------------------
# DESCRIPTION
#
# Runs the job browser container locally, in a manner allowing both host access
# on `localhost:5000` and internal docker access on the network `kbase-dev` on 
# host `JobBrowserBFF:5000`. 
#
# This allows it to be used in coordination with a local web app (the kbase-ui 
# plugin `job-browser2`) as well as by the same web app when running in a 
# kbase-ui instanced running within a local docker container.
#
#------------------------------------------------------------------------------
# USAGE
#
# From the top level of this repo:
# 
# bash scripts/run-docker-image-dev.sh
#
# or, as it is designed to be used,
# 
# make run-docker-image
#
#------------------------------------------------------------------------------
# ARGUMENTS
#
# This scripts is designed to be configurated via environment variables, it 
# does not directly accept any command line arguments.
#
#------------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
#
# ENV
# The KBase deployment environment against which the service runs.
# Optional; defaults to CI. 
#
# This value is used to construct urls required by the
# service configuration (which are in turn provided as environment
# variables!)
# 
# NETWORK 
# The docker network with which the running docker container is
# associated.
# Optional; defaults to kbase-dev, the network used by kbase-ui for local
# development
#
#
#------------------------------------------------------------------------------
# REQUIREMENTS
# 
# docker
# git
#
#------------------------------------------------------------------------------
# TODO
#
# - don't set the network if not needed
# 
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# ensure_network_exists $net
#------------------------------------------------------------------------------
# Ensures that the docker network passed to this script exists - create it if it
# doesn't.
#
# ARGUMENTS
# $1 - The network name
#------------------------------------------------------------------------------
function ensure_network_exists() {
    local net=$1
    local network_exists=$(docker network ls --filter name=$net --format='{{.CreatedAt}}')
    if [ -z "$network_exists" ]; then
        docker network create $net
    fi
}

#------------------------------------------------------------------------------
# ensure_deploy_local_exists 
#------------------------------------------------------------------------------
#
# Ensure that the local directory deploy_local/work_dir exists
# 
# This directory is volume mounted into the running docker container
# to allow local inspection of files created in the service's standard working
# directory.
#
# ARGUMENTS
# none
#------------------------------------------------------------------------------
function ensure_deploy_local_exists() {
    if [ ! -d deploy_local ]
    then
        mkdir -p deploy_local/work_dir
        echo "created deploy_local"
    else 
        echo "deploy_local already exists"
    fi
}

# This gets the top level directory for this repo.
root=$(git rev-parse --show-toplevel)
source_dir=lib
container_root=/kb/module
test_dir=test/enabled

# Supported environment variables
ENV="${ENV:-ci}"
NETWORK="${NETWORK:-kbase-dev}"

echo "Ensuring network $NETWORK exists"
# ensure_network_exists kbase-dev

echo "Ensuring deploy_dir is set up"
ensure_deploy_local_exists

echo "Starting dev image..."
#
# Notes about docker run usage:
# - Run with interactive terminal because we want to stop it with Ctrl-C
# - provide standard minimal environment variables required by an sdk service
# - expose port 5000
# - mounts local directories:
#    - the internal work directory is mapped to deploy_local/work_dir, for 
#      compilation support, at a minimum.
#    - mount the local source into the container, to provide for quick edit/reload
#      type of development flow (possible since this is a python project)
# - remove the container when it is exited. 
#
docker run -it \
  --network="${NETWORK}" \
  --name=JobBrowserBFF  \
  -e "KBASE_ENDPOINT=https://${ENV}.kbase.us/services" \
  -e "AUTH_SERVICE_URL=https://${ENV}.kbase.us/services/auth/api/legacy/KBase/Sessions/Login" \
  -e "AUTH_SERVICE_URL_ALLOW_INSECURE=true" \
  -p 5000:5000 \
  --mount type=bind,src=${root}/test_local,dst=${container_root}/work \
  --mount type=bind,src=${root}/${source_dir},dst=${container_root}/${source_dir} \
  --mount type=bind,src=${root}/${test_dir},dst=${container_root}/${test_dir} \
  --rm test/job-browser-bff:dev 
