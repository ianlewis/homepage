if [ "$1" = "" ]; then
    echo "Usage: $0 NAMESPACE"
    exit 1
fi 
NAMESPACE=$1
export HOMEPAGE_VERSION=$(git rev-parse --short master)
export NGINX_VERSION=1.13.10
envsubst < deploy.yaml | kubectl apply -n ${NAMESPACE} -f -
