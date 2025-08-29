# dnsandpinglogger

A small tool to log availability of a host and the dns server a the same time.

Every seconds, a ping and a DNS request are sent. The idea is to analyse dns outages: if the DNS query failes but the ping succedes, the DNS server is unavailable; if both fail, the problem might not be the DNS server.

## **Prerequisites**

- Python version 3.11 or newer with pip + venv

This program should run in any OS, but I have no capacity to test this, so feedback is appreciated. My test machines run Ubuntu and Raspbian.

## **Install**

```
git clone https://github.com/danielringch/dnsandpinglogger.git
python3 -m venv <path to virtual environment>
source <path to virtual environment>/bin/activate
python3 -m pip install -r requirements.txt
```

## **Usage**

```
source <path to virtual environment>/bin/activate
python3 -B tibber2mqtt/tibber2mqtt.py --host <host> --timeout <timeout in seconds> -- file <optional, path to log file>
```
