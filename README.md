Task

Create and deploy a microservice where a client application will be able to:
retrieve the current price of Bitcoin (BTC) in both EUR and CZK;
retrieve locally calculated daily and monthly averages for the price mentioned above, obtained from locally stored data.
Considerations:
the data storage cadence should be a minimum of 1 request every 5 minutes.
the microservice may be left running for years, but only a retention of 12 months is necessary.
a credential is required to leverage the microservice.
The output of any request should:
include both prices per 1 BTC, their currency, the client request’s time, and the server data’s time (if available).
be JSON formatted.
Use either JavaScript, Python or another language you are familiar with.
Containerize the microservice.
Prepare a deployment into Kubernetes:
the deployment should be reproducible.
the microservice should auto-start and be reachable via appropriate calls (for example: curl, postman, etc..).
the microservice and any related additional resources should be deployed into appropriate custom namespaces.
use Helm for this deployment.
Store the codebase in GitHub, and please share the link for the repository with us.

## Design

I have made this task in a very minimalistic way as a MVP:
* Minikube was used
* All 3 parts of app (flask, sheduled prices fetcher , db ) are in one pod as 3 containers
* no CI/CD, deployment is manual. But easy going 8)
  

## Build and publish docker image. You should use your own tag and login

```
docker build . -t maxi4/bitcoin-prices-app
docker login
docker push maxi4/bitcoin-prices-app
```

## Install minikube k8s cluster as a minimal MVP and use the kl alias to reach it

```
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
sudo ln -s /usr/local/bin/minikube /usr/bin/minikube
minikube start
alias kl="minikube kubectl -- "
kl get ns
```

## Get the IP of minikube controlplane as a NodePort exposes the app ip port to controlplane

```
kl get no -o wide
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION                  CONTAINER-RUNTIME
minikube   Ready    control-plane   45m   v1.30.0   192.168.49.2
```
```
export app_ip=192.168.49.2
```
or read it into the var 

```
$ app_ip=$(kl get nodes -o wide --no-headers | awk -v OFS='\t\t' 'FNR > 1; {print $6}') ; echo $app_ip
```

## Deploy the app as a kubectl deployment
```
kl apply -f k8s/bitcoin-prices-app.yaml
```

## or Helm deployment. In this case you can tune the params of deployment
```
helm install my-bitcoin-app helm-chart/
helm status my-bitcoin-app
```  

## Let`s ping the app

```
curl -X GET http://$app_ip:30000/ping
{
  "msg": "pong OK"
}
```

## Let`s login and get the token to env var

```
$ token=$(curl -X POST http://$app_ip:30000/login      -H "Content-Type: application/json"      -d '{"username":"admin", "password":"password"}' | jq -r '.access_token') && echo $token
```
## Let`s read the current prices

```
$ curl -X GET http://$app_ip:30000/current_price -H "Authorization: Bearer $token"
{
  "client_request_time": "2024-07-23T13:57:04.070820",
  "price_czk": 1531457.6311650001,
  "price_eur": 60676.65539100001,
  "server_data_time": "2024-07-23T13:56:06.511453"
}
```

## Let`s read the average prices (daily by default)

```
$ curl -X GET http://$app_ip:30000/average_price -H "Authorization: Bearer $token"
{
  "average_price_czk": 1542800.7561810217,
  "average_price_eur": 61126.0722561147,
  "client_request_time": "2024-07-23T13:59:03.229565"
}
```

## Let`s read the average prices (monthly)

```
$ curl -X GET http://$app_ip:30000/average_price?period=monthly -H "Authorization: Bearer $token"
```

## Destroy the app

```
helm delete my-bitcoin-app
```

## PS
This git branch have a Deployment instead of single add pod. the postges is in separated pod/service also.
when i killed the app
```
kl delete replicaset.apps/all-services-deployment-679fcb7c79 -n bitcoin-app-namespace
kl delete pod/all-services-deployment-679fcb7c79-9v5d7 -n bitcoin-app-namespace
kl delete pod/all-services-deployment-679fcb7c79-lpwbm -n bitcoin-app-namespace
```
i expected that the aold bearer token shouldnt work , but it works again on new created pods. how the Flask store the token really??

```
curl -X GET http://$app_ip:30000/current_price -H "Authorization: Bearer $token"
{
  "client_request_time": "2024-07-25T12:03:17.635323",
  "price_czk": 1503766.654698,
  "price_eur": 59175.111209200004,
  "server_data_time": "2024-07-25T12:02:50.873190"
}
```
