## Generate certs

### Generate CA key

```
$ openssl ecparam -out ca.key -name secp521r1 -genkey
$ openssl req -new -x509 -key ca.key -sha384 -days 365 -subj "/C=JP/ST=Tokyo/O=organization/CN=DynDNS CA" -extensions v3_ca -out ca.pem
```

### Generate Server key

```
$ openssl ecparam -out server.key -name secp521r1 -genkey
$ openssl req -new -key server.key -outform PEM -keyform PEM -out server.csr -subj "/C=JP/ST=Tokyo/O=organization/CN=dyndns.staging.ianlewis.org"


openssl ca -in server.csr -keyfile ca.key -cert ca.pem -extensions usr_cert -out server.pem
```
