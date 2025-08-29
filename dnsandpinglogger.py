import argparse, os, datetime, asyncio, traceback, logging, sys, time
from logging.handlers import TimedRotatingFileHandler
import aioping
import dns.asyncresolver

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help="Host to check.")
    parser.add_argument('--timeout', type=int, required=True, help="Timeout.")
    parser.add_argument('--file', type=str, default=None, help="Path to log file.")
    args = parser.parse_args()

    configure_logging(args.file)

    next_request = datetime.datetime.now()

    known_ip = None

    while True:
        while datetime.datetime.now() < next_request:
            await asyncio.sleep(.1)
        now = datetime.datetime.now()

        next_request = (now + datetime.timedelta(seconds=1)).replace(microsecond=0)

        try:
            if known_ip:
                host_result, ip_result = await asyncio.gather(get_ip(args.host, args.timeout), ping(known_ip, args.timeout))
            else:
                host_result = await get_ip(args.host, args.timeout)
                ip_result = None

            message = ' | '.join(((f'dns: success ({host_result[1]} ms)' if host_result[0] else ''), (f'ping: success ({ip_result} ms)' if ip_result is not None else '')))
            if message:
                logging.info(message)

            if host_result[0] and (host_result[0] != known_ip):
                logging.info(f'IP address changed: {known_ip} -> {host_result[0]}')
                known_ip = host_result[0]
        except Exception as e:
            logging.critical(f'Cycle FAILED: {e}\n{traceback.print_exception(e)}')     

def configure_logging(file: str | None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if file:
        file_handler = TimedRotatingFileHandler(file, when="midnight", interval=1)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

async def get_ip(host: str, timeout: int):
    resolver = dns.asyncresolver.Resolver()
    try:
        start_ts = time.perf_counter()
        response = await resolver.resolve(host, lifetime=timeout)
        duration = time.perf_counter() - start_ts
        ip = next(iter((answer.address for answer in response)), None)
        return ip, int(duration * 1000)
    except Exception as e:
        logging.warning(f'DNS lookup FAILED: {e}')
        return None, None
    
async def ping(ip: str, timeout: int):
    try:
        duration = await aioping.ping(ip, timeout=timeout)
        return int(duration * 1000)
    except TimeoutError:
        logging.warning(f'Ping FAILED, ip was {ip}')
        return None

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()