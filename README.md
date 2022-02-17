# porkbun_ddns

A fork of
[porkbun-dynamic-dns-python](https://github.com/porkbundomains/porkbun-dynamic-dns-python).

The script will update your DNS table in case of your external IP is changed.

Run as a daemon and can be deployed with containers using either Podman or
Dockers.

## Configuration
Copy config.json.example to config.json and fill in your API key from Porkbun.
Copy domains.cfg.example to domains.cfg and add your domains that you want to
monitor.

Supports both base domains, subdomains and also wildcards.

## Installation: 

`podman build -t porkbun_ddns .`
or
`docker build -t porkbun_ddns .`
