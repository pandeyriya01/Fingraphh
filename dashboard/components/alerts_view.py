"""
FinGraph – Professional Fraud Alerts & Response Center (Dark Theme)
Displays real-time fraud alert stream with severity tags and account freezing actions.
"""

import textwrap
import streamlit as st
from typing import List, Dict, Any
from datetime import datetime, timezone


def render_alerts_view(alerts: List[Dict[str, Any]]):
    """Render real-time fraud alert center."""

    # ------------------------------------------------------------
    # Section Header (Dedented HTML)
    # ------------------------------------------------------------
    header_html = textwrap.dedent("""
    <div style="margin-bottom: 16px;">
        <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; color: #94A3B8; text-transform: uppercase;">
            INCIDENT RESPONSE
        </div>
        <div style="font-size: 1.35rem; font-weight: 750; color: #F8FAFC; margin-top: 2px;">
            Fraud Alert Center & Incident Management
        </div>
        <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 2px;">
            Real-time automated alerts triggered when account graph risk scores exceed compliance thresholds.
        </div>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # Maintain frozen accounts state in streamlit session_state
    if "frozen_accounts" not in st.session_state:
        st.session_state["frozen_accounts"] = set()

    if not alerts:
        st.success("🟢 No high-risk fraud alerts active at this moment. All monitored account scores are within normal operational thresholds.")
        return

    st.warning(f"⚠️ **{len(alerts)} High-Risk Fraud Alerts** require immediate AML analyst review.")

    for idx, alert in enumerate(alerts):
        acc_id = str(alert.get("account_id", f"ACC_{idx}"))
        risk_score = float(alert.get("risk_score", 0.0))
        risk_level = str(alert.get("risk_level", "HIGH RISK")).upper()
        is_frozen = acc_id in st.session_state["frozen_accounts"]

        status_text = "FROZEN ❄️" if is_frozen else "ACTIVE ALERT 🚨"

        with st.expander(
            f"ALERT #{idx+1:02d} | Account: {acc_id} | Risk Score: {risk_score:.1f} | Status: {status_text}",
            expanded=(idx < 3),
        ):
            col1, col2 = st.columns([3, 1], gap="medium")

            with col1:
                st.markdown(f"**Account ID:** `{acc_id}`")
                st.markdown(f"**Risk Score:** `{risk_score:.1f} / 100.0` &nbsp; ({risk_level})")
                st.markdown(f"**Detection Timestamp:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`")

                reasons = alert.get("reasons", ["High graph centrality and suspicious transaction velocity"])
                if isinstance(reasons, str):
                    reasons = [reasons]

                st.markdown("**Contributing Risk Factors:**")
                for r in reasons:
                    st.markdown(f"- 🔴 `{r}`")

            with col2:
                st.markdown("**Action Panel:**")

                if is_frozen:
                    st.success("❄️ ACCOUNT FROZEN")
                    st.caption("Transactions blocked by compliance team.")
                else:
                    if st.button("🔒 Freeze Account", key=f"freeze_btn_{acc_id}_{idx}", type="primary"):
                        st.session_state["frozen_accounts"].add(acc_id)
                        st.success(f"Account {acc_id} has been FROZEN successfully.")
                        st.rerun()
