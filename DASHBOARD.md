# Import the P2Pool dashboard

In Grafana, choose Dashboards, New, Import, then upload `p2pool-dashboard.json`. Select the Prometheus data source and the P2Pool instance. The data source variable supports an existing Prometheus connection. A newly provisioned data source is not required.

The 12 panels use only metric families emitted by this repository's collector. Install its timer, expose the textfile through Node Exporter, and deliver those metrics to Prometheus as described in `BUNDLE-README.md`. Keep the same stable `instance` label. Missing optional fields display no telemetry. No panel fabricates zero values for missing data.

The dashboard uses UTC. File content age and collector age are separate because P2Pool can leave unchanged JSON files untouched. API status means the collector could read and parse the file. Stratum submissions, sidechain shares and payouts are different events.

This dashboard was assembled for the supplied small collector. It does not claim to recreate every panel or private metric in the article's production screenshots. Daemon log panels require a separately configured log pipeline and are not included.

JSON structure, query metric names and collector tests were checked locally. No live Grafana import or rendering test was performed.
