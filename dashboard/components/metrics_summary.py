"""
FinGraph – Executive Dashboard Metrics (Dark Theme)
Professional KPI cards for AML & fraud risk analysts.
"""

import textwrap
import streamlit as st
from typing import List, Dict, Any


def render_metrics_summary(
    transactions: List[Dict[str, Any]],
    scored_accounts: List[Dict[str, Any]],
    fraud_patterns: List[Dict[str, Any]],
):
    """Render executive-level KPI metrics."""

    # ------------------------------------------------------------
    # Calculate metrics
    # ------------------------------------------------------------
    total_txns = len(transactions)

    total_vol = sum(
        float(
            transaction.get(
                "amount",
                transaction.get("Amount", 0.0)
            )
        )
        for transaction in transactions
    )

    high_risk_count = sum(
        1
        for account in scored_accounts
        if str(account.get("risk_level", "")).upper()
        in {"HIGH RISK", "HIGH"}
    )

    medium_risk_count = sum(
        1
        for account in scored_accounts
        if str(account.get("risk_level", "")).upper()
        in {"MEDIUM RISK", "MEDIUM"}
    )

    syndicates_count = len(fraud_patterns)

    # ------------------------------------------------------------
    # Section Heading (Unindented to prevent Streamlit Markdown code block parsing)
    # ------------------------------------------------------------
    heading_html = textwrap.dedent("""
    <div style="margin: 4px 0 16px 0;">
        <div style="color: #94A3B8; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
            SYSTEM MONITORING
        </div>
        <div style="color: #F8FAFC; font-size: 1.4rem; font-weight: 750; margin-top: 2px;">
            Transaction & Risk Overview
        </div>
        <div style="color: #94A3B8; font-size: 0.88rem; margin-top: 2px;">
            Live indicators from the current streaming fraud analytics pipeline.
        </div>
    </div>
    """)
    st.markdown(heading_html, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # KPI cards
    # ------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    # Total Transactions
    with col1:
        st.metric(
            label="TOTAL TRANSACTIONS",
            value=f"{total_txns:,}",
            help="Total number of financial transactions processed in the current stream batch."
        )
        st.caption("Stream processed")

    # Total Volume
    with col2:
        st.metric(
            label="TOTAL VOLUME (USD)",
            value=f"${total_vol:,.2f}",
            help="Total monetary volume of processed transactions."
        )
        st.caption("Processed value")

    # High Risk Accounts
    with col3:
        st.metric(
            label="HIGH-RISK ACCOUNTS",
            value=f"{high_risk_count:,}",
            delta=f"{high_risk_count} Flagged" if high_risk_count > 0 else "Clean",
            delta_color="inverse" if high_risk_count > 0 else "normal",
            help="Accounts classified as HIGH RISK (Score >= 75)."
        )
        if high_risk_count > 0:
            st.caption("🔴 Requires immediate review")
        else:
            st.caption("🟢 No high-risk accounts")

    # Fraud Syndicates
    with col4:
        st.metric(
            label="FRAUD SYNDICATES",
            value=f"{syndicates_count:,}",
            delta=f"{syndicates_count} Active" if syndicates_count > 0 else "Clean",
            delta_color="inverse" if syndicates_count > 0 else "normal",
            help="Suspicious fraud patterns (Smurfing, Starburst, Circular Flows, Layering)."
        )
        if syndicates_count > 0:
            st.caption(f"⚠️ {syndicates_count} active clusters")
        else:
            st.caption("🟢 No suspicious clusters")

    # ------------------------------------------------------------
    # Risk monitoring summary bar
    # ------------------------------------------------------------
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.caption("📊 **STATUS BREAKDOWN**")

    with summary_col2:
        st.caption(f"🔴 High Risk: **{high_risk_count}**")

    with summary_col3:
        st.caption(f"🟠 Medium Risk: **{medium_risk_count}**")

    with summary_col4:
        st.caption(f"🔷 Active Syndicates: **{syndicates_count}**")