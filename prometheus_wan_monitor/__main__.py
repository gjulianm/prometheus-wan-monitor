# Module entry point
import sys
import argparse
import logging
import datetime
import time
import subprocess
import re

import speedtest
from prometheus_client import start_http_server, Histogram, Gauge

from .utils import configure_log


Bandwidth = Gauge("wan_bandwidth_bps",
                  "Available bandwidth, in bits per second", ['dir', 'server'])
LatencyHist = Histogram("wan_latency_hist_seconds",
                        "Latency to the measurement servers, histogram mode", ['server'])
LatencyGauge = Gauge("wan_latency_seconds",
                     "Current latency to the measurement servers", ['server'])
Connectivity = Gauge(
    "wan_reachable", "Indicates whether the given server is reachable or not", ['server'])


def speedtest_check(speed):
    logging.info('Measuring download speed...')
    speed.download()
    logging.info('Measuring upload speed...')
    speed.upload()
    logging.info('Done!')

    results = speed.results.dict()

    with Bandwidth._lock:
        # Clear old results in this hacky way because the developers don't want to provide a
        # clear() method to avoid old labels persisting.
        #
        # See https://github.com/prometheus/client_python/issues/277
        Bandwidth._metrics.clear()

    Bandwidth.labels('upload', results['server']['host']).set(
        results['upload'])
    Bandwidth.labels('download', results['server']['host']).set(
        results['download'])


ping_time_regex = re.compile(r'time=([0-9]+\.[0-9]+) *ms')


def latency_check():
    ping_hosts = ['1.1.1.1', '8.8.8.8']
    ping_batch = 4

    for host in ping_hosts:
        logging.info(f"Pinging {host}")
        ping_cmd = f'ping -i 0.2 -c {ping_batch} {host}'

        try:
            ping_out = subprocess.check_output(
                ping_cmd.split(' '), encoding='utf-8')
            measures = [
                float(v) / 1000.0 for v in ping_time_regex.findall(ping_out)]

            if len(measures) == 0:
                logging.warning(
                    f'No ping times could be extracted! ping tool output is {ping_out}')
                continue

            avg = sum(measures) / len(measures)

            for m in measures:
                LatencyHist.labels(host).observe(m)

            LatencyGauge.labels(host).set(avg)

            reachable = True
        except subprocess.CalledProcessError:
            logging.error(
                f'Could not ping {host} correctly, an error occurred')
            reachable = False
        except ValueError:
            logging.exception(
                f'Could not parse ping times from output {ping_out}')

        Connectivity.labels(host).set(1.0 if reachable else 0.0)


def main(args=None):
    argp = argparse.ArgumentParser(description='Deadman server for MS Teams')

    argp.add_argument('--verbose', '-v', action='store_true',
                      help='Verbose log output')

    argp.add_argument('--port', '-p', type=int,
                      default=26543, help='Where to listen')

    argp.add_argument('--interval-speedtest', type=int,
                      default=600, help='Interval (in seconds) of speed test')

    argp.add_argument('--interval-latency', type=int, default=10,
                      help='Interval (in seconds) of latency test')

    argp.add_argument('--speedtest-server-refresh-interval', type=int, default=3600,
                      help='How frequently the best speedtest server should be refreshed')

    args = argp.parse_args()

    configure_log(args=args)

    last_speedcheck = None
    last_latency = None
    last_server_refresh = None

    speedcheck_interval = datetime.timedelta(seconds=args.interval_speedtest)
    latency_interval = datetime.timedelta(seconds=args.interval_latency)
    server_refresh_interval = datetime.timedelta(
        seconds=args.speedtest_server_refresh_interval)

    speed = speedtest.Speedtest()

    start_http_server(args.port)

    logging.info(f"Started! Listening on port {args.port}")

    try:
        while True:
            now = datetime.datetime.now()

            # This could be done way better and more generic, but for now it's just a simple
            # script so I prefer to avoid complications
            if last_server_refresh is None or now - last_server_refresh > server_refresh_interval:
                speed.get_servers([])
                speed.get_best_server()
                last_server_refresh = now

            if last_latency is None or now - last_latency > latency_interval:
                latency_check()
                last_latency = now

            if last_speedcheck is None or now - last_speedcheck > speedcheck_interval:
                speedtest_check(speed)
                last_speedcheck = now

            # This is enough for most purposes. Maybe compute the gcm of all the intervals...
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Ctrl-C detected, exiting")
        sys.exit(0)


if __name__ == '__main__':
    main()
