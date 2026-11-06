import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('p2pool-collector.py'))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'local').mkdir()
        self.write('stratum', dict(connections=7, hashrate_15m=45000, total_stratum_shares=100, wallet='PRIVATE_WALLET', workers=['PRIVATE_WORKER']))
        self.write('p2p', dict(connections=24, incoming_connections=10, uptime=1200, zmq_last_active=8, peers=['PRIVATE_ADDRESS']))

    def write(self, name, value):
        (self.root / 'local' / name).write_text(json.dumps(value))

    def test_valid_values_and_private_fields(self):
        text = collector.collect(self.root)
        self.assertIn('p2pool_hashrate_hps{window="15m"} 45000', text)
        self.assertIn('p2pool_zmq_silence_seconds 8', text)
        self.assertIn('p2pool_api_up{endpoint="local/stratum"} 1', text)
        self.assertNotIn('PRIVATE_', text)
        self.assertNotIn('window="24h"', text)

    def test_invalid_json_drops_old_values_preserves_other_endpoint(self):
        (self.root / 'local/stratum').write_text('{broken')
        text = collector.collect(self.root)
        self.assertIn('p2pool_api_up{endpoint="local/stratum"} 0', text)
        self.assertNotIn('p2pool_hashrate_hps', text)
        self.assertIn('p2pool_peer_connections 24', text)
        self.assertIn('p2pool_collector_timestamp_seconds', text)

    def test_missing_file(self):
        (self.root / 'local/p2p').unlink()
        text = collector.collect(self.root)
        self.assertIn('p2pool_api_up{endpoint="local/p2p"} 0', text)
        self.assertNotIn('p2pool_peer_connections', text)

    def test_permission_error(self):
        original = Path.open
        def denied(path, *args, **kwargs):
            if path.name == 'stratum':
                raise PermissionError('denied')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', denied):
            text = collector.collect(self.root)
        self.assertIn('p2pool_api_up{endpoint="local/stratum"} 0', text)
        self.assertIn('p2pool_api_up{endpoint="local/p2p"} 1', text)

    def test_invalid_numeric_has_no_partial_metrics(self):
        for value in [True, -1, float('nan'), float('inf'), '45000']:
            with self.subTest(value=value):
                self.write('stratum', dict(connections=7, hashrate_15m=45000, current_effort=value))
                text = collector.collect(self.root)
                self.assertNotIn('p2pool_hashrate_hps', text)
                self.assertIn('p2pool_api_up{endpoint="local/stratum"} 0', text)

    def test_timestamp_is_file_mtime(self):
        os.utime(self.root / 'local/stratum', (1700000000, 1700000000))
        self.assertIn('p2pool_api_timestamp_seconds{endpoint="local/stratum"} 1700000000.0', collector.collect(self.root))

    def test_atomic_replace_and_failure_preserves_previous_file(self):
        output = self.root / 'output'
        output.mkdir()
        target = output / 'p2pool.prom'
        with patch.dict(os.environ, P2POOL_API_DIR=str(self.root), METRICS_DIR=str(output)):
            collector.main()
            before = target.read_text()
            self.assertIn('p2pool_peer_connections 24', before)
            with patch.object(collector.os, 'replace', side_effect=OSError('write failure')):
                with self.assertRaises(OSError):
                    collector.main()
            self.assertEqual(target.read_text(), before)
            self.assertEqual([p.name for p in output.iterdir()], ['p2pool.prom'])

if __name__ == '__main__':
    unittest.main()
