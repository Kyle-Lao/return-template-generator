
import streamlit as st
import json
import os
from datetime import date

POLICY_DB = "policies.json"

if os.path.exists(POLICY_DB):
    with open(POLICY_DB, "r") as f:
        policies = json.load(f)
else:
    policies = {}

st.set_page_config(page_title="Policy Onboarding", layout="centered")
st.title("📥 Life Settlement Policy Onboarding")

if "step" not in st.session_state:
    st.session_state.step = 1
if "policy_inputs" not in st.session_state:
    st.session_state.policy_inputs = {}
if "premium_years" not in st.session_state:
    st.session_state.premium_years = []

# Step 1: collect policy metadata
if st.session_state.step == 1:
    with st.form("step1_form"):
        st.subheader("Step 1: Policy Information")
        insured_name = st.text_input("Insured’s Full Name")
        dob = st.date_input("Date of Birth")
        carrier = st.text_input("Carrier Name")
        le_months = st.number_input("Life Expectancy at Report Generation (months)", min_value=1, step=1)
        le_report_date = st.date_input("LE Report Generation Date")
        death_benefit = st.number_input("Death Benefit", step=1000.0)
        submitted = st.form_submit_button("Next: Enter Premiums")

    if submitted:
        remaining_years = (int(le_months + 11) // 12) + 3
        start_year = max(le_report_date.year, date.today().year)
        years = [start_year + i for i in range(remaining_years)]

        st.session_state.policy_inputs = {
            "insured_name": insured_name,
            "dob": str(dob),
            "carrier": carrier,
            "le_months": int(le_months),
            "le_report_date": str(le_report_date),
            "death_benefit": death_benefit,
        }
        st.session_state.premium_years = years
        st.session_state.step = 2
        st.rerun()

# Step 2: input monthly premiums per year
if st.session_state.step == 2:
    st.subheader("Step 2: Monthly Premiums by Year")
    st.markdown("Paste one premium per line (up to 12 per year). Dollar signs and commas are okay.")

    premium_inputs = {}
    for year in st.session_state.premium_years:
        premium_inputs[year] = st.text_area(f"Premiums for {year}", key=str(year), height=150)

    if st.button("Save Policy"):
        def parse_premiums(inputs_dict):
            premiums = {}
            for year, val in inputs_dict.items():
                cleaned_lines = []
                for line in val.strip().splitlines():
                    line = line.strip().replace("$", "").replace(",", "")
                    if line:
                        try:
                            cleaned_lines.append(float(line))
                        except ValueError:
                            continue
                if cleaned_lines:
                    premiums[year] = cleaned_lines
            return premiums

        premiums = parse_premiums(premium_inputs)
        key = st.session_state.policy_inputs["insured_name"].lower().replace(" ", "_")

        if not premiums:
            st.error("❌ No premiums parsed. Please check your input.")
        else:
            policies[key] = {
                **st.session_state.policy_inputs,
                "monthly_premiums": premiums
            }
            with open(POLICY_DB, "w") as f:
                json.dump(policies, f, indent=2)
            st.success(f"✅ Policy for {st.session_state.policy_inputs['insured_name']} saved.")
