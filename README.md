# TaskMaster

A simple tool for tasks!

## Technology

Python for logic
SQLite for persistance

## Getting started

Install Python 3.11, Sqlite
New virtual environment with `python -m venv .taskmaster`
Activate virtual environment `source .taskmaster/bin/activate`
`pip install -r requirements-dev.txt`
Create a new database 'taskmaster.sqlite'
`alembic upgrade head`
Install it as an executable `pip install --editable .`
Run with `taskmaster`

## Running webserver locally

You can serve this directly from Gunicorn for local development only. Just run

`gunicorn --reload website.app:app`

## Hosting

Stick this on a webserver running Gunicorn, Nginx, SQLite.
Assumption is you have an account on there that can sudo and the web processes run as user www-data.

### File copy

There's a helper script, `deploy.sh`, that will:

1. Copy the files to `~/temp_transfer` on the target server
2. Move them to `/var/www/taskmaster`
3. Chown them to `www-data`, 755
4. Delete `~/temp_transfer`

### Gunicorn

Sample `gunicorn.service` file:


```
[Unit]
Description=Gunicorn instance to serve Taskmaster
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/taskmaster
Environment="PATH=/var/www/taskmaster/.taskmaster/bin"
ExecStart=/usr/bin/gunicorn --reload --workers 3 --bind unix:/var/www/taskmaster/taskmaster.sock website.app:app

[Install]
WantedBy=multi-user.target
```

### Nginx

Sample Nginx config:

```
server {
    listen 443 ssl;
    server_name <IP GOES HERE>;

    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://unix:/var/www/taskmaster/taskmaster.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
