"""
FinGraph – Professional Risk Intelligence Table (Dark Theme)
Enterprise risk leaderboard with explainable risk scores and recommended compliance actions.
"""

import textwrap
import pandas as pd
import streamlit as st
from typing import List, Dict, Any


def render_risk_table(scored_accounts: List[Dict[str, Any]]):
    """Render enterprise risk intelligence table."""

    # ------------------------------------------------------------
    # Section Header (Dedented HTML)
    # ------------------------------------------------------------
    header_html = textwrap.dedent("""
    <div style="margin-bottom: 16px;">
        <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; color: #94A3B8; text-transform: uppercase;">
            RISK MONITORING
        </div>
        <div style="font-size: 1.35rem; font-weight: 750; color: #F8FAFC; margin-top: 2px;">
            Account Risk Intelligence & Leaderboard
        </div>
        <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 2px;">
            Composite graph topology scores, centrality metrics, and automated compliance recommendations.
        </div>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    if not scored_accounts:
        st.info("No account risk scores available in the current dataset.")
        return

    # Filter Controls
    col_search, col_filter = st.columns([2, 1])

    with col_search:
        search_query = st.text_input("Search Account ID", value="", placeholder="Enter account ID (e.g. ACC_001)...")

    with col_filter:
        risk_tier_filter = st.selectbox(
            "Filter by Tier",
            options=["All Tiers", "HIGH RISK", "MEDIUM RISK", "LOW RISK"],
            index=0,
        )

    # Process accounts into display DataFrame
    table_rows = []
    for acc in scored_accounts:
        acc_id = str(acc.get("account_id", "N/A"))
        risk_score = float(acc.get("risk_score", 0.0))
        risk_tier = str(acc.get("risk_level", "LOW RISK")).upper()

        if search_query and search_query.lower() not in acc_id.lower():
            continue
        if risk_tier_filter != "All Tiers":
            if "HIGH" in risk_tier_filter and "HIGH" not in risk_tier:
                continue
            if "MEDIUM" in risk_tier_filter and "MEDIUM" not in risk_tier:
                continue
            if "LOW" in risk_tier_filter and "LOW" not in risk_tier:
                continue

        reasons = acc.get("reasons", ["Normal transaction behavior"])
        if isinstance(reasons, list):
            reasons_str = "; ".join(reasons)
        else:
            reasons_str = str(reasons)

        # Recommended Action Logic
        if "HIGH" in risk_tier:
            recommended_action = "🚨 FREEZE & INVESTIGATE"
        elif "MEDIUM" in risk_tier:
            recommended_action = "⚠️ ENHANCED MONITORING"
        else:
            recommended_action = "🟢 ROUTINE MONITORING"

        table_rows.append(
            {
                "Account ID": acc_id,
                "Risk Score": risk_score,
                "Risk Tier": risk_tier,
                "PageRank": float(acc.get("pagerank", 0.0)),
                "WCC Cluster": int(acc.get("wcc_component_id", 0)),
                "Louvain Community": int(acc.get("louvain_community_id", 0)),
                "Risk Indicators": reasons_str,
                "Recommended Action": recommended_action,
            }
        )

    if not table_rows:
        st.info("No accounts match the specified search or filter criteria.")
        return

    df = pd.DataFrame(table_rows)

    st.dataframe(
        df,
        column_config={
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score (0-100)",
                help="Composite topology and AML risk score",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
            "PageRank": st.column_config.NumberColumn(
                "PageRank",
                format="%.4f",
            ),
        },
        use_container_width=True,
        hide_index=True,
    )
