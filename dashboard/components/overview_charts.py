"""
FinGraph – Executive Overview Charts (Dark Theme)
Interactive Plotly charts inspired by enterprise fintech dashboards.
"""

import textwrap
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import List, Dict, Any


def render_overview_charts(
    transactions: List[Dict[str, Any]],
    scored_accounts: List[Dict[str, Any]],
    fraud_patterns: List[Dict[str, Any]],
):
    """Render dark-themed executive overview charts and recent suspicious activity."""

    # ------------------------------------------------------------
    # 1. Real-Time Transaction Volume Trend (Area Chart)
    # ------------------------------------------------------------
    st.markdown(
        textwrap.dedent("""
        <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem; margin-bottom: 8px;">
            Real-Time Transaction Activity & Volume Stream
        </div>
        """),
        unsafe_allow_html=True,
    )

    if transactions:
        df_txns = pd.DataFrame(transactions)
        if "amount" in df_txns.columns:
            df_txns["amount"] = pd.to_numeric(df_txns["amount"], errors="coerce").fillna(0.0)
        else:
            df_txns["amount"] = 0.0

        df_txns["Index"] = range(1, len(df_txns) + 1)

        fig_trend = px.area(
            df_txns,
            x="Index",
            y="amount",
            labels={"Index": "Transaction Sequence", "amount": "Volume ($USD)"},
            color_discrete_sequence=["#38BDF8"],
        )
        fig_trend.update_traces(
            line=dict(width=2.5),
            fillcolor="rgba(56, 189, 248, 0.15)",
        )
        fig_trend.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=260,
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
            font=dict(color="#94A3B8"),
            xaxis=dict(gridcolor="#334155", title="Transaction Event Index"),
            yaxis=dict(gridcolor="#334155", title="Amount (USD)"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    # ------------------------------------------------------------
    # 2. Risk Level Distribution (Donut Chart)
    # ------------------------------------------------------------
    with col1:
        st.markdown(
            textwrap.dedent("""
            <div style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem; margin-bottom: 8px;">
                Account Risk Breakdown
            </div>
            """),
            unsafe_allow_html=True,
        )

        risk_counts = {"HIGH RISK": 0, "MEDIUM RISK": 0, "LOW RISK": 0}
        for acc in scored_accounts:
            level = str(acc.get("risk_level", "LOW RISK")).upper()
            if "HIGH" in level:
                risk_counts["HIGH RISK"] += 1
            elif "MEDIUM" in level:
                risk_counts["MEDIUM RISK"] += 1
            else:
                risk_counts["LOW RISK"] += 1

        df_risk = pd.DataFrame(
            {
                "Risk Tier": list(risk_counts.keys()),
                "Count": list(risk_counts.values()),
            }
        )

        fig_donut = px.pie(
            df_risk,
            names="Risk Tier",
            values="Count",
            hole=0.6,
            color="Risk Tier",
            color_discrete_map={
                "HIGH RISK": "#EF4444",
                "MEDIUM RISK": "#F97316",
                "LOW RISK": "#22C55E",
            },
        )
        fig_donut.update_traces(
            textinfo="percent+value",
            textfont_size=13,
            textfont_color="#FFFFFF",
            marker=dict(line=dict(color="#1E293B", width=2)),
        )
        fig_donut.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=260,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5, font=dict(color="#94A3B8")),
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    # ------------------------------------------------------------
    # 3. Fraud Pattern Composition (Bar Chart)
    # ------------------------------------------------------------
    with col2:
        st.markdown(
            textwrap.dedent("""
            <div style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem; margin-bottom: 8px;">
                Detected Fraud Syndicate Patterns
            </div>
            """),
            unsafe_allow_html=True,
        )

        pattern_counts = {}
        for pattern in fraud_patterns:
            p_type = str(pattern.get("pattern", pattern.get("pattern_type", "UNKNOWN"))).replace("_", " ").title()
            pattern_counts[p_type] = pattern_counts.get(p_type, 0) + 1

        if not pattern_counts:
            pattern_counts = {"No Patterns Detected": 0}

        df_patterns = pd.DataFrame(
            {
                "Pattern": list(pattern_counts.keys()),
                "Occurrences": list(pattern_counts.values()),
            }
        )

        fig_bar = px.bar(
            df_patterns,
            x="Occurrences",
            y="Pattern",
            orientation="h",
            color="Pattern",
            color_discrete_sequence=["#3B82F6", "#818CF8", "#10B981", "#F59E0B"],
        )
        fig_bar.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=260,
            showlegend=False,
            font=dict(color="#94A3B8"),
            xaxis=dict(title="Count", gridcolor="#334155"),
            yaxis=dict(title="", gridcolor="#334155"),
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------------------------------------------------
    # 4. Recent Suspicious Activity Table
    # ------------------------------------------------------------
    st.markdown(
        textwrap.dedent("""
        <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem; margin-top: 16px; margin-bottom: 8px;">
            Recent Suspicious Transactions Feed
        </div>
        """),
        unsafe_allow_html=True,
    )

    suspicious_txns = [t for t in transactions if t.get("is_suspicious")]

    if not suspicious_txns:
        st.info("🟢 No suspicious transactions detected in the current stream batch.")
    else:
        df_susp = pd.DataFrame(suspicious_txns).head(10)

        display_cols = []
        col_rename = {}

        if "transaction_id" in df_susp.columns:
            display_cols.append("transaction_id")
            col_rename["transaction_id"] = "Transaction ID"
        if "sender_account" in df_susp.columns:
            display_cols.append("sender_account")
            col_rename["sender_account"] = "Sender Account"
        if "receiver_account" in df_susp.columns:
            display_cols.append("receiver_account")
            col_rename["receiver_account"] = "Receiver Account"
        if "amount" in df_susp.columns:
            display_cols.append("amount")
            col_rename["amount"] = "Amount (USD)"
        if "pattern_type" in df_susp.columns:
            display_cols.append("pattern_type")
            col_rename["pattern_type"] = "Pattern Tag"
        if "sender_ip" in df_susp.columns:
            display_cols.append("sender_ip")
            col_rename["sender_ip"] = "Origin IP"

        df_display = df_susp[display_cols].rename(columns=col_rename)

        st.dataframe(
            df_display,
            column_config={
                "Amount (USD)": st.column_config.NumberColumn(
                    "Amount (USD)",
                    format="$%.2f",
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
