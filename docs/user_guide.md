# FinGraph User & Analyst Guide

## Executive Summary

FinGraph provides risk analysts with a real-time, interactive network dashboard to visually untangle money laundering syndicates. Instead of scanning tabular transaction rows, analysts view a self-updating node-link graph with automated risk scoring and one-click account freeze capability.

## Key Features

1. **Interactive Node-Link Network Graph**:
   - **Red Nodes**: High-Risk Accounts (Score >= 70)
   - **Yellow Nodes**: Medium-Risk Accounts (Score 31 - 69)
   - **Green Nodes**: Low-Risk Accounts (Score 0 - 30)
   - Hover over nodes to inspect PageRank score, WCC component ID, and specific AML reason codes.

2. **Account Risk Leaderboard**:
   - Ranked list of accounts ordered by composite risk score.
   - Includes progress bars and explicit reason codes for compliance audits.

3. **Real-Time Alerts & Freeze Action**:
   - Automated alerts triggered when an account score crosses 70.
   - **Freeze Account Button**: Click to immediately flag and lock suspicious accounts/syndicates.

## Common Operations

### Starting Dashboard
```bash
streamlit run dashboard/app.py
```

### Running Pipeline Simulation
Click **"🚀 Run Pipeline Simulation"** in the sidebar to generate new transaction streams and update graph risk scores in real time.
