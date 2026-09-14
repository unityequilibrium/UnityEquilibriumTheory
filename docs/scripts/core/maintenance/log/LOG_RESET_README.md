# Log Reset System

A comprehensive system for managing log files across all UET research topics.

## Overview

This system provides tools to:
- Analyze log distribution across all topics
- Reset logs for individual topics or all topics
- Diagnose broken log systems
- Manage excessive log files

## Components

### 1. analyze_log_distribution.py
Scans all topics and generates a comprehensive report on log distribution.

**Usage:**
```bash
python docs/scripts/maintenance/analyze_log_distribution.py
```

**Output:**
- Console report with statistics
- CSV report: `docs/scripts/maintenance/log_analysis_report.csv`
- JSON report: `docs/scripts/maintenance/log_analysis_report.json`

### 2. reset_topic_logs.py
Core reset system with selective deletion options.

**Usage:**
```bash
# Reset logs for a single topic (dry run)
python docs/scripts/maintenance/reset_topic_logs.py --topic 0.10 --dry-run

# Reset logs for a single topic, keep 10 most recent
python docs/scripts/maintenance/reset_topic_logs.py --topic 0.10 --keep-recent 10

# Reset logs for all topics with excessive logs
python docs/scripts/maintenance/reset_topic_logs.py --category EXCESSIVE --keep-recent 5

# Reset all logs (dangerous!)
python docs/scripts/maintenance/reset_topic_logs.py --all --force
```

**Options:**
- `--topic ID`: Reset logs for a specific topic (e.g., 0.10)
- `--all`: Reset logs for all topics
- `--category CAT`: Reset topics in a category (EXCESSIVE, HIGH, MODERATE, LOW, MINIMAL, NO_LOGS)
- `--keep-recent N`: Keep N most recent timestamp folders
- `--keep-pattern PATTERN`: Keep folders matching this pattern
- `--dry-run`: Preview changes without deletion
- `--force`: Skip confirmation prompts
- `--verbose`: Verbose output

### 3. diagnose_log_systems.py
Check which topics have working log generation and identify broken log systems.

**Usage:**
```bash
python docs/scripts/maintenance/diagnose_log_systems.py
```

**Output:**
- Console report with health status for each topic
- JSON report: `docs/scripts/maintenance/log_health_report.json`

### 4. log_reset_manager.py
Interactive master interface for managing log resets.

**Usage:**
```bash
python docs/scripts/maintenance/log_reset_manager.py
```

**Features:**
- Interactive menu system
- Analyze log distribution
- Diagnose log system health
- Reset logs for specific topics
- Reset logs by category
- Quick cleanup for excessive logs

### 5. Topic-Specific Reset Scripts
Individual reset scripts for each topic in `docs/scripts/maintenance/reset_logs/`:

- `reset_0.0_grand_unification.py`
- `reset_0.1_galaxy_rotation.py`
- `reset_0.3_cosmology.py`
- `reset_0.9_quantum_nonlocality.py`
- `reset_0.10_fluid_dynamics.py` (high priority)
- `reset_0.11_phase_transitions.py`
- `reset_0.13_thermodynamic_bridge.py`
- `reset_0.14_complex_systems.py` (high priority)
- `reset_0.17_mass_generation.py`
- `reset_0.29_ocean_recovery.py`
- `reset_0.30_mega_flora_biotech.py`
- `reset_0.31_spacetime_propulsion.py`

**Usage:**
```bash
python docs/scripts/maintenance/reset_logs/reset_0.10_fluid_dynamics.py
```

## Current Log Status

Based on the latest analysis:

### Excessive Logs (High Priority for Cleanup)
- 0.10_Fluid_Dynamics_Chaos: 1535 log files
- 0.14_Complex_Systems: 1095 log files

### High Log Count
- 0.3_Cosmology_Hubble_Tension: 606 log files
- 0.13_Thermodynamic_Bridge: 531 log files
- 0.9_Quantum_Nonlocality: 529 log files

### Broken Log Systems (Investigation Needed)
- 0.0_Grand_Unification: No log files
- 0.17_Mass_Generation: No log files
- 0.29_Ocean_Recovery: No log files

### Minimal Logs
- 0.30_Mega_Flora_Biotech: 7 log files
- 0.31_SpaceTime_Propulsion: 2 log files

## Safety Features

All reset operations include:
- **Dry-run mode**: Preview changes before actual deletion
- **Confirmation prompts**: Require user confirmation before deletion
- **Selective deletion**: Keep recent logs, keep by pattern
- **Detailed logging**: Audit trail of all operations
- **Backup reports**: JSON reports of what was deleted

## Quick Start

1. **Analyze current log distribution:**
   ```bash
   python docs/scripts/maintenance/analyze_log_distribution.py
   ```

2. **Diagnose log system health:**
   ```bash
   python docs/scripts/maintenance/diagnose_log_systems.py
   ```

3. **Quick cleanup for excessive logs:**
   ```bash
   python docs/scripts/maintenance/reset_topic_logs.py --category EXCESSIVE --keep-recent 10
   ```

4. **Interactive management:**
   ```bash
   python docs/scripts/maintenance/log_reset_manager.py
   ```

## Recommendations

1. **Run regular cleanup** for topics with excessive logs (keep 10-20 most recent)
2. **Investigate broken log systems** (0.0, 0.17, 0.29)
3. **Monitor log growth** for topics with high/moderate log counts
4. **Use dry-run mode** before actual deletion to preview changes
