Notes on how to deploy by forwarding the traffic through a different machine
----------------------------------------------------------------------------

This happens when you want to use e.g. a reverse proxy, e.g.
website on a hidden machine in the local network,
proxied by a machine visible from the outside. For instance, if you
run seekpath in a Docker container and want to show it by proxying it
via your main Apache server.

1. Enable modules `proxy` and `proxy_http` (more modules needed if you want to
   proxy https requests). Moreover, add also the `headers` module if you
   want to proxy seekpath to a subdomain (see below).

2. Add the following to your site. **Note**: in the following, we want to proxy
   the web service at the address `http://mymachine/proxied`,
   and the actual seekpath service runs on `localhost` at port `4444`;
   of course, adapt as needed:

   ```
   ProxyRequests off
   ProxyPreserveHost off

   <Location /proxied>
       ProxyPass http://localhost:4444/
       ProxyPassReverse http://localhost:4444/
       RequestHeader set X-Script-Name /proxied
       RequestHeader set X-Scheme http
       Order deny,allow
       Allow from all
   </Location>
   ```

  For nginx, similar headers need to be set, see
  http://flask.pocoo.org/snippets/35/
  (something similar to the following, untested):

    location /proxied {
        proxy_pass http://localhost:4444;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /proxied;
        }

   **Technical note**: The important header to set is `X-Script-Name`,
   that is used in the `ReverseProxied` class inside tools-barebone
   to properly set the script name, and therefore generate correct
   redirect URLs. Otherwise, redirects like
   `return flask.redirect(flask.url_for('input_structure'))` would not
   prepend `/proxied/` to the URL.

