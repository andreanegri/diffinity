# Sample Data

Two directories simulating consecutive ML pipeline runs, for manually testing diffinity.

## --includelist

Files are named identically in both directories; pass them explicitly.

```bash
# From project root
source .venv/bin/activate

diffinity sample_data/run1 sample_data/run2 \
  --includelist config.json database.ini pipeline.yaml run_summary.txt

# Verbose output
diffinity sample_data/run1 sample_data/run2 \
  --includelist config.json database.ini pipeline.yaml run_summary.txt \
  --style verbose

# Export to HTML
diffinity sample_data/run1 sample_data/run2 \
  --includelist config.json database.ini pipeline.yaml run_summary.txt \
  --output report.html

# Obfuscate filesystem paths
diffinity sample_data/run1 sample_data/run2 \
  --includelist config.json database.ini pipeline.yaml run_summary.txt \
  --ignore-paths
```

### Files

| File | Diff Type | Changes |
|------|-----------|---------|
| `config.json` | Semantic (JSON) | model, batch_size, learning_rate, epochs, optimizer, dropout, output paths; key order differs between files |
| `database.ini` | Semantic (INI) | host, max_connections, min_connections, timeout, cache host and ttl |
| `pipeline.yaml` | Plain text | trainer image version, mixed_precision, grad_clip, augment flag, added export stage |
| `run_summary.txt` | Plain text | run ID, timestamps, duration, accuracy metrics, artifact paths, notes |

---

## --includepatterns

Files are named with the directory basename as a prefix: `run1_<suffix>` / `run2_<suffix>`.
The pattern is the shared suffix (starting with `_`); diffinity substitutes each dir's basename.

```bash
diffinity sample_data/run1 sample_data/run2 \
  --includepatterns _hyperparams.json _environment.ini

# Verbose output
diffinity sample_data/run1 sample_data/run2 \
  --includepatterns _hyperparams.json _environment.ini \
  --style verbose
```

### Files

| Pattern | Resolved in run1 | Resolved in run2 | Diff Type | Changes |
|---------|-----------------|-----------------|-----------|---------|
| `_hyperparams.json` | `run1_hyperparams.json` | `run2_hyperparams.json` | Semantic (JSON) | learning_rate, batch_size, weight_decay, lr_scheduler, warmup_steps |
| `_environment.ini` | `run1_environment.ini` | `run2_environment.ini` | Semantic (INI) | python_version, cuda_version, framework_version, gpu model, gpu_count, cpu_cores, ram |
