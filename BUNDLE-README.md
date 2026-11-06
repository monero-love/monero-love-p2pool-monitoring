# P2Pool monitoring examples

This is a small file reader for the accompanying article. It is not a copy of the private collector. It exports only allowlisted numeric fields from `local/stratum` and `local/p2p`. It deliberately omits wallet, peer and worker data. Other API versions may require a schema change.

Reuse the Node Exporter, Alloy, TLS, Prometheus, Grafana, Loki and alert-routing setup from https://monero.love/guides/xmrig-observability/.

1. Add `--data-api /var/lib/p2pool/api --local-api` to your existing P2Pool command. Preserve all existing mining and network arguments. The directory is an example path. Arrange a controlled restart and confirm that both local files exist.
2. Create the `p2pool-monitor` system account and group. This example assumes the P2Pool service group is named `p2pool`. Adapt `SupplementaryGroups` to your installation. Grant the collector read and directory-traversal access to the API path through that group or a narrow ACL. Do not make private JSON files world-readable. In a container setup, use a read-only bind mount into the collector's filesystem namespace.
3. Install `p2pool-collector.py` as a root-owned, mode 0644 file at `/usr/local/lib/p2pool-monitor/p2pool-collector.py`. Create `/var/lib/p2pool-monitor/textfile` owned by `p2pool-monitor`, mode 0755.
4. Install the service and timer into `/etc/systemd/system/`, run `systemctl daemon-reload`, start `p2pool-monitor.service`, and inspect its exit status and generated `p2pool.prom`. Enable and start `p2pool-monitor.timer` once the first run succeeds.
5. Configure the existing Node Exporter textfile collector to read `/var/lib/p2pool-monitor/textfile`. If you already have a shared textfile directory, set `METRICS_DIR` and `ReadWritePaths` to it and grant the account narrow write permission there. Do not start a second exporter on the same listener. Node Exporter needs read access to the final `.prom` file.
6. Keep one stable `instance` label through Alloy. Verify that the metrics arrive in Prometheus and check the panel selectors before adding alerts.

`p2pool_api_up` is a collector parse/read check, not P2Pool's own HTTP status or proof of synchronization. A read, JSON or known-field validation failure emits zero and omits that file's old values from the new exposition. Missing optional fields stay absent. An output-write failure leaves the old file intact so collector age can reveal it.

File modification time means last content change. P2Pool avoids rewriting identical content. Treat rising age as a reason to investigate, not a universal heartbeat failure. Keep a separate collector timestamp, API read status, peer connectivity and daemon checks.

Run `python3 -m unittest test_collector.py` in this directory. Tests use synthetic files and do not connect to a miner. No P2Pool, exporter or monitoring service was reconfigured for this article. Deployment, filesystem permissions, service account names and notification delivery must be checked on your installation.
