SA=jenkins-sa
NS=jenkins
SERVER=$(kubectl config view -o jsonpath='{.clusters[?(@.name=="mlops-dev-aks")].cluster.server}')
SECRET_NAME=jenkins-sa-token
CA=$(kubectl get secret -n $NS $SECRET_NAME -o jsonpath='{.data.ca\.crt}')
TOKEN=$(kubectl get secret -n $NS $SECRET_NAME -o jsonpath='{.data.token}' | base64 -d)

cat > kubeconfig-jenkins <<EOF
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: ${CA}
    server: ${SERVER}
  name: mlops-dev-aks
contexts:
- context:
    cluster: mlops-dev-aks
    user: jenkins-sa
    namespace: jenkins
  name: jenkins-sa@mlops-dev-aks
current-context: jenkins-sa@mlops-dev-aks
kind: Config
preferences: {}
users:
- name: jenkins-sa
  user:
    token: ${TOKEN}
EOF

kubectl create secret generic jenkins-kubeconfig -n $NS \
  --from-file=kubeconfig=kubeconfig-jenkins \
  --dry-run=client -o yaml | kubectl apply -f -

rm kubeconfig-jenkins
