# Online hosting

This project is prepared as a single Node.js web service.

## Recommended deployment shape

The app serves both the dashboard pages and the `/api/*` endpoints from the same service, so the browser can keep using relative API URLs after deployment.

The project includes `render.yaml` for Render. It also includes a `Dockerfile` for Docker-based hosts.

### Important: account data persistence

The current application stores accounts in `data.json`. On hosts with an ephemeral filesystem, that file can disappear after a restart/redeploy.

The included Render configuration mounts `/var/data` and sets `DATA_DIR=/var/data`, so `data.json` is stored on the persistent disk.

## Render

1. Put this project in a Git repository.
2. Create a Render Web Service from that repository.
3. Render can use the included `render.yaml` configuration.
4. Set the `DEFAULT_ADMIN_PASSWORD` secret to a strong password before going live.
5. After deployment, open the public `onrender.com` address.

The service listens on the `PORT` supplied by the host and binds to `0.0.0.0`.

## Local testing

Node.js is required for the Node server:

    npm install
    npm start

Then open:

    http://localhost:3000

## Before making the site public

This project preserves the existing simple account architecture. For a real production site, move passwords to a proper password-hashing system (such as Argon2/bcrypt), use server-side sessions or signed tokens, validate all admin actions on the server, add rate limiting, and use a real database such as Postgres for larger deployments.

Do not publish the default administrator password.
