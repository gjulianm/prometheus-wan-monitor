# Prometheus WAN monitor

This is a simple Python application that takes measurements of your Internet collection and exposes them in Prometheus format.

The use is simple: install this with `pip install git+https://github.com/gjulianm/prometheus-wan-exporter.git` and run it with the command `prometheus-wan-exporter`. Then, you can add it to your Prometheus scraping configuration. By default it listens on port 26543, but it can be changed with the `--port` CLI argument.

## Speed test

This program uses [speedtest-cli](https://pypi.org/project/speedtest-cli/) to measure bandwidth agains the best available server. By default, it will check the bandwidth every 10 minutes, as to not cause too much interference. This means that the bandwidth will appear as constant in Prometheus all that time.

The resulting metrics will be `wan_bandwidth_bps`, with two attributes: `dir` for upload/download and `server` for the measurement server used.

## Latency test

Latency test is done by pinging some servers (for now, Google and Cloudflare DNS, but if you want you can change the IPs in the `ping_hosts` variable of the function `latency_check()` in the __main__.py file). All measures go into a histogram metric from Prometheus (`wan_latency_hist_seconds`), and the mean of each batch is set in a gauge (`wan_latency_seconds`). Both metrics have the attribute `server` with the server used for the ping.

## Running as a service

You can use the prometheus-wan-monitor.service, set in *ExecStart* the correct path of the prometheus-wan-exporter executable and then drop the file in */etc/systemd/system*. After running `systemctl daemon-reload`, you will be able to use prometheus-wan-exporter as a regular systemd service and enable it on boot if you want.
