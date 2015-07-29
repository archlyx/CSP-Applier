#!/bin/bash

mkdir logs
mkdir js_repository
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
sudo npm install --save express
sudo npm install --save morgan
sudo npm install --save cors
sudo npm install --save formidable


