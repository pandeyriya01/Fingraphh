"""
FinGraph – Professional Financial Network Graph (Dark Theme)
Interactive fraud syndicate visualization using PyVis.
"""

import html
import tempfile
import textwrap
from typing import List, Dict, Any

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network


def render_network_graph(
    transactions: List[Dict[str, Any]],
    scored_accounts: List[Dict[str, Any]],
):
    """Render interactive financial transaction network with filters."""

    # ------------------------------------------------------------
    # Section Header (Dedented HTML)
    # ------------------------------------------------------------
    header_html = textwrap.dedent("""
    <div style="margin-bottom: 16px;">
        <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; color: #94A3B8; text-transform: uppercase;">
            NETWORK INTELLIGENCE
        </div>
        <div style="font-size: 1.35rem; font-weight: 750; color: #F8FAFC; margin-top: 2px;">
            Financial Transaction Network Graph
        </div>
        <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 2px;">
            Interactive topological view of account relationships and money laundering flows.
        </div>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Filter Controls
    # ------------------------------------------------------------
    filter_col1, filter_col2, filter_col3 = st.columns(3, gap="medium")

    with filter_col1:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            options=["All Levels", "HIGH RISK", "MEDIUM RISK", "LOW RISK"],
            index=0,
        )

    with filter_col2:
        pattern_options = ["All Patterns"] + sorted(
            list(set(str(t.get("pattern_type", "NORMAL")).upper() for t in transactions))
        )
        pattern_filter = st.selectbox(
            "Filter by Pattern Tag",
            options=pattern_options,
            index=0,
        )

    with filter_col3:
        max_amount = max([float(t.get("amount", 0.0)) for t in transactions] + [10000.0])
        min_amount = st.slider(
            "Min Transaction Amount ($)",
            min_value=0,
            max_value=int(max_amount),
            value=0,
            step=500,
        )

    # Apply Filters to Transactions
    filtered_txns = []
    for txn in transactions:
        amt = float(txn.get("amount", txn.get("Amount", 0.0)))
        pattern = str(txn.get("pattern_type", "NORMAL")).upper()

        if amt < min_amount:
            continue
        if pattern_filter != "All Patterns" and pattern != pattern_filter:
            continue

        filtered_txns.append(txn)

    # ------------------------------------------------------------
    # Summary Bar
    # ------------------------------------------------------------
    account_ids = set()
    suspicious_count = 0
    total_volume = 0.0

    for txn in filtered_txns:
        sender = txn.get("sender_account", txn.get("Sender", ""))
        receiver = txn.get("receiver_account", txn.get("Receiver", ""))
        if sender:
            account_ids.add(str(sender))
        if receiver:
            account_ids.add(str(receiver))
        if txn.get("is_suspicious"):
            suspicious_count += 1
        try:
            total_volume += float(txn.get("amount", txn.get("Amount", 0.0)))
        except (TypeError, ValueError):
            pass

    stat1, stat2, stat3, stat4 = st.columns(4)
    with stat1:
        st.metric("Network Accounts", f"{len(account_ids):,}")
    with stat2:
        st.metric("Transactions", f"{len(filtered_txns):,}")
    with stat3:
        st.metric("Suspicious Transfers", f"{suspicious_count:,}")
    with stat4:
        st.metric("Network Volume", f"${total_volume:,.2f}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Graph Container & Legend
    # ------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            "**Legend:** &nbsp;&nbsp; 🔴 **High Risk** &nbsp;&nbsp;|&nbsp;&nbsp; 🟠 **Medium Risk** &nbsp;&nbsp;|&nbsp;&nbsp; 🟢 **Low Risk** &nbsp;&nbsp;|&nbsp;&nbsp; 🛑 **Suspicious Transfer Edge**",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # PyVis Network Configuration (Dark Canvas)
        net = Network(
            height="580px",
            width="100%",
            bgcolor="#0F172A",
            font_color="#F8FAFC",
            directed=True,
            notebook=False,
        )

        net.force_atlas_2based(
            gravity=-35,
            central_gravity=0.01,
            spring_length=150,
            spring_strength=0.08,
            damping=0.4,
        )

        risk_map = {str(a.get("account_id")): a for a in scored_accounts if a.get("account_id")}

        added_nodes = set()

        for txn in filtered_txns:
            sender = str(txn.get("sender_account", txn.get("Sender", "")))
            receiver = str(txn.get("receiver_account", txn.get("Receiver", "")))

            for node_id in [sender, receiver]:
                if not node_id or node_id in added_nodes:
                    continue

                account_info = risk_map.get(node_id, {})
                risk_level = str(account_info.get("risk_level", "LOW RISK")).upper()
                risk_score = account_info.get("risk_score", 0.0)

                # Filter node by risk level if selected
                if risk_filter != "All Levels":
                    if "HIGH" in risk_filter and "HIGH" not in risk_level:
                        continue
                    if "MEDIUM" in risk_filter and "MEDIUM" not in risk_level:
                        continue
                    if "LOW" in risk_filter and "LOW" not in risk_level:
                        continue

                if "HIGH" in risk_level:
                    node_color = {"background": "#EF4444", "border": "#991B1B", "highlight": {"background": "#F87171", "border": "#7F1D1D"}}
                    node_size = 28
                elif "MEDIUM" in risk_level:
                    node_color = {"background": "#F97316", "border": "#9A3412", "highlight": {"background": "#FB923C", "border": "#7C2D12"}}
                    node_size = 22
                else:
                    node_color = {"background": "#22C55E", "border": "#166534", "highlight": {"background": "#4ADE80", "border": "#14532D"}}
                    node_size = 16

                reasons = account_info.get("reasons", ["No suspicious indicators"])
                if not isinstance(reasons, list):
                    reasons = [str(reasons)]

                safe_reasons = "<br>• ".join(html.escape(str(reason)) for reason in reasons)
                safe_node_id = html.escape(node_id)

                tooltip = (
                    f"<b>Account ID:</b> {safe_node_id}<br>"
                    f"<b>Risk Score:</b> {risk_score} / 100.0<br>"
                    f"<b>Risk Level:</b> {html.escape(risk_level)}<br><br>"
                    f"<b>Risk Factors:</b><br>• {safe_reasons}"
                )

                net.add_node(
                    node_id,
                    label=node_id,
                    title=tooltip,
                    color=node_color,
                    size=node_size,
                    borderWidth=2,
                    font={"color": "#F8FAFC", "size": 13, "face": "Arial"},
                )

                added_nodes.add(node_id)

        # Add edges
        for txn in filtered_txns:
            sender = str(txn.get("sender_account", txn.get("Sender", "")))
            receiver = str(txn.get("receiver_account", txn.get("Receiver", "")))

            if not sender or not receiver or sender not in added_nodes or receiver not in added_nodes:
                continue

            try:
                amount = float(txn.get("amount", txn.get("Amount", 0.0)))
            except (TypeError, ValueError):
                amount = 0.0

            pattern = str(txn.get("pattern_type", "NORMAL"))
            suspicious = bool(txn.get("is_suspicious", False))

            if suspicious:
                edge_color = {"color": "#EF4444", "highlight": "#F87171", "hover": "#DC2626"}
            else:
                edge_color = {"color": "#475569", "highlight": "#94A3B8", "hover": "#64748B"}

            txn_id = html.escape(str(txn.get("transaction_id", "N/A")))
            safe_pattern = html.escape(pattern)

            edge_title = (
                f"<b>Txn ID:</b> {txn_id}<br>"
                f"<b>Amount:</b> ${amount:,.2f}<br>"
                f"<b>Pattern:</b> {safe_pattern}"
            )

            net.add_edge(
                sender,
                receiver,
                value=max(1, min(amount / 2000.0, 8)),
                title=edge_title,
                color=edge_color,
                arrows="to",
            )

        net.set_options("""
        {
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "zoomView": true
          },
          "physics": {
            "enabled": true,
            "stabilization": { "enabled": true, "iterations": 120 }
          },
          "edges": {
            "smooth": { "type": "dynamic" },
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } }
          },
          "nodes": { "shape": "dot", "borderWidth": 2 }
        }
        """)

        if not added_nodes:
            st.info("No network accounts match the selected filter criteria.")
        else:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                    temp_path = tmp.name

                net.save_graph(temp_path)

                with open(temp_path, "r", encoding="utf-8") as file:
                    html_content = file.read()

                components.html(html_content, height=600, scrolling=False)
            except Exception as error:
                st.error("Unable to render the financial network graph.")
                st.caption(f"Technical details: {error}")