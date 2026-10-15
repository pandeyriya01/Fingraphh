"""
FinGraph – Real-Time Fraud Syndicate Analytics
Enterprise Banking & AML Analytics Dashboard (High Contrast Dark Theme)
"""

import os
import sys
import textwrap
from pathlib import Path

# Ensure root Fingraph directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from src.simulator.generator import TransactionGenerator
from src.flink.processing_utils import TransactionStreamProcessor
from src.neo4j.connection import Neo4jConnection
from src.neo4j.loader import GraphDataLoader
from src.fraud_detection.cypher_detector import CypherFraudDetector
from src.graph_algorithms.gds_runner import GDSRunner
from src.risk_scoring.engine import RiskScoringEngine
from src.alerts.alert_manager import AlertManager
from src.kafka.producer import KafkaProducerClient

from dashboard.components.metrics_summary import render_metrics_summary
from dashboard.components.overview_charts import render_overview_charts
from dashboard.components.network_graph import render_network_graph
from dashboard.components.risk_table import render_risk_table
from dashboard.components.alerts_view import render_alerts_view


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FinGraph Analytics | Real-Time Fraud & AML Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HIGH CONTRAST DARK ENTERPRISE CSS
# ============================================================

css_styles = textwrap.dedent("""
<style>
    /* Streamlit Default Header Bar Background Overrides */
    header[data-testid="stHeader"] {
        background-color: #0B0F17 !important;
    }

    /* Dark Theme Main Background */
    .stApp {
        background-color: #0B0F17 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #F8FAFC !important;
    }

    /* Container Top Padding & Max Width */
    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem;
    }

    /* Headings Global Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 750 !important;
    }

    p, span, label {
        color: #CBD5E1;
    }

    /* Dark Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #F8FAFC !important;
    }

    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
    }

    /* Dataframe Dark Mode Override */
    [data-testid="stDataFrame"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    /* Primary Accent Buttons */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 650 !important;
        min-height: 42px !important;
        transition: background-color 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
        padding: 6px !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 650 !important;
        color: #CBD5E1 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    /* Dividers */
    hr {
        border-color: #1E293B !important;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #64748B;
        font-size: 0.82rem;
        padding: 24px 0 8px 0;
    }
</style>
""")

st.markdown(css_styles, unsafe_allow_html=True)


# ============================================================
# MAIN HEADER (High Contrast & Visible Padding)
# ============================================================

header_html = textwrap.dedent("""
<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 4px; padding-bottom: 8px;">
    <div>
        <div style="font-size: 2.1rem; font-weight: 850; color: #FFFFFF; display: flex; align-items: center; gap: 12px; letter-spacing: -0.02em;">
            🛡️ FinGraph Analytics
        </div>
        <div style="font-size: 0.95rem; color: #94A3B8; margin-top: 4px; font-weight: 500;">
            Real-Time Fraud & AML Intelligence Platform
        </div>
    </div>
    <div style="background-color: #064E3B; color: #34D399; border: 1px solid #059669; padding: 7px 16px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; gap: 8px;">
        <span style="height: 9px; width: 9px; background-color: #34D399; border-radius: 50%; display: inline-block;"></span>
        Pipeline Online
    </div>
</div>
""")

st.markdown(header_html, unsafe_allow_html=True)
st.markdown("---")


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

if "scored_accounts" not in st.session_state:
    st.session_state["scored_accounts"] = []

if "fraud_patterns" not in st.session_state:
    st.session_state["fraud_patterns"] = []

if "alerts" not in st.session_state:
    st.session_state["alerts"] = []

if "frozen_accounts" not in st.session_state:
    st.session_state["frozen_accounts"] = set()


# ============================================================
# SIDEBAR CONTROLS & REAL-TIME SYSTEM STATUS
# ============================================================

st.sidebar.title("FinGraph Controls")
st.sidebar.caption("Configure transaction stream and execute analytics pipeline.")
st.sidebar.divider()

st.sidebar.markdown("<div style='font-size:0.75rem; font-weight:700; color:#94A3B8; letter-spacing:0.08em; text-transform:uppercase;'>PIPELINE CONTROLS</div>", unsafe_allow_html=True)

batch_size = st.sidebar.slider(
    "Simulation Batch Size",
    min_value=20,
    max_value=200,
    value=60,
    step=10,
    help="Number of transaction events generated per batch."
)

fraud_ratio = st.sidebar.slider(
    "Fraud Syndicate Ratio",
    min_value=0.10,
    max_value=0.80,
    value=0.35,
    step=0.05,
    help="Ratio of fraud syndicate patterns (Smurfing, Starburst, Circular Flows) in generated stream."
)

st.sidebar.divider()

# Check Real-Time Infrastructure Connectivity
conn_check = Neo4jConnection()
is_neo4j_live = conn_check.is_connected
conn_check.close()

kafka_check = KafkaProducerClient()
is_kafka_live = kafka_check.producer is not None
kafka_check.close()

