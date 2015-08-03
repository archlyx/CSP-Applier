# CSP-Applier

## Introduction

## Usage
1. Initiate environment:
./prepare.sh

2. Create a screen session and start local javascript server (port 8880, 4433)
screen -S local_server
nodemon local_server.js

3. Create a screen session and start template database server (port 4040, 27017)
screen -S template
nodemon training/db_server.js

4. Create a screen session and run Proxy (port 8080)
Screen -S proxy
mitmproxy -s 'intercept_xiang.py false domain(cnn.com)'

5. Deploy Chrome browser: 
1). install proxy extension (SwitchSharp)
2). add 8080 as proxy port
3). add two certs: (all in ./yu/)
    a. ./certs/cert.pem
    b. ~/.mitmproxy/mitmproxy-ca-cert.pem and ~/.mitmproxy/mitmproxy-ca.pem

6. Set port forwarding: port(27017, 4040, 8080, 8880, 4433)
ssh -L 27017:localhostL:27017 -L 4040:localhost:4040 -L 8080:localhost:8080 -L 8880:localhost:8880 -L 4433:localhost:4433 yu@lotus.cs.northwestern.edu

## Update
git pull https://github.com/archlyx/CSP-Applier.git xiang
