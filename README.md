# CSP-Applier

## Usage:

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
    * `http_path`: The HTTPS server address, e.g., `https://127.0.0.1:12345`
    * `file_path`: The path of where the JS/CSS files are saved on the machine.
      The Https server should run at here, e.g., `/tmp/csp`
6. Open browser and change the Http/Https proxy to 127.0.0.1, and port is 8080.
7. Browse certain websites and the new JS/CSS files should be generated in `/tmp/csp`

## Generate SSL Certificate

```bash
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
```

* Generate the `.pem` file using the command above
* Add the certificate to the trust list of the browser
