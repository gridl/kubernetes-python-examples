#!/usr/bin/env python
from kubernetes import client, config
import argparse

# monkey patch
from kube import local_load_oid_token
config.kube_config.KubeConfigLoader._load_oid_token = local_load_oid_token

parser = argparse.ArgumentParser()
parser.add_argument('--in-cluster', help="use in cluster kubernetes config", action="store_true")
parser.add_argument('--node-name', help="node name to get pods for", required=True)
args = parser.parse_args()

if args.in_cluster:
    config.load_incluster_config()
else:
    try:
        config.load_kube_config()
    except Exception as e:
        print("Error creating Kubernetes configuration: %s", e)
        exit(2)

def main():

    # it works only if this script is run by K8s as a POD
    # config.load_incluster_config()
    config.load_kube_config()
    
    # node_name = os.environ.get('NODE_NAME', None)

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs on node: ", args.node_name)
    field_selector = 'spec.nodeName='+args.node_name
    ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


if __name__ == '__main__':
    main()
