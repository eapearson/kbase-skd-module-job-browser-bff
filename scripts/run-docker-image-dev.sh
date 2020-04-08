function ensure_network_exists() {
    local net=$1
    local network_exists=$(docker network ls --filter name=$net --format='{{.CreatedAt}}')
    if [ -z "$network_exists" ]; then
        docker network create $net
    fi
}

function ensure_deploy_local_exists() {
    if [ ! -d deploy_local ]
    then
        mkdir -p deploy_local/work_dir
        echo "created deploy_local"
    else 
        echo "deploy_local already exists"
    fi
}

root=$(git rev-parse --show-toplevel)
source_dir=lib
container_root=/kb/module

ENV=ci
NETWORK_NAME="kbase-dev"

echo "Ensuring network $NETWORK_NAME exists"
# ensure_network_exists kbase-dev

echo "Ensuring deploy_dir is set up"
ensure_deploy_local_exists

echo "Starting dev image..."
docker run -i -t \
  --network="${NETWORK_NAME}" \
  --name=JobBrowserBFF  \
  --dns=8.8.8.8 \
  -e "KBASE_ENDPOINT=https://${ENV}.kbase.us/services" \
  -e "AUTH_SERVICE_URL=https://${ENV}.kbase.us/services/auth/api/legacy/KBase/Sessions/Login" \
  -e "AUTH_SERVICE_URL_ALLOW_INSECURE=true" \
  -p 5000:5000 \
  --mount type=bind,src=${root}/deploy_local/work_dir,dst=${container_root}/work \
  --mount type=bind,src=${root}/${source_dir},dst=${container_root}/${source_dir} \
  --rm test/job-browser-bff:dev 
