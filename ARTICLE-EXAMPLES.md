# Original article examples

Source: https://monero.love/guides/p2pool-monitoring/

These are the original fenced examples in article order. Some are commands, queries or explanatory output, not standalone config files. Follow the linked article before running a command.

## 1. Enable P2Pool’s local data files

```text
--data-api /var/lib/p2pool/api
--local-api
```

## 2. Enable P2Pool’s local data files

```text
/var/lib/p2pool/api/local/stratum
/var/lib/p2pool/api/local/p2p
```

## 3. Enable P2Pool’s local data files

```promql
p2pool_api_up{endpoint="local/stratum"}
p2pool_hashrate_hps{window="15m"}
p2pool_stratum_connections
```

## 4. Separate Stratum submissions from sidechain shares

```promql
rate(p2pool_stratum_shares_total[5m])
```

## 5. Check file freshness and the Monero connection

```promql
time() - p2pool_api_timestamp_seconds{endpoint="local/stratum"}
```
