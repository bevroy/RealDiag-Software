This folder contains Kubernetes manifests for staging and example resources.

Files:
- staging-realdiag.yaml    - Deployments and Services for realdiag-api and realdiag-web.
- ingress-realdiag.yaml    - Example Ingress (NGINX) with cert-manager annotations.

Usage notes:
- The `ingress-realdiag.yaml` is an example only. To enable external HTTPS access you
  must install an Ingress Controller (e.g., nginx-ingress) and cert-manager in the
  target cluster. For a production-ready setup:
  1. Install nginx-ingress (or your preferred controller) and ensure it exposes LoadBalancer/Host networking.
  2. Install cert-manager and create a ClusterIssuer (e.g., Let’s Encrypt or a staging issuer).
  3. Update `ingress-realdiag.yaml`: set `kubernetes.io/ingress.class` to your controller class,
     set `cert-manager.io/cluster-issuer` to your ClusterIssuer, and replace `realdiag.example.com` with
     the DNS name you control.
  4. Apply the manifest: `kubectl apply -f k8s/ingress-realdiag.yaml`.

Notes for kind clusters:
- kind does not provide a LoadBalancer by default. To test ingress locally you can:
  - Use `kind load` with a NodePort or install a local ingress solution (e.g., ingress-nginx with hostPort),
  - Or use port-forwarding for quick testing instead of ingress.
