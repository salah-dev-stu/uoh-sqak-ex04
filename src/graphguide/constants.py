"""Non-configurable literals (names/keys/filenames). Tunables live in ``config/``."""

# Output artifact filenames (Graphify + reports)
GRAPH_JSON = "graph.json"
GRAPH_HTML = "graph.html"
GRAPH_REPORT = "GRAPH_REPORT.md"
COST_JSON = "cost.json"

# Report destinations (relative to repo root)
REPORTS_DIR = "reports"
GRAPH_REPORT_DIR = "reports/graph"
METRICS_DIR = "reports/metrics"
VAULT_DIR = "vault"

# Investigation modes
MODE_NAIVE = "naive"
MODE_GRAPH = "graph"

# Gatekeeper call kinds
KIND_LLM = "llm"
KIND_SUBPROCESS = "subprocess"
KIND_FILE_READ = "file_read"

# Config file stems (loaded by shared.config)
CONFIG_GRAPHIFY = "graphify"
CONFIG_RATE_LIMITS = "rate_limits"
CONFIG_AGENTS = "agents"
CONFIG_TASKS = "tasks"
CONFIG_LOGGING = "logging"
