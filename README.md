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
3). add two certs:
    a. ./certs/cert.pem
    b. ~/.mitmproxy/mitmproxy-ca-cert.pem and ~/.mitmproxy/mitmproxy-ca.pem

6. Set port forwarding: port(27017, 4040, 8080, 8880, 4433)
ssh -L 27017:localhostL:27017 -L 4040:localhost:4040 -L 8080:localhost:8080 -L 8880:localhost:8880 -L 4433:localhost:4433 yu@lotus.cs.northwestern.edu



1. Create a directory where the generated JS/CSS files should be saved (e.g. `/tmp/csp`)
2. Start the daemon of database for templates.
3. Run a Https server in `/tmp/csp` such that the files can be normally requested from the website.
    * The `https_server.py` in `resources` directory is a simple implementation of Https server.
    * Generate SSL certificate (see below) and place it at `/path/to/the/pem`.
    * Replace your path of `certfile` in `https_server.py` and run.
4. Add the certificate of mitmproxy to the trust list of the browser. Usually the cert file
   is `~/.mitmproxy/mitmproxy-ca-cert.pem`.
5. Run mitmproxy use the following command:

    ```bash
    mitmproxy -s "intercept.py http_path file_path"
    ```
    
    * `http_path`: The Https server address, e.g., `https://127.0.0.1:12345`
    * `file_path`: The path of where the JS/CSS files are saved on the machine.
      The Https server should run at here, e.g., `/tmp/csp`
6. Open browser and change the Http/Https proxy to `127.0.0.1`, and port is `8080`.
7. Browse certain websites and the new JS/CSS files should be generated in `/tmp/csp`

## Generate SSL Certificate

```bash
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
```

* Generate the `.pem` file using the command above
* Add the certificate to the trust list of the browser
