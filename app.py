import streamlit as st
import pandas as pd
import re
from utils.calculations import calculate_lod, calculate_gsd, model_resolution_control

st.set_page_config(page_title="GDT Assessment Tool", layout="wide")
st.markdown('<h1 class="main-title" style="color: #E5E1DA !important;">Geometric Digital Twin Assessment Tool</h1>', unsafe_allow_html=True)

# Add custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        color: #E5E1DA !important;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    /* Section headers */
    .section-title {
        color: #B3C8CF !important;
        font-size: 1.6rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    /* Other styles */
    h2 {
        color: #E5E1DA;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #B3C8CF;
        padding-bottom: 0.5rem;
        text-transform: none;
    }
    
    /* Subsection headers */
    h3 {
        color: #B3C8CF;
        font-size: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    /* Captions */
    .caption {
        color: #89A8B2;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Cards for metrics */
    .metric-card {
        background-color: #2C3E50;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #B3C8CF;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem;
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: #2C3E50;
        color: #E5E1DA;
        font-weight: 600;
        padding: 0.5rem;
        text-align: left;
        border-bottom: 2px solid #B3C8CF;
    }
    
    .dataframe td {
        padding: 0.5rem;
        border-bottom: 1px solid #B3C8CF;
        color: #E5E1DA;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #B3C8CF;
        color: #2C3E50;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #89A8B2;
        color: #E5E1DA;
    }
    
    /* Status indicators */
    .status-critical {
        background-color: #E74C3C;
        color: #E5E1DA;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-warning {
        background-color: #F39C12;
        color: #E5E1DA;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-partial {
        background-color: #F1C40F;
        color: #2C3E50;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-suitable {
        background-color: #27AE60;
        color: #E5E1DA;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Compact layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: #2C3E50;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        color: #E5E1DA;
        font-weight: bold;
        font-size: 1.3rem;
        min-width: 200px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background-color: #B3C8CF;
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #B3C8CF;
        color: #2C3E50;
    }
    
    .stTabs [aria-selected="true"]::after {
        transform: scaleX(1);
    }
    
    .stTabs [aria-selected="false"] {
        opacity: 0.7;
    }
    
    .stTabs [aria-selected="false"]:hover {
        opacity: 1;
    }
    
    .stTabs [aria-selected="false"]:hover::after {
        transform: scaleX(0.5);
    }
    
    /* Other styles */
    h2 {
        color: #34495e;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
        text-transform: none;
    }
    
    /* Subsection headers */
    h3 {
        color: #34495e;
        font-size: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    /* Captions */
    .caption {
        color: #95a5a6;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Cards for metrics */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem;
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: #f8f9fa;
        color: #2c3e50;
        font-weight: 600;
        padding: 0.5rem;
        text-align: left;
        border-bottom: 2px solid #ecf0f1;
    }
    
    .dataframe td {
        padding: 0.5rem;
        border-bottom: 1px solid #ecf0f1;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #B3C8CF;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #89A8B2;
    }
    
    /* Status indicators */
    .status-critical {
        background-color: #e74c3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-warning {
        background-color: #f39c12;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-partial {
        background-color: #f1c40f;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-suitable {
        background-color: #27ae60;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Compact layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: #F1F0E8;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        color: #000000;
        font-weight: bold;
        font-size: 1.3rem;
        min-width: 200px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background-color: #ffffff;
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #B3C8CF;
        color: #000000;
    }
    
    .stTabs [aria-selected="true"]::after {
        transform: scaleX(1);
    }
    
    .stTabs [aria-selected="false"] {
        opacity: 0.7;
    }
    
    .stTabs [aria-selected="false"]:hover {
        opacity: 1;
    }
    
    .stTabs [aria-selected="false"]:hover::after {
        transform: scaleX(0.5);
    }
</style>
""", unsafe_allow_html=True)

# Define data quality data lists
feature_dq_data = [
    {
        "Evaluation Category": "Category: Mandatory", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Accuracy", "Measure": "Positional absolute (external)",
        "Hint": "Alignment of the model with real-world context"
    },
    {
        "Evaluation Category": "Category: Mandatory", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Accuracy", "Measure": "Positional relative (internal)",
        "Hint": "Internal consistency of the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Commission", "Measure": "Excess items",
        "Hint": "Items are not correctly presented in the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Commission", "Measure": "Number of excess items",
        "Hint": "The number of items within the model that are incorrectly represented or should not have been included"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Commission", "Measure": "Rate of excess items",
        "Hint": "The number of incorrect items within the model relative to the total number of items represented"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Commission", "Measure": "Number of duplicate items",
        "Hint": "The total number of duplications within the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Omission", "Measure": "Missing items",
        "Hint": "Required items are missing in the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Omission", "Measure": "Number of missing items",
        "Hint": "The number of missing items that should have been presented in the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Completeness", "Sub-Type": "Sub-Type: Omission", "Measure": "Rate of missing items",
        "Hint": "The number of missing items in the model or sample relative to the total number of items represented"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Number of incorrectly classified items",
        "Hint": "The total number of incorrectly classified items"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Misclassification rate",
        "Hint": "The ratio of incorrectly classified items to the total number of items"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Interoperability", "Sub-Type": "Sub-Type: N/A", "Measure": "Data model compliance",
        "Hint": "Compliance with interoperability requirements"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Generalization", "Sub-Type": "Sub-Type: N/A", "Measure": "LoD compliance",
        "Hint": "The degree to which the model meets the required LoD"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Generalization", "Sub-Type": "Sub-Type: N/A", "Measure": "Number of generalization discrepancies",
        "Hint": "The total number of items not meeting the required LoD"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: N/A", "Measure": "Conceptual schema compliance",
        "Hint": "Items are compliant with the definitions or rules of the relevant conceptual schema"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: N/A", "Measure": "Number of items not compliant",
        "Hint": "The total number of items that are not compliant with the definitions or rules of the relevant conceptual schema"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: N/A", "Measure": "Not compliant rate",
        "Hint": "The number of items that are not compliant with the definitions or rules of the relevant conceptual schema relative to the total number of items"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Chronological order",
        "Hint": "The event is incorrectly ordered against the other event during the model updating process"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "The number of chronological errors",
        "Hint": "The total number of incorrectly ordered events"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Chronological error rate",
        "Hint": "The ratio of incorrectly ordered events to the total number of events during the model updating process"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Temporal consistency",
        "Hint": "The degree to which data is temporally consistent"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Temporal accuracy",
        "Hint": "Accuracy of the temporal attributes of the data"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Interoperability", "Sub-Type": "Sub-Type: N/A", "Measure": "Interoperability issues",
        "Hint": "Issues preventing seamless data exchange"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Generalization", "Sub-Type": "Sub-Type: N/A", "Measure": "Generalization discrepancy rate",
        "Hint": "The ratio of discrepancies to the total number of items"
    }
]

scale_dq_data = [
    {
        "Evaluation Category": "Category: Mandatory", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Accuracy", "Measure": "Positional absolute (external)",
        "Hint": "Alignment of the model with real-world context"
    },
    {
        "Evaluation Category": "Category: Mandatory", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Accuracy", "Measure": "Positional relative (internal)",
        "Hint": "Internal consistency of the model"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Interoperability", "Sub-Type": "Sub-Type: N/A", "Measure": "Data model compliance",
        "Hint": "Compliance with interoperability requirements"
    },
    {
        "Evaluation Category": "Category: Conditional", "DQ Type": "Type: Generalization", "Sub-Type": "Sub-Type: N/A", "Measure": "LoD compliance",
        "Hint": "The degree to which the model meets the required LoD"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "The number of chronological errors",
        "Hint": "The total number of incorrectly ordered events"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Chronological error rate",
        "Hint": "The ratio of incorrectly ordered events to the total number of events during the model updating process"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Temporal consistency",
        "Hint": "The degree to which data is temporally consistent"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Consistency", "Sub-Type": "Sub-Type: Temporal Quality", "Measure": "Temporal accuracy",
        "Hint": "Accuracy of the temporal attributes of the data"
    },
    {
        "Evaluation Category": "Category: Optional", "DQ Type": "Type: Interoperability", "Sub-Type": "Sub-Type: N/A", "Measure": "Interoperability issues",
        "Hint": "Issues preventing seamless data exchange"
    }
]

# Create tabs
tab1, tab2, tab3 = st.tabs(["Model G(0)", "Model G(t)", "Assessment Results"])

# Function to create the model assessment form
def create_model_assessment_form(tab_prefix=""):
    # --- 1. GDT Characteristics ---
    model_name = "Model G(0)" if tab_prefix == "g0" else "Model G(t)"
    st.markdown(f'<h1 class="section-title" style="font-size: 1.4rem;">{model_name}</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 1. Geometric Digital Twin (GDT) Characteristics</h2>', unsafe_allow_html=True)
    
    if tab_prefix == "g0":
        gdt_scale = st.selectbox("GDT Scale", ["Building Part", "Building", "Site", "Urban"], key=f"{tab_prefix}_gdt_scale")
    else:
        # For Model G(t), use the value from Model G(0)
        g0_scale = st.session_state.get("g0_gdt_scale", "Building Part")
        st.selectbox("GDT Scale", ["Building Part", "Building", "Site", "Urban"], key=f"{tab_prefix}_gdt_scale", index=["Building Part", "Building", "Site", "Urban"].index(g0_scale), disabled=True)
    
    gdt_scale_value = st.text_input("GDT Scale Value (optional)", key=f"{tab_prefix}_gdt_scale_value")
    gdt_stage = st.selectbox("Building Life Cycle Stage", ["Pre-construction", "Construction A5", "Use B1-B2", "Use B3-B5", "End of Life", "Beyond Life Cycle"], key=f"{tab_prefix}_gdt_stage")
    agr = st.number_input("Average Ground Resolution (AGR) of Model [mm/px]", format="%.3f", key=f"{tab_prefix}_agr")

    # --- 2. Sample Election ---
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 2. Sample for Evaluation</h2>', unsafe_allow_html=True)
    if tab_prefix == "g0":
        sample_type = st.radio("Sample Type", ["Feature-based", "Scale-based"], key=f"{tab_prefix}_sample_type")
    else:
        # For Model G(t), use the value from Model G(0)
        g0_sample_type = st.session_state.get("g0_sample_type", "Feature-based")
        st.radio("Sample Type", ["Feature-based", "Scale-based"], key=f"{tab_prefix}_sample_type", index=["Feature-based", "Scale-based"].index(g0_sample_type), disabled=True)
        sample_type = g0_sample_type

    if sample_type == "Feature-based":
        total_features = st.number_input("Total Number of Features (items)", min_value=0, value=0, key=f"{tab_prefix}_total_features")
    else:
        sample_scale = st.text_input("Sample Scale (optional)", key=f"{tab_prefix}_sample_scale")

    # --- 3. Parameters for Updating ---
    if tab_prefix == "g0":  # Only show this section in Model G(0) tab
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 3. Parameters for Updating</h2>', unsafe_allow_html=True)
        updates = st.number_input("Number of Previous Updates", min_value=0, key=f"{tab_prefix}_updates")
        schedule = st.selectbox("Update Schedule", ["Planned", "Event-driven"], key=f"{tab_prefix}_schedule")
        survey_type = st.selectbox("Survey Type", ["Image-based", "Range-based"], key=f"{tab_prefix}_survey_type")
        acq_sequence = st.selectbox("Data Acquisition Sequence", ["Parallel", "Sequential", "Mixed"], key=f"{tab_prefix}_acq_sequence")

    # --- 4. LoD Verification ---
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 4. LoD Verification</h2>', unsafe_allow_html=True)
    suggested_lod = calculate_lod(agr)
    st.markdown(f'<p style="color: #B3C8CF;"><strong>Suggested LoD:</strong> {suggested_lod}</p>', unsafe_allow_html=True)

    match = re.search(r'LoD (\d\.\d)', suggested_lod)
    if match:
        lod_value = float(match.group(1))
        if 2.1 <= lod_value <= 3.2:
            verified_lod = st.selectbox(
                "Verified LoD", [
                    "LoD 2.1", "LoD 2.2", "LoD 2.3", "LoD 3.0", "LoD 3.3", "LoD 4"
                ], key=f"{tab_prefix}_verified_lod"
            )
    
    # Add RMSE field
    st.markdown('<h3 style="font-size: 1.4rem;">Feature\'s RMSE (optional)</h3>', unsafe_allow_html=True)
    st.markdown("*RMSE of the actual dimensions of specific elements (e.g., roof elements, windows) between the model and real-world measurements obtained with more precise equipment*")
    rmse_value = st.number_input("Value", min_value=0.0, format="%.2f", key=f"{tab_prefix}_rmse_value")

    # --- 4.1 GSD & Model Resolution ---
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 4.1 Ground Sample Distance (GSD) Calculation</h2>', unsafe_allow_html=True)
    sensor_size = st.number_input("Sensor size (mm)", min_value=0.0, key=f"{tab_prefix}_sensor_size")
    focal_length = st.number_input("Focal length (mm)", min_value=0.0, key=f"{tab_prefix}_focal_length")
    flight_height = st.number_input("Flight height (m)", min_value=0, step=1, key=f"{tab_prefix}_flight_height")
    image_width = st.number_input("Image width (px)", min_value=1, value=None, key=f"{tab_prefix}_image_width")

    # Check if all required values are entered and valid
    if all([sensor_size > 0, focal_length > 0, flight_height > 0, image_width is not None and image_width > 0]):
        gsd = calculate_gsd(sensor_size, focal_length, flight_height, image_width)
        model_resolution = model_resolution_control(gsd, agr)

        st.write(f"**Calculated GSD:** {gsd:.4f} mm")
        st.write(f"**Resolution Achieved:** {model_resolution * 100:.2f}%")
        
        # Store resolution value in session state
        st.session_state[f"{tab_prefix}_model_resolution"] = model_resolution
    else:
        st.info("Please enter all required values to calculate GSD and Resolution Achieved.")
        # Clear any previously stored resolution value
        st.session_state[f"{tab_prefix}_model_resolution"] = None

    # --- 5. Data Quality Elements ---
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 5. Data Quality Elements</h2>', unsafe_allow_html=True)

    if sample_type == "Feature-based":
        st.markdown('<h3 style="font-size: 1.2rem;">Feature-based Evaluation</h3>', unsafe_allow_html=True)
        feature_selected_dq = []

        st.markdown('<h3 style="color: #B3C8CF; font-size: 1.2rem;">📋 Data Quality Checklist</h3>', unsafe_allow_html=True)

        if tab_prefix == "g0":
            # For Model G(0), show all measures
            for i, dq in enumerate(feature_dq_data):
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    checked = st.checkbox("", key=f"{tab_prefix}_feature_check_{i}")
                with col2:
                    st.markdown(f"**{dq['Measure']}**  \n*{dq['Evaluation Category']} | {dq['DQ Type']} | {dq.get('Sub-Type', '')}*  \n:gray[{dq['Hint']}]")

                if checked:
                    dq_input = {}
                    dq_input["Measure"] = dq["Measure"]
                    
                    # List of measures that should only accept numbers and not have units
                    feature_number_only_measures = [
                        "Number of excess items",
                        "Number of missing items",
                        "Number of incorrectly classified items",
                        "Number of generalization discrepancies",
                        "Number of items not compliant",
                        "The number of chronological errors",
                        "Number of duplicate items"
                    ]

                    # List of measures that should have decimal input
                    feature_decimal_measures = [
                        "Positional absolute (external)",
                        "Positional relative (internal)"
                    ]

                    # List of measures that should have Yes/No selection
                    feature_yes_no_measures = [
                        "Excess items",
                        "Missing items",
                        "Data model compliance",
                        "LoD compliance",
                        "Conceptual schema non-compliance",
                        "Conceptual schema compliance",
                        "Chronological order",
                        "Temporal consistency",
                        "Interoperability issues"
                    ]

                    # List of rate measures that should be calculated automatically
                    rate_measures = {
                        "Rate of excess items": "Number of excess items",
                        "Rate of missing items": "Number of missing items",
                        "Misclassification rate": "Number of incorrectly classified items",
                        "Not compliant rate": "Number of items not compliant",
                        "Chronological error rate": "The number of chronological errors",
                        "Generalization discrepancy rate": "Number of generalization discrepancies"
                    }
                    
                    if dq["Measure"] in feature_decimal_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0.0,
                            format="%.3f",
                            step=0.001,
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                    elif dq["Measure"] in feature_number_only_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0,
                            step=1,
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                    elif dq["Measure"] in feature_yes_no_measures:
                        dq_input["Value"] = st.radio(
                            f"Select for `{dq['Measure']}`",
                            options=["Yes", "No"],
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                        if dq["Measure"] == "Interoperability issues" and dq_input["Value"] == "Yes":
                            dq_input["Description"] = st.text_area(
                                "Please describe the interoperability issues",
                                key=f"{tab_prefix}_feature_desc_{i}"
                            )
                    elif dq["Measure"] in rate_measures:
                        # Get the corresponding number measure
                        number_measure = rate_measures[dq["Measure"]]
                        # Find the index of the number measure
                        number_measure_index = next((j for j, d in enumerate(feature_dq_data) if d["Measure"] == number_measure), None)
                        
                        if number_measure_index is not None:
                            # Get the total number of items from session state
                            total_items = st.session_state.get(f"{tab_prefix}_total_features", 0)
                            if total_items > 0:
                                # Get the number value from session state
                                number_value = st.session_state.get(f"{tab_prefix}_feature_value_{number_measure_index}", 0)
                                if isinstance(number_value, (int, float)):
                                    # Calculate the rate
                                    rate = (number_value / total_items) * 100
                                    dq_input["Value"] = f"{rate:.2f}%"
                                    st.markdown(f"**Calculated Rate:** {rate:.2f}%")
                                else:
                                    dq_input["Value"] = "N/D"
                                    st.info(f"Please enter a valid number for {number_measure} to calculate the rate.")
                            else:
                                dq_input["Value"] = "N/D"
                                st.info("Please enter the total number of features to calculate the rate.")
                        else:
                            dq_input["Value"] = "N/D"
                            st.info(f"Could not find the corresponding number measure for {dq['Measure']}")
                    else:
                        dq_input["Value"] = st.text_input(f"🔢 Enter value for `{dq['Measure']}`", key=f"{tab_prefix}_feature_value_{i}")
                        dq_input["Unit"] = st.text_input(f"📏 Unit for `{dq['Measure']}`", key=f"{tab_prefix}_feature_unit_{i}")
                    
                    feature_selected_dq.append(dq_input)
                    st.markdown("---")
        else:
            # For Model G(t), show only measures selected in Model G(0)
            for i, dq in enumerate(feature_dq_data):
                if st.session_state.get(f"g0_feature_check_{i}", False):
                    # Set the check state for Model G(t) to match Model G(0)
                    st.session_state[f"gt_feature_check_{i}"] = True
                    st.markdown(f"**{dq['Measure']}**  \n*{dq['Evaluation Category']} | {dq['DQ Type']} | {dq.get('Sub-Type', '')}*  \n:gray[{dq['Hint']}]")
                    
                    dq_input = {}
                    dq_input["Measure"] = dq["Measure"]
                    
                    # List of measures that should only accept numbers and not have units
                    feature_number_only_measures = [
                        "Number of excess items",
                        "Number of missing items",
                        "Number of incorrectly classified items",
                        "Number of generalization discrepancies",
                        "Number of items not compliant",
                        "The number of chronological errors",
                        "Number of duplicate items"
                    ]

                    # List of measures that should have decimal input
                    feature_decimal_measures = [
                        "Positional absolute (external)",
                        "Positional relative (internal)"
                    ]

                    # List of measures that should have Yes/No selection
                    feature_yes_no_measures = [
                        "Excess items",
                        "Missing items",
                        "Data model compliance",
                        "LoD compliance",
                        "Conceptual schema non-compliance",
                        "Conceptual schema compliance",
                        "Chronological order",
                        "Temporal consistency",
                        "Interoperability issues"
                    ]

                    # List of rate measures that should be calculated automatically
                    rate_measures = {
                        "Rate of excess items": "Number of excess items",
                        "Rate of missing items": "Number of missing items",
                        "Misclassification rate": "Number of incorrectly classified items",
                        "Not compliant rate": "Number of items not compliant",
                        "Chronological error rate": "The number of chronological errors",
                        "Generalization discrepancy rate": "Number of generalization discrepancies"
                    }
                    
                    if dq["Measure"] in feature_decimal_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0.0,
                            format="%.3f",
                            step=0.001,
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                    elif dq["Measure"] in feature_number_only_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0,
                            step=1,
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                    elif dq["Measure"] in feature_yes_no_measures:
                        dq_input["Value"] = st.radio(
                            f"Select for `{dq['Measure']}`",
                            options=["Yes", "No"],
                            key=f"{tab_prefix}_feature_value_{i}"
                        )
                        if dq["Measure"] == "Interoperability issues" and dq_input["Value"] == "Yes":
                            dq_input["Description"] = st.text_area(
                                "Please describe the interoperability issues",
                                key=f"{tab_prefix}_feature_desc_{i}"
                            )
                    elif dq["Measure"] in rate_measures:
                        # Get the corresponding number measure
                        number_measure = rate_measures[dq["Measure"]]
                        # Find the index of the number measure
                        number_measure_index = next((j for j, d in enumerate(feature_dq_data) if d["Measure"] == number_measure), None)
                        
                        if number_measure_index is not None:
                            # Get the total number of items from session state
                            total_items = st.session_state.get(f"{tab_prefix}_total_features", 0)
                            if total_items > 0:
                                # Get the number value from session state
                                number_value = st.session_state.get(f"{tab_prefix}_feature_value_{number_measure_index}", 0)
                                if isinstance(number_value, (int, float)):
                                    # Calculate the rate
                                    rate = (number_value / total_items) * 100
                                    dq_input["Value"] = f"{rate:.2f}%"
                                    st.markdown(f"**Calculated Rate:** {rate:.2f}%")
                                else:
                                    dq_input["Value"] = "N/D"
                                    st.info(f"Please enter a valid number for {number_measure} to calculate the rate.")
                            else:
                                dq_input["Value"] = "N/D"
                                st.info("Please enter the total number of features to calculate the rate.")
                        else:
                            dq_input["Value"] = "N/D"
                            st.info(f"Could not find the corresponding number measure for {dq['Measure']}")
                    else:
                        dq_input["Value"] = st.text_input(f"🔢 Enter value for `{dq['Measure']}`", key=f"{tab_prefix}_feature_value_{i}")
                        dq_input["Unit"] = st.text_input(f"📏 Unit for `{dq['Measure']}`", key=f"{tab_prefix}_feature_unit_{i}")
                    
                    feature_selected_dq.append(dq_input)
                    st.markdown("---")

        if feature_selected_dq:
            st.markdown("### Selected DQ Elements Summary")
            # Process the data before creating DataFrame
            for item in feature_selected_dq:
                # Handle Value column
                if "Value" not in item or not item["Value"]:
                    item["Value"] = "N/D"
                
                # Handle Unit column
                if "Unit" in item:
                    item["Unit"] = item["Unit"] if item["Unit"] else "N/D"
                else:
                    item["Unit"] = "N/A"
                
                # Handle Description column
                if "Description" in item:
                    item["Description"] = item["Description"] if item["Description"] else "N/D"
                else:
                    item["Description"] = "N/A"
            
            summary_df = pd.DataFrame(feature_selected_dq)
            st.dataframe(summary_df)
        else:
            st.info("Please select DQ measures to evaluate.")

    elif sample_type == "Scale-based":
        st.markdown('<h3 style="font-size: 1.2rem;">Scale-based Evaluation</h3>', unsafe_allow_html=True)

        scale_selected_dq = []

        st.markdown("### 📋 Data Quality Checklist")

        if tab_prefix == "g0":
            # For Model G(0), show all measures
            for i, dq in enumerate(scale_dq_data):
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    checked = st.checkbox("", key=f"{tab_prefix}_scale_check_{i}")
                with col2:
                    st.markdown(f"**{dq['Measure']}**  \n*{dq['Evaluation Category']} | {dq['DQ Type']} | {dq.get('Sub-Type', '')}*  \n:gray[{dq['Hint']}]")

                if checked:
                    dq_input = {}
                    dq_input["Measure"] = dq["Measure"]
                    
                    # List of measures that should only accept numbers and not have units
                    scale_number_only_measures = [
                        "The number of chronological errors"
                    ]

                    # List of measures that should have Yes/No selection
                    scale_yes_no_measures = [
                        "Data model compliance",
                        "LoD compliance",
                        "Chronological order",
                        "Temporal consistency",
                        "Interoperability issues"
                    ]
                    
                    if dq["Measure"] in scale_number_only_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0,
                            step=1,
                            key=f"{tab_prefix}_scale_value_{i}"
                        )
                    elif dq["Measure"] in scale_yes_no_measures:
                        dq_input["Value"] = st.radio(
                            f"Select for `{dq['Measure']}`",
                            options=["Yes", "No"],
                            key=f"{tab_prefix}_scale_value_{i}"
                        )
                        if dq["Measure"] == "Interoperability issues" and dq_input["Value"] == "Yes":
                            dq_input["Description"] = st.text_area(
                                "Please describe the interoperability issues",
                                key=f"{tab_prefix}_scale_desc_{i}"
                            )
                    else:
                        dq_input["Value"] = st.text_input(f"🔢 Enter value for `{dq['Measure']}`", key=f"{tab_prefix}_scale_value_{i}")
                        dq_input["Unit"] = st.text_input(f"📏 Unit for `{dq['Measure']}`", key=f"{tab_prefix}_scale_unit_{i}")
                    
                    scale_selected_dq.append(dq_input)
                    st.markdown("---")
        else:
            # For Model G(t), show only measures selected in Model G(0)
            for i, dq in enumerate(scale_dq_data):
                if st.session_state.get(f"g0_scale_check_{i}", False):
                    # Set the check state for Model G(t) to match Model G(0)
                    st.session_state[f"gt_scale_check_{i}"] = True
                    st.markdown(f"**{dq['Measure']}**  \n*{dq['Evaluation Category']} | {dq['DQ Type']} | {dq.get('Sub-Type', '')}*  \n:gray[{dq['Hint']}]")
                    
                    dq_input = {}
                    dq_input["Measure"] = dq["Measure"]
                    
                    # List of measures that should only accept numbers and not have units
                    scale_number_only_measures = [
                        "The number of chronological errors"
                    ]

                    # List of measures that should have Yes/No selection
                    scale_yes_no_measures = [
                        "Data model compliance",
                        "LoD compliance",
                        "Chronological order",
                        "Temporal consistency",
                        "Interoperability issues"
                    ]
                    
                    if dq["Measure"] in scale_number_only_measures:
                        dq_input["Value"] = st.number_input(
                            f"🔢 Enter value for `{dq['Measure']}`",
                            min_value=0,
                            step=1,
                            key=f"{tab_prefix}_scale_value_{i}"
                        )
                    elif dq["Measure"] in scale_yes_no_measures:
                        dq_input["Value"] = st.radio(
                            f"Select for `{dq['Measure']}`",
                            options=["Yes", "No"],
                            key=f"{tab_prefix}_scale_value_{i}"
                        )
                        if dq["Measure"] == "Interoperability issues" and dq_input["Value"] == "Yes":
                            dq_input["Description"] = st.text_area(
                                "Please describe the interoperability issues",
                                key=f"{tab_prefix}_scale_desc_{i}"
                            )
                    else:
                        dq_input["Value"] = st.text_input(f"🔢 Enter value for `{dq['Measure']}`", key=f"{tab_prefix}_scale_value_{i}")
                        dq_input["Unit"] = st.text_input(f"📏 Unit for `{dq['Measure']}`", key=f"{tab_prefix}_scale_unit_{i}")
                    
                    scale_selected_dq.append(dq_input)
                    st.markdown("---")

        if scale_selected_dq:
            st.markdown("### Selected DQ Elements Summary")
            # Process the data before creating DataFrame
            for item in scale_selected_dq:
                # Handle Value column
                if "Value" not in item or not item["Value"]:
                    item["Value"] = "N/D"
                
                # Handle Unit column
                if "Unit" in item:
                    item["Unit"] = item["Unit"] if item["Unit"] else "N/D"
                else:
                    item["Unit"] = "N/A"
                
                # Handle Description column
                if "Description" in item:
                    item["Description"] = item["Description"] if item["Description"] else "N/D"
                else:
                    item["Description"] = "N/A"
            
            summary_df = pd.DataFrame(scale_selected_dq)
            st.dataframe(summary_df)
        else:
            st.info("Please select DQ measures to evaluate.")

# Create Model G(0) tab content
with tab1:
    create_model_assessment_form("g0")
    
    # Add buttons in a row
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📥 Download Model Data", use_container_width=True, key="g0_download_button"):
            # Create a list to store all data rows
            csv_data = []
            
            # Add GDT Characteristics
            csv_data.extend([
                ["GDT Characteristics", "", ""],
                ["GDT Scale", st.session_state.get("g0_gdt_scale", "Not specified"), ""],
                ["GDT Scale Value", st.session_state.get("g0_gdt_scale_value", "Not specified"), ""],
                ["Building Life Cycle Stage", st.session_state.get("g0_gdt_stage", "Not specified"), ""],
                ["AGR of model", st.session_state.get("g0_agr", "Not specified"), "mm/px"],
                ["", "", ""]
            ])
            
            # Add Sample for Evaluation
            csv_data.extend([
                ["Sample for Evaluation", "", ""],
                ["Sample Type", st.session_state.get("g0_sample_type", "Not specified"), ""]
            ])
            
            if st.session_state.get("g0_sample_type") == "Feature-based":
                csv_data.append(["Total Features", st.session_state.get("g0_total_features", "Not specified"), ""])
            else:
                csv_data.append(["Sample Scale", st.session_state.get("g0_sample_scale", "Not specified"), ""])
            
            csv_data.append(["", "", ""])
            
            # Add Parameters for Updating
            csv_data.extend([
                ["Parameters for Updating", "", ""],
                ["Number of Previous Updates", st.session_state.get("g0_updates", "Not specified"), ""],
                ["Update Schedule", st.session_state.get("g0_schedule", "Not specified"), ""],
                ["Survey Type", st.session_state.get("g0_survey_type", "Not specified"), ""],
                ["Data Acquisition Sequence", st.session_state.get("g0_acq_sequence", "Not specified"), ""],
                ["", "", ""]
            ])
            
            # Add LoD Verification
            csv_data.extend([
                ["LoD Verification", "", ""],
                ["Suggested LoD", calculate_lod(st.session_state.get("g0_agr", 0)) if st.session_state.get("g0_agr", 0) > 0 else "Not calculated", ""],
                ["Feature's RMSE", st.session_state.get("g0_rmse_value", "Not specified"), ""],
                ["", "", ""]
            ])
            
            # Add GSD Calculation
            sensor_size = st.session_state.get('g0_sensor_size')
            focal_length = st.session_state.get('g0_focal_length')
            flight_height = st.session_state.get('g0_flight_height')
            image_width = st.session_state.get('g0_image_width')
            
            # Check if all required values are present and greater than 0
            if all(v is not None and v > 0 for v in [sensor_size, focal_length, flight_height, image_width]):
                gsd = calculate_gsd(sensor_size, focal_length, flight_height, image_width)
                gsd_value = f"{gsd:.4f} mm"
            else:
                gsd_value = "Not calculated"
            
            csv_data.extend([
                ["GSD Calculation", "", ""],
                ["Sensor Size", st.session_state.get("g0_sensor_size", "Not specified"), "mm"],
                ["Focal Length", st.session_state.get("g0_focal_length", "Not specified"), "mm"],
                ["Flight Height", st.session_state.get("g0_flight_height", "Not specified"), "m"],
                ["Image Width", st.session_state.get("g0_image_width", "Not specified"), "px"],
                ["Calculated GSD", gsd_value, ""],
                ["Resolution Achieved", f"{st.session_state.get('g0_model_resolution', 0) * 100:.2f}%" if st.session_state.get('g0_model_resolution') is not None else "Not calculated", ""],
                ["", "", ""]
            ])
            
            # Add Selected Measures
            csv_data.append(["Selected Measures", "", ""])
            if st.session_state.get("g0_sample_type") == "Feature-based":
                for i, dq in enumerate(feature_dq_data):
                    if st.session_state.get(f"g0_feature_check_{i}", False):
                        csv_data.append([
                            dq["Measure"],
                            st.session_state.get(f"g0_feature_value_{i}", "Not specified"),
                            st.session_state.get(f"g0_feature_unit_{i}", "N/A")
                        ])
            else:
                for i, dq in enumerate(scale_dq_data):
                    if st.session_state.get(f"g0_scale_check_{i}", False):
                        csv_data.append([
                            dq["Measure"],
                            st.session_state.get(f"g0_scale_value_{i}", "Not specified"),
                            st.session_state.get(f"g0_scale_unit_{i}", "N/A")
                        ])
            
            # Convert to CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            
            # Create download button
            st.download_button(
                label="Click to download",
                data=output.getvalue(),
                file_name="model_g0_data.csv",
                mime="text/csv",
                key="g0_download_csv_button"
            )
    
    with col2:
        if st.button("💾 Save & Continue to Model G(t)", use_container_width=True, key="g0_next_button"):
            # Store the current state
            st.session_state["g0_saved"] = True
            st.success("Model G(0) data saved! Please click on the 'Model G(t)' tab above to continue.")

# Create Model G(t) tab content
with tab2:
    create_model_assessment_form("gt")
    
    # Add buttons in a row
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📥 Download Model Data", use_container_width=True, key="gt_download_button"):
            # Create a list to store all data rows
            csv_data = []
            
            # Add GDT Characteristics
            csv_data.extend([
                ["GDT Characteristics", "", ""],
                ["GDT Scale", st.session_state.get("gt_gdt_scale", "Not specified"), ""],
                ["GDT Scale Value", st.session_state.get("gt_gdt_scale_value", "Not specified"), ""],
                ["Building Life Cycle Stage", st.session_state.get("gt_gdt_stage", "Not specified"), ""],
                ["AGR of model", st.session_state.get("gt_agr", "Not specified"), "mm/px"],
                ["", "", ""]
            ])
            
            # Add Sample for Evaluation
            csv_data.extend([
                ["Sample for Evaluation", "", ""],
                ["Sample Type", st.session_state.get("gt_sample_type", "Not specified"), ""]
            ])
            
            if st.session_state.get("gt_sample_type") == "Feature-based":
                csv_data.append(["Total Features", st.session_state.get("gt_total_features", "Not specified"), ""])
            else:
                csv_data.append(["Sample Scale", st.session_state.get("gt_sample_scale", "Not specified"), ""])
            
            csv_data.append(["", "", ""])
            
            # Add LoD Verification
            csv_data.extend([
                ["LoD Verification", "", ""],
                ["Suggested LoD", calculate_lod(st.session_state.get("gt_agr", 0)) if st.session_state.get("gt_agr", 0) > 0 else "Not calculated", ""],
                ["Feature's RMSE", st.session_state.get("gt_rmse_value", "Not specified"), ""],
                ["", "", ""]
            ])
            
            # Add GSD Calculation
            sensor_size = st.session_state.get('gt_sensor_size')
            focal_length = st.session_state.get('gt_focal_length')
            flight_height = st.session_state.get('gt_flight_height')
            image_width = st.session_state.get('gt_image_width')
            
            # Check if all required values are present and greater than 0
            if all(v is not None and v > 0 for v in [sensor_size, focal_length, flight_height, image_width]):
                gsd = calculate_gsd(sensor_size, focal_length, flight_height, image_width)
                gsd_value = f"{gsd:.4f} mm"
            else:
                gsd_value = "Not calculated"
            
            csv_data.extend([
                ["GSD Calculation", "", ""],
                ["Sensor Size", st.session_state.get("gt_sensor_size", "Not specified"), "mm"],
                ["Focal Length", st.session_state.get("gt_focal_length", "Not specified"), "mm"],
                ["Flight Height", st.session_state.get("gt_flight_height", "Not specified"), "m"],
                ["Image Width", st.session_state.get("gt_image_width", "Not specified"), "px"],
                ["Calculated GSD", gsd_value, ""],
                ["Resolution Achieved", f"{st.session_state.get('gt_model_resolution', 0) * 100:.2f}%" if st.session_state.get('gt_model_resolution') is not None else "Not calculated", ""],
                ["", "", ""]
            ])
            
            # Add Selected Measures
            csv_data.append(["Selected Measures", "", ""])
            if st.session_state.get("gt_sample_type") == "Feature-based":
                for i, dq in enumerate(feature_dq_data):
                    if st.session_state.get(f"gt_feature_check_{i}", False):
                        csv_data.append([
                            dq["Measure"],
                            st.session_state.get(f"gt_feature_value_{i}", "Not specified"),
                            st.session_state.get(f"gt_feature_unit_{i}", "N/A")
                        ])
            else:
                for i, dq in enumerate(scale_dq_data):
                    if st.session_state.get(f"gt_scale_check_{i}", False):
                        csv_data.append([
                            dq["Measure"],
                            st.session_state.get(f"gt_scale_value_{i}", "Not specified"),
                            st.session_state.get(f"gt_scale_unit_{i}", "N/A")
                        ])
            
            # Convert to CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            
            # Create download button
            st.download_button(
                label="Click to download",
                data=output.getvalue(),
                file_name="model_gt_data.csv",
                mime="text/csv",
                key="gt_download_csv_button"
            )
    
    with col2:
        if st.button("💾 Save & View Results", use_container_width=True, key="gt_results_button"):
            # Store the current state
            st.session_state["gt_saved"] = True
            st.success("Model G(t) data saved! Please click on the 'Assessment Results' tab above to view results.")

# Create Assessment Results tab content
with tab3:
    def create_assessment_results():
        st.markdown('<h1 class="section-title" style="font-size: 1.4rem;">Assessment Results</h1>', unsafe_allow_html=True)
        
        # Get GDT Scale from Model G(0)
        gdt_scale = st.session_state.get("g0_gdt_scale", "Not specified")
        st.markdown(f'<p><span style="color: #B3C8CF; font-weight: bold;">GDT Scale:</span> {gdt_scale}</p>', unsafe_allow_html=True)

        # Get Building life cycle stages from both models
        g0_stage = st.session_state.get("g0_gdt_stage", "Not specified")
        gt_stage = st.session_state.get("gt_gdt_stage", "Not specified")
        
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Building Life Cycle Stage Comparison</h2>', unsafe_allow_html=True)
        
        st.write(f"**Model G(0):** {g0_stage}")
        st.write(f"**Model G(t):** {gt_stage}")
        
        # Get Sample for Evaluation from Model G(0)
        sample_type = st.session_state.get("g0_sample_type", "Not specified")
        
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Sample for Evaluation</h2>', unsafe_allow_html=True)
        
        st.write(f"**Selected Type:** {sample_type}")
        
        # Display additional sample information based on the type
        if sample_type == "Feature-based":
            total_features = st.session_state.get("g0_total_features", "Not specified")
            st.write(f"**Total number of features (items):** {total_features}")
        elif sample_type == "Scale-based":
            sample_scale = st.session_state.get("g0_sample_scale", "Not specified")
           
        # LoD Verification Summary Table
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">LoD Verification Summary</h2>', unsafe_allow_html=True)
        
        # Get values for Model G(0)
        g0_agr = st.session_state.get("g0_agr", "N/D")
        g0_suggested_lod = calculate_lod(g0_agr) if g0_agr != "N/D" else "N/D"
        g0_rmse = st.session_state.get("g0_rmse_value", "N/D")
        
        # Get values for Model G(t)
        gt_agr = st.session_state.get("gt_agr", "N/D")
        gt_suggested_lod = calculate_lod(gt_agr) if gt_agr != "N/D" else "N/D"
        gt_rmse = st.session_state.get("gt_rmse_value", "N/D")
        
        # Create the summary table
        lod_summary_data = {
            "Model version": ["Model G(0)", "Model G(t)"],
            "AGR of model": [f"{g0_agr} mm/px" if g0_agr != "N/D" else "N/D", 
                            f"{gt_agr} mm/px" if gt_agr != "N/D" else "N/D"],
            "Suggested LoD": [g0_suggested_lod, gt_suggested_lod],
            "Resolution achieved": [f"{st.session_state.get('g0_model_resolution', 0) * 100:.2f}%" if st.session_state.get('g0_model_resolution') is not None else "N/D",
                                  f"{st.session_state.get('gt_model_resolution', 0) * 100:.2f}%" if st.session_state.get('gt_model_resolution') is not None else "N/D"],
            "Feature's RMSE": [f"{g0_rmse}" if g0_rmse != "N/D" else "N/D",
                              f"{gt_rmse}" if gt_rmse != "N/D" else "N/D"]
        }
        
        lod_summary_df = pd.DataFrame(lod_summary_data)
        st.dataframe(lod_summary_df, use_container_width=True)

        # Measures Summary Table
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Measures Summary</h2>', unsafe_allow_html=True)
        
        # Get all selected measures from both models
        g0_measures = []
        gt_measures = []
        
        # Get sample type from Model G(0)
        sample_type = st.session_state.get("g0_sample_type", "Feature-based")
        
        # Determine which data list to use based on sample type
        if sample_type == "Feature-based":
            data_list = feature_dq_data
            check_prefix = "feature_check"
            value_prefix = "feature_value"
        else:  # Scale-based
            data_list = scale_dq_data
            check_prefix = "scale_check"
            value_prefix = "scale_value"
        
        # Collect measures from Model G(0)
        for i, dq in enumerate(data_list):
            if st.session_state.get(f"g0_{check_prefix}_{i}", False):
                measure = st.session_state.get(f"g0_{value_prefix}_{i}", "N/D")
                g0_measures.append({"Measure": dq["Measure"], "Value": measure})
        
        # Collect measures from Model G(t)
        for i, dq in enumerate(data_list):
            if st.session_state.get(f"gt_{check_prefix}_{i}", False):
                measure = st.session_state.get(f"gt_{value_prefix}_{i}", "N/D")
                gt_measures.append({"Measure": dq["Measure"], "Value": measure})
        
        # Create a combined list of all unique measures
        all_measures = set()
        for measure in g0_measures + gt_measures:
            all_measures.add(measure["Measure"])
        
        # Create the summary data
        measures_summary_data = {
            "Measure": list(all_measures),
            "Model G(0)": ["N/D"] * len(all_measures),
            "Model G(t)": ["N/D"] * len(all_measures)
        }
        
        # Fill in the values
        for i, measure in enumerate(measures_summary_data["Measure"]):
            # Find value in G(0)
            for g0_measure in g0_measures:
                if g0_measure["Measure"] == measure:
                    measures_summary_data["Model G(0)"][i] = g0_measure["Value"]
                    break
            
            # Find value in G(t)
            for gt_measure in gt_measures:
                if gt_measure["Measure"] == measure:
                    measures_summary_data["Model G(t)"][i] = gt_measure["Value"]
                    break
        
        # Create and display the DataFrame
        measures_summary_df = pd.DataFrame(measures_summary_data)
        st.dataframe(measures_summary_df, use_container_width=True)

        # Decision Model Table
        st.markdown('<h2 style="color: #B3C8CF; font-size: 1.4rem;">Decision Model based on Mandatory Data Quality Elements</h2>', unsafe_allow_html=True)
        
        # Models alignment data section
        st.markdown('<h3 style="color: #E5E1DA; font-size: 1.2rem;">Models alignment data (optional)</h3>', unsafe_allow_html=True)
        
        # Create input fields for geometric deviations
        mean_deviation = st.number_input(
            "Mean of geometric deviations μ",
            help="Average deviation between corresponding points in Model G(0) and Model G(t)",
            format="%.3f",
            key="mean_deviation"
        )
        
        std_deviation = st.number_input(
            "Standard deviation σ",
            help="Standard deviation of the geometric deviations between corresponding points in Model G(0) and Model G(t)",
            format="%.3f",
            key="std_deviation"
        )
        
        # Calculate deviation threshold
        if mean_deviation != 0 and std_deviation != 0:
            deviation_threshold = mean_deviation + 2 * std_deviation
            st.write(f"**Deviation threshold δpos:** {deviation_threshold:.3f}")
            st.caption("Filters out noise and identifies significant deviations")
        else:
            st.write("**Deviation threshold δpos:** Not calculated")
            st.caption("Both mean and standard deviation must be non-zero to calculate the threshold")

        # Condition 1 section
        st.markdown('<h3 style="color: #B3C8CF; font-size: 1.2rem;">Condition 1: Model Accuracy Consistency Assessment</h3>', unsafe_allow_html=True)
        st.caption("Evaluates the consistency of model accuracy over time by comparing positional accuracy measures between Model G(0) and Model G(t)")
        
        # Get values for Dacc calculation
        g0_abs_pos = None
        g0_rel_pos = None
        gt_abs_pos = None
        gt_rel_pos = None
        
        # Find the values from measures based on sample type
        for i, dq in enumerate(data_list):
            if dq["Measure"] == "Positional absolute (external)":
                if st.session_state.get(f"g0_{check_prefix}_{i}", False):
                    g0_abs_pos = st.session_state.get(f"g0_{value_prefix}_{i}", 0)
                if st.session_state.get(f"gt_{check_prefix}_{i}", False):
                    gt_abs_pos = st.session_state.get(f"gt_{value_prefix}_{i}", 0)
            elif dq["Measure"] == "Positional relative (internal)":
                if st.session_state.get(f"g0_{check_prefix}_{i}", False):
                    g0_rel_pos = st.session_state.get(f"g0_{value_prefix}_{i}", 0)
                if st.session_state.get(f"gt_{check_prefix}_{i}", False):
                    gt_rel_pos = st.session_state.get(f"gt_{value_prefix}_{i}", 0)
        
        # Calculate Dacc
        dacc = None
        if all(v is not None and v != 0 for v in [g0_abs_pos, g0_rel_pos, gt_abs_pos, gt_rel_pos]):
            try:
                # Convert string values to float if they are strings
                g0_abs_pos = float(g0_abs_pos) if isinstance(g0_abs_pos, str) else g0_abs_pos
                g0_rel_pos = float(g0_rel_pos) if isinstance(g0_rel_pos, str) else g0_rel_pos
                gt_abs_pos = float(gt_abs_pos) if isinstance(gt_abs_pos, str) else gt_abs_pos
                gt_rel_pos = float(gt_rel_pos) if isinstance(gt_rel_pos, str) else gt_rel_pos
                
                # Calculate Dacc using the formula
                dacc = abs((1 - (gt_rel_pos/g0_rel_pos)) - (1 - (gt_abs_pos/g0_abs_pos)))
                st.write(f"**Dacc (Accuracy difference between models):** {dacc:.3f}")
                st.caption("Controls and assesses the consistency of model accuracy over time")
            except (ValueError, TypeError, ZeroDivisionError) as e:
                st.write("**Dacc (Accuracy difference between models):** Not calculated")
                st.caption(f"Error in calculation: {str(e)}. Please ensure all values are valid numbers and non-zero.")
        else:
            st.write("**Dacc (Accuracy difference between models):** Not calculated")
            st.caption("All required positional accuracy measures must be provided and non-zero")
        
        # Input for δD
        delta_d = st.number_input(
            "δD (Accuracy difference threshold)",
            help="Set your value. An empirical approach is preferable (δD = μDacc ± 2σDacc) from multiple update processes. Alternatively, use relevant regulatory or project requirements",
            format="%.3f",
            key="delta_d"
        )
        
        # Compare Dacc vs δD
        if dacc is not None and delta_d != 0:
            comparison_result = "Consistent accuracy in both models" if dacc < delta_d else "Decline in model G(t) accuracy"
            st.write(f"**Dacc vs. δD comparison:** {comparison_result}")
            st.caption("Indicates whether the model accuracy has remained consistent or declined over time")
        else:
            st.write("**Dacc vs. δD comparison:** Not calculated")
            st.caption("Both Dacc and δD must be calculated and non-zero for comparison")

        # Conditions 2-3 section
        st.markdown('<h3 style="color: #B3C8CF; font-size: 1.2rem;">Conditions 2-3: Model Resolution Validation</h3>', unsafe_allow_html=True)
        st.caption("Evaluates the consistency of model resolution and LoD between Model G(0) and Model G(t)")
        
        # Get values for LoD comparison
        g0_lod = g0_suggested_lod
        gt_lod = gt_suggested_lod
        
        # Compare LoD
        if g0_lod != "N/D" and gt_lod != "N/D":
            lod_comparison = "Consistent LoD for both models" if g0_lod == gt_lod else "Inconsistent LoD"
            st.write(f"**Condition 2: LoD comparison:** {lod_comparison}")
            st.caption("Indicates whether the Level of Detail remains consistent between models")
        else:
            st.write("**Condition 2: LoD comparison:** Not calculated")
            st.caption("Both models must have valid LoD values for comparison. Please provide AGR values in Model G(0) and Model G(t) tabs to calculate LoD.")
        
        # Compare Resolution achieved
        if st.session_state.get('g0_model_resolution') is not None and st.session_state.get('gt_model_resolution') is not None:
            resolution_comparison = "Decline in model G(t) resolution" if st.session_state.get('gt_model_resolution') < st.session_state.get('g0_model_resolution') else "Increase in model G(t) resolution"
            st.write(f"**Condition 3: Resolution comparison:** {resolution_comparison}")
            st.caption("Indicates whether the model resolution has improved or declined over time")
        else:
            st.write("**Condition 3: Resolution comparison:** Not calculated")
            st.caption("Both models must have valid resolution values for comparison")

        # Performance Comparison section
        st.markdown('<h3 style="color: #B3C8CF; font-size: 1.2rem;">Performance Comparison: Model G(t) vs Model G(0)</h3>', unsafe_allow_html=True)
        st.caption("Calculates the percentage of evaluation parameters where Model G(t) outperforms Model G(0) based on Conditional and Optional DQ Elements")
        
        # Initialize counters
        total_parameters = 0
        gt_better_count = 0
        
        # Analyze each measure
        for i, dq in enumerate(data_list):
            # Only consider Conditional and Optional measures
            if "Category: Mandatory" not in dq["Evaluation Category"]:
                if st.session_state.get(f"g0_{check_prefix}_{i}", False):
                    total_parameters += 1
                    
                    # Get values for both models
                    g0_value = st.session_state.get(f"g0_{value_prefix}_{i}", "N/D")
                    gt_value = st.session_state.get(f"gt_{value_prefix}_{i}", "N/D")
                    
                    # Compare values based on measure type
                    if g0_value != "N/D" and gt_value != "N/D":
                        if dq["Measure"] in ["Excess items", "Missing items", "Data model compliance", "LoD compliance", 
                                           "Conceptual schema compliance", "Chronological order", "Temporal consistency", 
                                           "Interoperability issues"]:
                            # For Yes/No measures, "No" is better
                            if g0_value == "Yes" and gt_value == "No":
                                gt_better_count += 1
                        else:
                            # For numeric measures, lower value is better
                            try:
                                g0_num = float(g0_value)
                                gt_num = float(gt_value)
                                if gt_num < g0_num:
                                    gt_better_count += 1
                            except ValueError:
                                pass
        
        # Calculate and display the percentage
        if total_parameters > 0:
            percentage = (gt_better_count / total_parameters) * 100
            st.write(f"**Percentage of parameters where G(t) outperforms G(0):** {percentage:.1f}%")
            
            # Add interpretation
            if percentage >= 75:
                interpretation = "Excellent improvement in Model G(t)"
            elif percentage >= 50:
                interpretation = "Good improvement in Model G(t)"
            elif percentage >= 25:
                interpretation = "Moderate improvement in Model G(t)"
            else:
                interpretation = "Limited improvement in Model G(t)"
            
            st.write(f"**Interpretation:** {interpretation}")
            st.caption(f"Based on {total_parameters} Conditional and Optional DQ Elements")
        else:
            st.write("**Performance comparison:** Not calculated")
            st.caption("No Conditional or Optional DQ Elements selected for comparison")

        # Visual Score section - only show if all conditions can be calculated
        can_calculate_condition1 = dacc is not None and delta_d != 0
        can_calculate_condition2 = g0_lod != "N/D" and gt_lod != "N/D"
        can_calculate_condition3 = st.session_state.get('g0_model_resolution') is not None and st.session_state.get('gt_model_resolution') is not None
        
        if can_calculate_condition1 and can_calculate_condition2 and can_calculate_condition3:
            st.markdown('<h2 style="color: #B3C8CF; font-size: 1.4rem;">Visual Score: Model Update Assessment</h2>', unsafe_allow_html=True)   
                         
            # Count fulfilled conditions
            conditions_fulfilled = 0
            
            # Check Condition 1 (Dacc vs δD)
            if dacc < delta_d:  # Consistent accuracy
                conditions_fulfilled += 1
            
            # Check Condition 2 (LoD)
            if g0_lod == gt_lod:  # Consistent LoD
                conditions_fulfilled += 1
            
            # Check Condition 3 (Resolution)
            if st.session_state.get('gt_model_resolution') >= st.session_state.get('g0_model_resolution'):  # No decline in resolution
                conditions_fulfilled += 1
            
            # Determine the score and color
            if conditions_fulfilled == 0:
                score = "❌ Critical"
                color = "#FF0000"  # Red
                message = "Decline in all metrics for model G(t). Unsuitable for the updating process."
            elif conditions_fulfilled == 1:
                score = "⚠️ Warning"
                color = "#FFA500"  # Orange
                message = "Only one of three conditions is fulfilled. Decline in metrics for model G(t). Unsuitable for the updating process."
            elif conditions_fulfilled == 2:
                score = "⚠️ Partial"
                color = "#FFD700"  # Gold
                message = "Two of three conditions are fulfilled. Model is suitable for partial updating."
            else:
                score = "✅ Suitable"
                color = "#008000"  # Green
                message = "Model G(t) outperforms model G(0). Suitable for updating."
            
            # Display the score with custom styling
            st.markdown(f"""
            <div style='background-color: {color}; padding: 20px; border-radius: 10px; color: white;'>
                <h2 style='margin: 0;'>{score}</h2>
                <p style='margin: 10px 0 0 0;'>{message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add legend
            st.markdown("""
            ### Assessment Legend
            - **❌ Critical**: Model G(t) shows significant decline in all key metrics. Immediate attention required.
            - **⚠️ Warning**: Model G(t) shows concerning decline in multiple metrics. Review and improvement needed.
            - **⚠️ Partial**: Model G(t) shows mixed results. Consider partial updates with specific improvements.
            - **✅ Suitable**: Model G(t) demonstrates overall improvement. Ready for full update implementation.
            """)
        else:
            st.write("#### Visual Score: Model Update Assessment")
            st.info("Visual score will be displayed when all three conditions (accuracy, LoD, and resolution) can be calculated.")

        # Add Download Results button
        st.markdown('<h2 style="color: #B3C8CF; font-size: 1.4rem;">Download Assessment Results</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Results (CSV)", use_container_width=True):
                # Create a dictionary to store all results
                results = {
                    "GDT Scale": gdt_scale,
                    "Building Life Cycle Stages": {
                        "Model G(0)": g0_stage,
                        "Model G(t)": gt_stage
                    },
                    "Sample Type": sample_type,
                    "LoD Verification": {
                        "Model G(0)": {
                            "AGR": f"{g0_agr} mm/px" if g0_agr != "N/D" else "N/D",
                            "Suggested LoD": g0_suggested_lod,
                            "Resolution achieved": f"{st.session_state.get('g0_model_resolution', 0) * 100:.2f}%" if st.session_state.get('g0_model_resolution') is not None else "N/D",
                            "Feature's RMSE": f"{g0_rmse}" if g0_rmse != "N/D" else "N/D"
                        },
                        "Model G(t)": {
                            "AGR": f"{gt_agr} mm/px" if gt_agr != "N/D" else "N/D",
                            "Suggested LoD": gt_suggested_lod,
                            "Resolution achieved": f"{st.session_state.get('gt_model_resolution', 0) * 100:.2f}%" if st.session_state.get('gt_model_resolution') is not None else "N/D",
                            "Feature's RMSE": f"{gt_rmse}" if gt_rmse != "N/D" else "N/D"
                        }
                    },
                    "Measures Summary": measures_summary_data,
                    "Model Accuracy Assessment": {
                        "Dacc": f"{dacc:.3f}" if dacc is not None else "Not calculated",
                        "δD": f"{delta_d:.3f}" if delta_d != 0 else "Not calculated",
                        "Dacc vs δD comparison": comparison_result if dacc is not None and delta_d != 0 else "Not calculated"
                    },
                    "Model Resolution Validation": {
                        "LoD comparison": lod_comparison if g0_lod != "N/D" and gt_lod != "N/D" else "Not calculated",
                        "Resolution comparison": resolution_comparison if st.session_state.get('g0_model_resolution') is not None and st.session_state.get('gt_model_resolution') is not None else "Not calculated"
                    },
                    "Performance Comparison": {
                        "Percentage of parameters where G(t) outperforms G(0)": f"{percentage:.1f}%" if total_parameters > 0 else "Not calculated",
                        "Interpretation": interpretation if total_parameters > 0 else "Not calculated",
                        "Total parameters compared": total_parameters
                    }
                }
                
                if can_calculate_condition1 and can_calculate_condition2 and can_calculate_condition3:
                    results["Visual Score"] = {
                        "Score": score,
                        "Message": message,
                        "Conditions fulfilled": conditions_fulfilled
                    }
                
                # Convert to CSV format
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write GDT Scale
                writer.writerow(["GDT Scale", gdt_scale])
                writer.writerow([])
                
                # Write Building Life Cycle Stages
                writer.writerow(["Building Life Cycle Stages"])
                writer.writerow(["Model G(0)", g0_stage])
                writer.writerow(["Model G(t)", gt_stage])
                writer.writerow([])
                
                # Write Sample Type
                writer.writerow(["Sample Type", sample_type])
                writer.writerow([])
                
                # Write LoD Verification
                writer.writerow(["LoD Verification"])
                writer.writerow(["Model", "AGR", "Suggested LoD", "Resolution achieved", "Feature's RMSE"])
                writer.writerow([
                    "Model G(0)",
                    f"{g0_agr} mm/px" if g0_agr != "N/D" else "N/D",
                    g0_suggested_lod,
                    f"{st.session_state.get('g0_model_resolution', 0) * 100:.2f}%" if st.session_state.get('g0_model_resolution') is not None else "N/D",
                    f"{g0_rmse}" if g0_rmse != "N/D" else "N/D"
                ])
                writer.writerow([
                    "Model G(t)",
                    f"{gt_agr} mm/px" if gt_agr != "N/D" else "N/D",
                    gt_suggested_lod,
                    f"{st.session_state.get('gt_model_resolution', 0) * 100:.2f}%" if st.session_state.get('gt_model_resolution') is not None else "N/D",
                    f"{gt_rmse}" if gt_rmse != "N/D" else "N/D"
                ])
                writer.writerow([])
                
                # Write Measures Summary
                writer.writerow(["Measures Summary"])
                writer.writerow(["Measure", "Model G(0)", "Model G(t)"])
                for i, measure in enumerate(measures_summary_data["Measure"]):
                    writer.writerow([
                        measure,
                        measures_summary_data["Model G(0)"][i],
                        measures_summary_data["Model G(t)"][i]
                    ])
                writer.writerow([])
                
                # Write Model Accuracy Assessment
                writer.writerow(["Model Accuracy Assessment"])
                writer.writerow(["Dacc", f"{dacc:.3f}" if dacc is not None else "Not calculated"])
                writer.writerow(["δD", f"{delta_d:.3f}" if delta_d != 0 else "Not calculated"])
                writer.writerow(["Dacc vs δD comparison", comparison_result if dacc is not None and delta_d != 0 else "Not calculated"])
                writer.writerow([])
                
                # Write Model Resolution Validation
                writer.writerow(["Model Resolution Validation"])
                writer.writerow(["LoD comparison", lod_comparison if g0_lod != "N/D" and gt_lod != "N/D" else "Not calculated"])
                writer.writerow(["Resolution comparison", resolution_comparison if st.session_state.get('g0_model_resolution') is not None and st.session_state.get('gt_model_resolution') is not None else "Not calculated"])
                writer.writerow([])
                
                # Write Performance Comparison
                writer.writerow(["Performance Comparison"])
                writer.writerow(["Percentage of parameters where G(t) outperforms G(0)", f"{percentage:.1f}%" if total_parameters > 0 else "Not calculated"])
                writer.writerow(["Interpretation", interpretation if total_parameters > 0 else "Not calculated"])
                writer.writerow(["Total parameters compared", total_parameters])
                writer.writerow([])
                
                # Write Visual Score if available
                if can_calculate_condition1 and can_calculate_condition2 and can_calculate_condition3:
                    writer.writerow(["Visual Score"])
                    writer.writerow(["Score", score])
                    writer.writerow(["Message", message])
                    writer.writerow(["Conditions fulfilled", conditions_fulfilled])
                
                # Create download button
                st.download_button(
                    label="Click to download CSV",
                    data=output.getvalue(),
                    file_name="assessment_results.csv",
                    mime="text/csv",
                    key="download_csv_button"
                )
        
        with col2:
            if st.button("📥 Download Results (JSON)", use_container_width=True):
                # Create a dictionary to store all results
                results = {
                    "GDT Scale": gdt_scale,
                    "Building Life Cycle Stages": {
                        "Model G(0)": g0_stage,
                        "Model G(t)": gt_stage
                    },
                    "Sample Type": sample_type,
                    "LoD Verification": {
                        "Model G(0)": {
                            "AGR": f"{g0_agr} mm/px" if g0_agr != "N/D" else "N/D",
                            "Suggested LoD": g0_suggested_lod,
                            "Resolution achieved": f"{st.session_state.get('g0_model_resolution', 0) * 100:.2f}%" if st.session_state.get('g0_model_resolution') is not None else "N/D",
                            "Feature's RMSE": f"{g0_rmse}" if g0_rmse != "N/D" else "N/D"
                        },
                        "Model G(t)": {
                            "AGR": f"{gt_agr} mm/px" if gt_agr != "N/D" else "N/D",
                            "Suggested LoD": gt_suggested_lod,
                            "Resolution achieved": f"{st.session_state.get('gt_model_resolution', 0) * 100:.2f}%" if st.session_state.get('gt_model_resolution') is not None else "N/D",
                            "Feature's RMSE": f"{gt_rmse}" if gt_rmse != "N/D" else "N/D"
                        }
                    },
                    "Measures Summary": measures_summary_data,
                    "Model Accuracy Assessment": {
                        "Dacc": f"{dacc:.3f}" if dacc is not None else "Not calculated",
                        "δD": f"{delta_d:.3f}" if delta_d != 0 else "Not calculated",
                        "Dacc vs δD comparison": comparison_result if dacc is not None and delta_d != 0 else "Not calculated"
                    },
                    "Model Resolution Validation": {
                        "LoD comparison": lod_comparison if g0_lod != "N/D" and gt_lod != "N/D" else "Not calculated",
                        "Resolution comparison": resolution_comparison if st.session_state.get('g0_model_resolution') is not None and st.session_state.get('gt_model_resolution') is not None else "Not calculated"
                    },
                    "Performance Comparison": {
                        "Percentage of parameters where G(t) outperforms G(0)": f"{percentage:.1f}%" if total_parameters > 0 else "Not calculated",
                        "Interpretation": interpretation if total_parameters > 0 else "Not calculated",
                        "Total parameters compared": total_parameters
                    }
                }
                
                if can_calculate_condition1 and can_calculate_condition2 and can_calculate_condition3:
                    results["Visual Score"] = {
                        "Score": score,
                        "Message": message,
                        "Conditions fulfilled": conditions_fulfilled
                    }
                
                # Convert to JSON
                import json
                json_str = json.dumps(results, indent=4)
                
                # Create download button
                st.download_button(
                    label="Click to download JSON",
                    data=json_str,
                    file_name="assessment_results.json",
                    mime="application/json",
                    key="download_json_button"
                )

    create_assessment_results()