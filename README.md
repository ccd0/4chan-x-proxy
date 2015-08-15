A simple script that runs a proxy on your local machine injecting the 4chan X script into 4chan, for use in browsers that don't support userscripts. Only works on http://boards.4chan.org/ (no HTTPS support).

Download it [here](https://ccd0.github.io/4chan-x-proxy/proxy.py).

Requires [Python 3](https://www.python.org/).

The script has these command line arguments:

`python proxy.py [port] [script filename or URL]`

The port defaults to 8000, and the script defaults to https://www.4chan-x.net/builds/4chan-X.user.js.

To use, run the script and change your proxy settings to use http://localhost:8000/proxy.pac (or http://localhost:PORT/proxy.pac) as the proxy auto-config URL.