st.sidebar.markdown("<div style='font-size:0.75rem; font-weight:700; color:#94A3B8; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:8px;'>SYSTEM STATUS</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600;'>● Simulator — Ready</div>", unsafe_allow_html=True)

if is_kafka_live:
    st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600; margin-top:4px;'>● Stream Processor — Ready (Live Kafka)</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600; margin-top:4px;'>● Stream Processor — Ready (Standalone Stream)</div>", unsafe_allow_html=True)

if is_neo4j_live:
    st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600; margin-top:4px;'>● Graph Engine — Ready (Live Neo4j Cluster)</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600; margin-top:4px;'>● Graph Engine — Ready (Local Graph Engine)</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div style='color:#34D399; font-size:0.85rem; font-weight:600; margin-top:4px;'>● Risk Engine — Ready (PageRank & GDS)</div>", unsafe_allow_html=True)

st.sidebar.divider()


# ============================================================
# PIPELINE EXECUTION FUNCTION
# ============================================================

def run_pipeline_execution():
    """Executes full end-to-end analytics pipeline."""
    with st.spinner("Executing FinGraph Analytics Pipeline (Simulator → Flink → Graph → GDS → Risk Engine)..."):
        # 1. Generate Transactions
        generator = TransactionGenerator()
        raw_transactions = generator.generate_batch(count=batch_size, fraud_ratio=fraud_ratio)

        # 2. Process via Flink Stream Processor
        flink_processor = TransactionStreamProcessor()
        processed_transactions = [flink_processor.process_record(t) for t in raw_transactions]

        # 3. Load into Graph Engine (Neo4j / Fallback)
        conn = Neo4jConnection()
        loader = GraphDataLoader(conn)
        loader.ingest_batch(processed_transactions)

        # 4. Run Cypher Fraud Detection
        detector = CypherFraudDetector(conn, loader.local_graph)
        circular_flows = detector.detect_circular_flows()
        starburst_hubs = detector.detect_starburst_hubs()
        multihop_layering = detector.detect_multihop_layering()
        fraud_patterns = circular_flows + starburst_hubs + multihop_layering

        # 5. Run Graph Data Science Algorithms (PageRank, WCC, Louvain)
        gds = GDSRunner(conn, loader.local_graph)
        gds_results = gds.run_gds_pipeline()

        # 6. Compute Explainable Risk Scores
        risk_engine = RiskScoringEngine(high_risk_threshold=75.0)
        scored_accounts = risk_engine.score_all_accounts(gds_results, fraud_patterns)

        # 7. Generate Alerts
        alert_manager = AlertManager()
        alerts = alert_manager.evaluate_high_risk_accounts(scored_accounts)

        # Save to Session State
        st.session_state["transactions"] = processed_transactions
        st.session_state["scored_accounts"] = scored_accounts
        st.session_state["fraud_patterns"] = fraud_patterns
        st.session_state["alerts"] = alerts

        conn.close()


if st.sidebar.button("🚀 Run Pipeline Simulation", type="primary", use_container_width=True):
    run_pipeline_execution()
    st.sidebar.success("Pipeline execution completed successfully.")


# Initial Data Load Check
if not st.session_state["transactions"]:
    run_pipeline_execution()


# ============================================================
# EXECUTIVE KPI SUMMARY
# ============================================================

render_metrics_summary(
    st.session_state["transactions"],
    st.session_state["scored_accounts"],
    st.session_state["fraud_patterns"],
)


# ============================================================
# MAIN NAVIGATION TABS
# ============================================================

st.divider()

tab_overview, tab_network, tab_risk, tab_alerts = st.tabs(
    [
        "📈 Overview",
        "🕸️ Network Analysis",
        "📊 Risk Intelligence",
        "🚨 Fraud Alerts",
    ]
)


# ------------------------------------------------------------
# TAB 1 — OVERVIEW
# ------------------------------------------------------------
with tab_overview:
    render_overview_charts(
        st.session_state["transactions"],
        st.session_state["scored_accounts"],
        st.session_state["fraud_patterns"],
    )


# ------------------------------------------------------------
# TAB 2 — NETWORK ANALYSIS
# ------------------------------------------------------------
with tab_network:
    render_network_graph(
        st.session_state["transactions"],
        st.session_state["scored_accounts"],
    )


# ------------------------------------------------------------
# TAB 3 — RISK INTELLIGENCE
# ------------------------------------------------------------
with tab_risk:
    render_risk_table(
        st.session_state["scored_accounts"]
    )


# ------------------------------------------------------------
# TAB 4 — FRAUD ALERTS
# ------------------------------------------------------------
with tab_alerts:
    render_alerts_view(
        st.session_state["alerts"]
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_html = textwrap.dedent("""
<div class="footer-text">
    <strong style="color:#CBD5E1;">FinGraph Analytics</strong> &nbsp;•&nbsp; Real-Time Fraud & AML Intelligence Platform
    <br>
    Powered by Kafka • Flink • Neo4j • Graph Data Science • Enterprise Dark Edition
</div>
""")

st.markdown(footer_html, unsafe_allow_html=True)