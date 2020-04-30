function ensure_network_exists() {
    local net=$1
    local network_exists=$(docker network ls --filter name=$net --format='{{.CreatedAt}}')
    if [ -z "$network_exists" ]; then
        docker network create $net
    fi
}

# This is the repo directory
root=$(git rev-parse --show-toplevel)

source_dir=lib
container_root=/kb/module

ENV=ci
NETWORK_NAME="kbase-dev"

echo "Ensuring network $NETWORK_NAME exists"
ensure_network_exists kbase-dev

echo "Starting dev image..."
docker run -i -t \
  --network=kbase-dev \
  --name=mongo  \
  --dns=8.8.8.8 \
  -e MONGO_INITDB_ROOT_USERNAME=test \
  -e MONGO_INITDB_ROOT_PASSWORD=test \
  -p 27017:27017 \
  --mount type=bind,src=${root}/test_local/mongo/db,dst=/data/db \
  --mount type=bind,src=${root}/test_local/mongo/config,dst=/data/configdb \
  --rm \
  mongo:latest
