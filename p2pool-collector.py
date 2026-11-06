#!/usr/bin/env python3
"""Read selected P2Pool JSON fields and atomically export Prometheus metrics."""
import json
import math
import os
from pathlib import Path
import tempfile
import time

FIELDS = {
    'local/stratum': [
        ('hashrate_15m', 'p2pool_hashrate_hps', 'gauge', '{window="15m"}'),
        ('hashrate_1h', 'p2pool_hashrate_hps', 'gauge', '{window="1h"}'),
        ('hashrate_24h', 'p2pool_hashrate_hps', 'gauge', '{window="24h"}'),
        ('connections', 'p2pool_stratum_connections', 'gauge', ''),
        ('total_stratum_shares', 'p2pool_stratum_shares_total', 'counter', ''),
        ('shares_found', 'p2pool_sidechain_shares_found_total', 'counter', ''),
        ('shares_failed', 'p2pool_sidechain_shares_failed_total', 'counter', ''),
        ('current_effort', 'p2pool_current_effort_percent', 'gauge', ''),
        ('average_effort', 'p2pool_average_effort_percent', 'gauge', ''),
        ('last_share_found_time', 'p2pool_last_share_found_timestamp_seconds', 'gauge', ''),
    ],
    'local/p2p': [
        ('connections', 'p2pool_peer_connections', 'gauge', ''),
        ('incoming_connections', 'p2pool_incoming_peer_connections', 'gauge', ''),
        ('uptime', 'p2pool_uptime_seconds', 'gauge', ''),
        ('zmq_last_active', 'p2pool_zmq_silence_seconds', 'gauge', ''),
    ],
}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def collect(root):
    lines, declared = [], set()

    def emit(name, kind, value, labels=''):
        if name not in declared:
            lines.append('# TYPE ' + name + ' ' + kind)
            declared.add(name)
        lines.append(f'{name}{labels} {value}')

    for endpoint, fields in FIELDS.items():
        labels = '{endpoint="' + endpoint + '"}'
        ok = 0
        try:
            with (root / endpoint).open() as source:
                timestamp = os.fstat(source.fileno()).st_mtime
                data = json.load(source)
            if not isinstance(data, dict) or not finite(data.get('connections')):
                raise ValueError('Expected numeric connections field')
            values = []
            for field, name, kind, series_labels in fields:
                if field not in data:
                    continue
                if not finite(data[field]):
                    raise ValueError('Invalid numeric metric')
                values.append((name, kind, data[field], series_labels))
            emit('p2pool_api_timestamp_seconds', 'gauge', timestamp, labels)
            for args in values:
                emit(*args)
            ok = 1
        except (OSError, ValueError, TypeError):
            pass
        emit('p2pool_api_up', 'gauge', ok, labels)
    emit('p2pool_collector_timestamp_seconds', 'gauge', time.time())
    return '\n'.join(lines) + '\n'


def main():
    root = Path(os.environ.get('P2POOL_API_DIR', '/var/lib/p2pool/api'))
    directory = Path(os.environ.get('METRICS_DIR', '/var/lib/p2pool-monitor/textfile'))
    text = collect(root)
    descriptor, name = tempfile.mkstemp(prefix='.p2pool-', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(descriptor, 'w') as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(name, 0o644)
        os.replace(name, directory / 'p2pool.prom')
    finally:
        if os.path.exists(name):
            os.unlink(name)


if __name__ == '__main__':
    main()
