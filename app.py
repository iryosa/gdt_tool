import streamlit as st
import pandas as pd
import re
from utils.calculations import calculate_lod, calculate_gsd, model_resolution_control

st.set_page_config(page_title="GDT Verification Tool", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        color: #FFFFFF !important;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    .section-title {
        color: #FFB433 !important;
        font-size: 1.6rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    h2 {
        color: #E5E1DA;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #B3C8CF;
        padding-bottom: 0.5rem;
        text-transform: none;
    }
    
    h3 {
        color: #B3C8CF;
        font-size: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        text-transform: none;
    }
    
    .caption {
        color: #89A8B2;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: #E5E1DA;
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
    
    .stTabs [aria-selected="true"] {
        background-color: #B3C8CF;
        color: #000000;
    }
    
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
        background-color: #FFB433;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Geometric Digital Twin Verification Tool</h1>', unsafe_allow_html=True)

# Optimized DQ Elements Lists (removed unwanted measures)
FEATURE_DQ_DATA = [
    {
        "Evaluation Category": "Category: Mandatory", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Accuracy", 
        "Measure": "Positional absolute (external)",
        "Hint": "Alignment of the model with real-world context",
        "Input_Type": "decimal"
    },
    {
        "Evaluation Category": "Category: Mandatory", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Accuracy", 
        "Measure": "Positional relative (internal)",
        "Hint": "Internal consistency of the model",
        "Input_Type": "decimal"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Commission", 
        "Measure": "Excess items",
        "Hint": "Items are not correctly presented in the model",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Commission", 
        "Measure": "Number of excess items",
        "Hint": "The number of items within the model that are incorrectly represented or should not have been included",
        "Input_Type": "integer"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Commission", 
        "Measure": "Rate of excess items",
        "Hint": "The number of incorrect items within the model relative to the total number of items represented",
        "Input_Type": "calculated_rate",
        "Depends_On": "Number of excess items"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Commission", 
        "Measure": "Number of duplicate items",
        "Hint": "The total number of duplications within the model",
        "Input_Type": "integer"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Omission", 
        "Measure": "Missing items",
        "Hint": "Required items are missing in the model",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Omission", 
        "Measure": "Number of missing items",
        "Hint": "The number of missing items that should have been presented in the model",
        "Input_Type": "integer"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Completeness", 
        "Sub-Type": "Sub-Type: Omission", 
        "Measure": "Rate of missing items",
        "Hint": "The number of missing items in the model or sample relative to the total number of items represented",
        "Input_Type": "calculated_rate",
        "Depends_On": "Number of missing items"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Temporal Quality", 
        "Measure": "Number of incorrectly classified items",
        "Hint": "The total number of incorrectly classified items",
        "Input_Type": "integer"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Temporal Quality", 
        "Measure": "Misclassification rate",
        "Hint": "The ratio of incorrectly classified items to the total number of items",
        "Input_Type": "calculated_rate",
        "Depends_On": "Number of incorrectly classified items"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Interoperability", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "Data model compliance",
        "Hint": "Compliance with interoperability requirements",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Generalization", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "LoD compliance",
        "Hint": "The degree to which the model meets the required LoD",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Optional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "Conceptual schema compliance",
        "Hint": "Items are compliant with the definitions or rules of the relevant conceptual schema",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Optional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "Number of items not compliant",
        "Hint": "The total number of items that are not compliant with the definitions or rules of the relevant conceptual schema",
        "Input_Type": "integer"
    },
    {
        "Evaluation Category": "Category: Optional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "Not compliant rate",
        "Hint": "The number of items that are not compliant with the definitions or rules of the relevant conceptual schema relative to the total number of items",
        "Input_Type": "calculated_rate",
        "Depends_On": "Number of items not compliant"
    },
    {
        "Evaluation Category": "Category: Optional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Temporal Quality", 
        "Measure": "Temporal accuracy",
        "Hint": "Accuracy of the temporal attributes of the data",
        "Input_Type": "text_with_unit"
    }
]

SCALE_DQ_DATA = [
    {
        "Evaluation Category": "Category: Mandatory", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Accuracy", 
        "Measure": "Positional absolute (external)",
        "Hint": "Alignment of the model with real-world context",
        "Input_Type": "decimal"
    },
    {
        "Evaluation Category": "Category: Mandatory", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Accuracy", 
        "Measure": "Positional relative (internal)",
        "Hint": "Internal consistency of the model",
        "Input_Type": "decimal"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Interoperability", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "Data model compliance",
        "Hint": "Compliance with interoperability requirements",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Conditional", 
        "DQ Type": "Type: Generalization", 
        "Sub-Type": "Sub-Type: N/A", 
        "Measure": "LoD compliance",
        "Hint": "The degree to which the model meets the required LoD",
        "Input_Type": "yes_no"
    },
    {
        "Evaluation Category": "Category: Optional", 
        "DQ Type": "Type: Consistency", 
        "Sub-Type": "Sub-Type: Temporal Quality", 
        "Measure": "Temporal accuracy",
        "Hint": "Accuracy of the temporal attributes of the data",
        "Input_Type": "text_with_unit"
    }
]

# Rate calculation mapping
RATE_MEASURES = {
    "Rate of excess items": "Number of excess items",
    "Rate of missing items": "Number of missing items",
    "Misclassification rate": "Number of incorrectly classified items",
    "Not compliant rate": "Number of items not compliant"
}

def create_input_field(dq, index, tab_prefix, total_features=None):
    """Create appropriate input field based on measure type"""
    measure = dq["Measure"]
    input_type = dq["Input_Type"]
    key = f"{tab_prefix}_{index}"
    
    if input_type == "decimal":
        return st.number_input(
            f"🔢 Enter value for `{measure}`",
            min_value=0.0,
            format="%.3f",
            step=0.001,
            key=f"{key}_value"
        )
    elif input_type == "integer":
        return st.number_input(
            f"🔢 Enter value for `{measure}`",
            min_value=0,
            step=1,
            key=f"{key}_value"
        )
    elif input_type == "yes_no":
        return st.radio(
            f"Select for `{measure}`",
            options=["Yes", "No"],
            key=f"{key}_value"
        )
    elif input_type == "calculated_rate":
        if measure in RATE_MEASURES and total_features:
            depends_on = RATE_MEASURES[measure]
            # Find the corresponding number measure
            data_list = FEATURE_DQ_DATA if "feature" in tab_prefix else SCALE_DQ_DATA
            number_index = next((i for i, d in enumerate(data_list) if d["Measure"] == depends_on), None)
            
            if number_index is not None:
                number_value = st.session_state.get(f"{tab_prefix}_{number_index}_value", 0)
                if isinstance(number_value, (int, float)) and total_features > 0:
                    rate = (number_value / total_features) * 100
                    st.markdown(f"**Calculated Rate:** {rate:.2f}%")
                    return f"{rate:.2f}%"
                else:
                    st.info(f"Please enter a valid number for {depends_on} to calculate the rate.")
                    return "N/D"
            else:
                st.info(f"Could not find the corresponding number measure for {measure}")
                return "N/D"
        else:
            st.info("Please enter the total number of features to calculate the rate.")
            return "N/D"
    else:  # text_with_unit
        col1, col2 = st.columns([2, 1])
        with col1:
            value = st.text_input(f"🔢 Enter value for `{measure}`", key=f"{key}_value")
        with col2:
            unit = st.text_input(f"📏 Unit", key=f"{key}_unit")
        return {"value": value, "unit": unit}

def create_model_verification_form(tab_prefix, model_name):
    """Create the model verification form"""
    st.markdown(f'<h1 class="section-title" style="font-size: 1.4rem;">{model_name}</h1>', unsafe_allow_html=True)
    
    # GDT Characteristics
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 1. Geometric Digital Twin Characteristics</h2>', unsafe_allow_html=True)
    
    if tab_prefix == "g0":
        gdt_scale = st.selectbox("Scale", ["Building Part", "Building", "Site", "Urban"], key=f"{tab_prefix}_gdt_scale")
    else:
        # For Model G(t), use the value from Model G(0)
        g0_scale = st.session_state.get("g0_gdt_scale", "Building Part")
        st.selectbox("Scale", ["Building Part", "Building", "Site", "Urban"], 
                    key=f"{tab_prefix}_gdt_scale", 
                    index=["Building Part", "Building", "Site", "Urban"].index(g0_scale), 
                    disabled=True)
    
    gdt_scale_value = st.text_input("Scale Value (optional)", key=f"{tab_prefix}_gdt_scale_value")
    gdt_stage = st.selectbox("Building Life Cycle Stage", 
                            ["Pre-construction", "Construction A5", "Use B1-B2", "Use B3-B5", "End of Life", "Beyond Life Cycle"], 
                            key=f"{tab_prefix}_gdt_stage")
    agr = st.number_input("Average Ground Resolution (AGR) of Model [mm/px]", format="%.3f", key=f"{tab_prefix}_agr")

    # Sample Election
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 2. Sample for Verification</h2>', unsafe_allow_html=True)
    
    if tab_prefix == "g0":
        sample_type = st.radio("Sample Type", ["Feature-based", "Scale-based"], key=f"{tab_prefix}_sample_type")
    else:
        g0_sample_type = st.session_state.get("g0_sample_type", "Feature-based")
        st.radio("Sample Type", ["Feature-based", "Scale-based"], 
                key=f"{tab_prefix}_sample_type", 
                index=["Feature-based", "Scale-based"].index(g0_sample_type), 
                disabled=True)
        sample_type = g0_sample_type

    if sample_type == "Feature-based":
        total_features = st.number_input("Total Number of Features (items)", min_value=0, value=0, key=f"{tab_prefix}_total_features")
    else:
        sample_scale = st.text_input("Sample Scale (optional)", key=f"{tab_prefix}_sample_scale")
        total_features = None

    # Parameters for Updating (only in G(0))
    if tab_prefix == "g0":
        st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 3. Parameters for Updating (optional)</h2>', unsafe_allow_html=True)
        updates = st.number_input("Number of Previous Updates", min_value=0, key=f"{tab_prefix}_updates")
        schedule = st.selectbox("Update Schedule", ["Planned", "Event-driven"], key=f"{tab_prefix}_schedule")
        survey_type = st.selectbox("Survey Type", ["Image-based", "Range-based"], key=f"{tab_prefix}_survey_type")
        acq_sequence = st.selectbox("Data Acquisition Sequence", ["Parallel", "Sequential", "Mixed"], key=f"{tab_prefix}_acq_sequence")

    # LoD Calculation
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 4. LoD Calculation</h2>', unsafe_allow_html=True)
    suggested_lod = calculate_lod(agr)
    st.markdown(f'<p style="color: #FFB433;"><strong>Suggested LoD:</strong> {suggested_lod}</p>', unsafe_allow_html=True)

    # Feature's RMSE
    st.markdown('<h3 style="font-size: 1.4rem;">Feature\'s RMSE (optional)</h3>', unsafe_allow_html=True)
    st.markdown("*RMSE of the actual dimensions of specific elements (e.g., roof elements, windows) between the model and real-world measurements obtained with more precise equipment*")
    rmse_value = st.number_input("Value", min_value=0.0, format="%.2f", key=f"{tab_prefix}_rmse_value")

    # GSD & Model Resolution
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Step 4.1 Ground Sample Distance (GSD) Calculation</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sensor_size = st.number_input("Sensor size (mm)", min_value=0.0, key=f"{tab_prefix}_sensor_size")
        focal_length = st.number_input("Focal length (mm)", min_value=0.0, key=f"{tab_prefix}_focal_length")
    with col2:
        flight_height = st.number_input("Flight height (m)", min_value=0, step=1, key=f"{tab_prefix}_flight_height")
        image_width = st.number_input("Image width (px)", min_value=1, value=None, key=f"{tab_prefix}_image_width")

    # Calculate GSD if all values are provided
    if all([sensor_size > 0, focal_length > 0, flight_height > 0, image_width is not None and image_width > 0]):
        gsd = calculate_gsd(sensor_size, focal_length, flight_height, image_width)
        model_resolution = model_resolution_control(gsd, agr)

        st.write(f"**Calculated GSD:** {gsd:.4f} mm")
        st.write(f"**Resolution Achieved:** {model_resolution * 100:.2f}%")
        
        st.session_state[f"{tab_prefix}_model_resolution"] = model_resolution
    else:
        st.info("Please enter all required values to calculate GSD and Resolution Achieved.")
        st.session_state[f"{tab_prefix}_model_resolution"] = None

    # Data Quality Elements
    st.markdown('<h2 style="color: #FFB433; font-size: 1.4rem;">Step 5. Data Quality Elements</h2>', unsafe_allow_html=True)
    
    data_list = FEATURE_DQ_DATA if sample_type == "Feature-based" else SCALE_DQ_DATA
    selected_dq = []
    
    st.markdown('<h3 style="color: #B3C8CF; font-size: 1.2rem;">📋 Data Quality Checklist</h3>', unsafe_allow_html=True)

    for i, dq in enumerate(data_list):
        # For Model G(t), only show measures selected in Model G(0)
        if tab_prefix == "gt" and not st.session_state.get(f"g0_{i}_check", False):
            continue
            
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            if tab_prefix == "g0":
                checked = st.checkbox("", key=f"{tab_prefix}_{i}_check")
            else:
                # For Model G(t), automatically check if it was selected in G(0)
                checked = st.session_state.get(f"g0_{i}_check", False)
                st.checkbox("", value=checked, key=f"{tab_prefix}_{i}_check", disabled=True)
        
        with col2:
            st.markdown(f"**{dq['Measure']}**  \n*{dq['Evaluation Category']} | {dq['DQ Type']} | {dq.get('Sub-Type', '')}*  \n:gray[{dq['Hint']}]")

        if checked:
            dq_input = {"Measure": dq["Measure"]}
            
            if sample_type == "Feature-based":
                total_for_calc = total_features
            else:
                total_for_calc = None
                
            value = create_input_field(dq, i, f"{tab_prefix}", total_for_calc)
            
            if isinstance(value, dict):  # text_with_unit
                dq_input["Value"] = value["value"] if value["value"] else "N/D"
                dq_input["Unit"] = value["unit"] if value["unit"] else "N/D"
            else:
                dq_input["Value"] = value if value else "N/D"
                dq_input["Unit"] = "N/A"
            
            selected_dq.append(dq_input)
            st.markdown("---")

    # Display summary
    if selected_dq:
        st.markdown("### Selected DQ Elements Summary")
        summary_df = pd.DataFrame(selected_dq)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    else:
        st.info("Please select DQ measures to evaluate.")

def create_verification_results():
    """Create the verification results tab"""
    st.markdown('<h1 class="section-title" style="font-size: 1.4rem;">Verification Results</h1>', unsafe_allow_html=True)
    
    # Basic Information
    gdt_scale = st.session_state.get("g0_gdt_scale", "Not specified")
    st.markdown(f'<p><span style="font-weight: bold;">Scale:</span> {gdt_scale}</p>', unsafe_allow_html=True)

    g0_stage = st.session_state.get("g0_gdt_stage", "Not specified")
    gt_stage = st.session_state.get("gt_gdt_stage", "Not specified")
    
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Building Life Cycle Stage</h2>', unsafe_allow_html=True)
    st.write(f"**Model G(0):** {g0_stage}")
    st.write(f"**Model G(t):** {gt_stage}")
    
    # Sample Information
    sample_type = st.session_state.get("g0_sample_type", "Not specified")
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">Sample for Verification</h2>', unsafe_allow_html=True)
    st.write(f"**Selected Type:** {sample_type}")
    
    if sample_type == "Feature-based":
        total_features = st.session_state.get("g0_total_features", "Not specified")
        st.write(f"**Total number of features (items):** {total_features}")
    elif sample_type == "Scale-based":
        sample_scale = st.session_state.get("g0_sample_scale", "Not specified")
        st.write(f"**Sample scale:** {sample_scale}")

    # LoD Summary
    st.markdown('<h2 style="color: #E5E1DA; font-size: 1.4rem;">LoD Calculation Summary</h2>', unsafe_allow_html=True)
    
    g0_agr = st.session_state.get("g0_agr", "N/D")
    g0_suggested_lod = calculate_lod(g0_agr) if g0_agr != "N/D" else "N/D"
    g0_rmse = st.session_state.get("g0_rmse_value", "N/D")
    
    gt_agr = st.session_state.get("gt_agr", "N/D")
    gt_suggested_lod = calculate_lod(gt_agr) if gt_agr != "N/D" else "N/D"
    gt_rmse = st.session_state.get("gt_rmse_value", "N/D")
    
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
    st.dataframe(lod_summary_df, use_container_width=True, hide_index=True)

    # Decision Model
    st.markdown('<h2 style="color: #FFB433; font-size: 1.4rem;">Decision Model based on Mandatory Data Quality Elements</h2>', unsafe_allow_html=True)
    
    # Models alignment data
    st.markdown('<h3 style="color: #E5E1DA; font-size: 1.2rem;">Models Alignment Data (optional)</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        mean_deviation = st.number_input("Mean of geometric deviations μ", format="%.3f", key="mean_deviation")
    with col2:
        std_deviation = st.number_input("Standard deviation σ", format="%.3f", key="std_deviation")
    
    if mean_deviation != 0 and std_deviation != 0:
        deviation_threshold = mean_deviation + 2 * std_deviation
        st.write(f"**Deviation threshold δpos:** {deviation_threshold:.3f}")

    # Condition 1: Model Accuracy Verification
    st.markdown('<h3 style="color: #fbd57a; font-size: 1.2rem;">Condition 1: Model Accuracy Verification</h3>', unsafe_allow_html=True)
    
    # Calculate Dacc
    data_list = FEATURE_DQ_DATA if sample_type == "Feature-based" else SCALE_DQ_DATA
    g0_abs_pos = g0_rel_pos = gt_abs_pos = gt_rel_pos = None
    
    for i, dq in enumerate(data_list):
        if dq["Measure"] == "Positional absolute (external)":
            if st.session_state.get(f"g0_{i}_check", False):
                g0_abs_pos = st.session_state.get(f"g0_{i}_value", 0)
            if st.session_state.get(f"gt_{i}_check", False):
                gt_abs_pos = float(gt_abs_pos) if isinstance(gt_abs_pos, str) else gt_abs_pos
            gt_rel_pos = float(gt_rel_pos) if isinstance(gt_rel_pos, str) else gt_rel_pos
            
            dacc = abs((1 - (gt_rel_pos/g0_rel_pos)) - (1 - (gt_abs_pos/g0_abs_pos)))
            st.write(f"**Accuracy difference between models Dacc:** {dacc:.3f}")
        except (ValueError, TypeError, ZeroDivisionError) as e:
            st.write("**Accuracy difference between models Dacc:** Not calculated")
            st.caption(f"Error in calculation: {str(e)}")
    else:
        st.write("**Accuracy difference between models Dacc:** Not calculated")
        st.caption("All required positional accuracy measures must be provided and non-zero")
    
    delta_d = st.number_input("δD (Accuracy difference threshold)", format="%.3f", key="delta_d")
    
    if dacc is not None and delta_d != 0:
        comparison_result = "Consistent accuracy in both models" if dacc < delta_d else "Decline in model G(t) accuracy"
        st.write(f"**Dacc vs. δD comparison:** {comparison_result}")

    # Condition 2: Model LoD Verification
    st.markdown('<h3 style="color: #fbd57a; font-size: 1.2rem;">Condition 2: Model LoD Verification</h3>', unsafe_allow_html=True)
    
    if g0_suggested_lod != "N/D" and gt_suggested_lod != "N/D":
        lod_comparison = "Consistent LoD for both models" if g0_suggested_lod == gt_suggested_lod else "Inconsistent LoD"
        st.write(f"**LoD Verification:** {lod_comparison}")
    else:
        st.write("**LoD Verification:** Not calculated")

    # Condition 3: Model Resolution Verification
    st.markdown('<h3 style="color: #fbd57a; font-size: 1.2rem;">Condition 3: Model Resolution Verification</h3>', unsafe_allow_html=True)
    
    g0_resolution = st.session_state.get('g0_model_resolution')
    gt_resolution = st.session_state.get('gt_model_resolution')
    
    if g0_resolution is not None and gt_resolution is not None:
        resolution_comparison = "Decline in model G(t) resolution" if gt_resolution < g0_resolution else "Increase in model G(t) resolution"
        st.write(f"**Resolution Verification:** {resolution_comparison}")
    else:
        st.write("**Resolution Verification:** Not calculated")

    # Verification Score
    can_calculate_condition1 = dacc is not None and delta_d != 0
    can_calculate_condition2 = g0_suggested_lod != "N/D" and gt_suggested_lod != "N/D"
    can_calculate_condition3 = g0_resolution is not None and gt_resolution is not None
    
    if can_calculate_condition1 and can_calculate_condition2 and can_calculate_condition3:
        st.markdown('<h2 style="color: #fbd57a; font-size: 1.4rem;">Verification Score</h2>', unsafe_allow_html=True)
        
        conditions_fulfilled = 0
        
        if dacc < delta_d:
            conditions_fulfilled += 1
        if g0_suggested_lod == gt_suggested_lod:
            conditions_fulfilled += 1
        if gt_resolution >= g0_resolution:
            conditions_fulfilled += 1
        
        if conditions_fulfilled == 0:
            score = "❌ Critical"
            color = "#FF0000"
            message = "Decline in all metrics for model G(t). Unsuitable for the updating process."
        elif conditions_fulfilled == 1:
            score = "⚠️ Warning"
            color = "#FFA500"
            message = "Only one of three conditions is fulfilled. Decline in metrics for model G(t). Unsuitable for the updating process."
        elif conditions_fulfilled == 2:
            score = "⚠️ Partial"
            color = "#FFD700"
            message = "Two of three conditions are fulfilled. Model is suitable for partial updating."
        else:
            score = "✅ Suitable"
            color = "#008000"
            message = "Model G(t) outperforms model G(0). Suitable for updating."
        
        st.markdown(f"""
        <div style='background-color: {color}; padding: 20px; border-radius: 10px; color: white;'>
            <h2 style='margin: 0;'>{score}</h2>
            <p style='margin: 10px 0 0 0;'>{message}</p>
        </div>
        """, unsafe_allow_html=True)

def download_csv_data(prefix, model_name):
    """Generate CSV data for download"""
    import csv
    import io
    
    csv_data = []
    
    # GDT Characteristics
    csv_data.extend([
        ["GDT Characteristics", "", ""],
        ["Scale", st.session_state.get(f"{prefix}_gdt_scale", "Not specified"), ""],
        ["Scale Value", st.session_state.get(f"{prefix}_gdt_scale_value", "Not specified"), ""],
        ["Building Life Cycle Stage", st.session_state.get(f"{prefix}_gdt_stage", "Not specified"), ""],
        ["AGR of model", st.session_state.get(f"{prefix}_agr", "Not specified"), "mm/px"],
        ["", "", ""]
    ])
    
    # Sample for Verification
    sample_type = st.session_state.get(f"{prefix}_sample_type", "Not specified")
    csv_data.extend([
        ["Sample for Verification", "", ""],
        ["Sample Type", sample_type, ""]
    ])
    
    if sample_type == "Feature-based":
        csv_data.append(["Total Features", st.session_state.get(f"{prefix}_total_features", "Not specified"), ""])
    else:
        csv_data.append(["Sample Scale", st.session_state.get(f"{prefix}_sample_scale", "Not specified"), ""])
    
    csv_data.append(["", "", ""])
    
    # Parameters for Updating (only for G(0))
    if prefix == "g0":
        csv_data.extend([
            ["Parameters for Updating", "", ""],
            ["Number of Previous Updates", st.session_state.get(f"{prefix}_updates", "Not specified"), ""],
            ["Update Schedule", st.session_state.get(f"{prefix}_schedule", "Not specified"), ""],
            ["Survey Type", st.session_state.get(f"{prefix}_survey_type", "Not specified"), ""],
            ["Data Acquisition Sequence", st.session_state.get(f"{prefix}_acq_sequence", "Not specified"), ""],
            ["", "", ""]
        ])
    
    # LoD Calculation
    agr = st.session_state.get(f"{prefix}_agr", 0)
    csv_data.extend([
        ["LoD Calculation", "", ""],
        ["Suggested LoD", calculate_lod(agr) if agr > 0 else "Not calculated", ""],
        ["Feature's RMSE", st.session_state.get(f"{prefix}_rmse_value", "Not specified"), ""],
        ["", "", ""]
    ])
    
    # GSD Calculation
    sensor_size = st.session_state.get(f'{prefix}_sensor_size')
    focal_length = st.session_state.get(f'{prefix}_focal_length')
    flight_height = st.session_state.get(f'{prefix}_flight_height')
    image_width = st.session_state.get(f'{prefix}_image_width')
    
    if all(v is not None and v > 0 for v in [sensor_size, focal_length, flight_height, image_width]):
        gsd = calculate_gsd(sensor_size, focal_length, flight_height, image_width)
        gsd_value = f"{gsd:.4f} mm"
    else:
        gsd_value = "Not calculated"
    
    csv_data.extend([
        ["GSD Calculation", "", ""],
        ["Sensor Size", st.session_state.get(f"{prefix}_sensor_size", "Not specified"), "mm"],
        ["Focal Length", st.session_state.get(f"{prefix}_focal_length", "Not specified"), "mm"],
        ["Flight Height", st.session_state.get(f"{prefix}_flight_height", "Not specified"), "m"],
        ["Image Width", st.session_state.get(f"{prefix}_image_width", "Not specified"), "px"],
        ["Calculated GSD", gsd_value, ""],
        ["Resolution Achieved", f"{st.session_state.get(f'{prefix}_model_resolution', 0) * 100:.2f}%" if st.session_state.get(f'{prefix}_model_resolution') is not None else "Not calculated", ""],
        ["", "", ""]
    ])
    
    # Selected Measures
    csv_data.append(["Selected Measures", "", ""])
    sample_type = st.session_state.get(f"{prefix}_sample_type", "Feature-based")
    data_list = FEATURE_DQ_DATA if sample_type == "Feature-based" else SCALE_DQ_DATA
    
    for i, dq in enumerate(data_list):
        if st.session_state.get(f"{prefix}_{i}_check", False):
            csv_data.append([
                dq["Measure"],
                st.session_state.get(f"{prefix}_{i}_value", "Not specified"),
                st.session_state.get(f"{prefix}_{i}_unit", "N/A")
            ])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)
    
    return output.getvalue()

# Main App
tab1, tab2, tab3 = st.tabs(["Model G(0)", "Model G(t)", "Verification Results"])

with tab1:
    create_model_verification_form("g0", "Model G(0)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Model Data", use_container_width=True, key="g0_download_button"):
            csv_data = download_csv_data("g0", "Model G(0)")
            st.download_button(
                label="Click to download",
                data=csv_data,
                file_name="model_g0_data.csv",
                mime="text/csv",
                key="g0_download_csv_button"
            )
    
    with col2:
        if st.button("💾 Save & Continue to Model G(t)", use_container_width=True, key="g0_next_button"):
            st.session_state["g0_saved"] = True
            st.success("Model G(0) data saved! Please click on the 'Model G(t)' tab above to continue.")

with tab2:
    create_model_verification_form("gt", "Model G(t)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Model Data", use_container_width=True, key="gt_download_button"):
            csv_data = download_csv_data("gt", "Model G(t)")
            st.download_button(
                label="Click to download",
                data=csv_data,
                file_name="model_gt_data.csv",
                mime="text/csv",
                key="gt_download_csv_button"
            )
    
    with col2:
        if st.button("💾 Save & View Results", use_container_width=True, key="gt_results_button"):
            st.session_state["gt_saved"] = True
            st.success("Model G(t) data saved! Please click on the 'Verification Results' tab above to view results.")

with tab3:
    create_verification_results() st.session_state.get(f"gt_{i}_value", 0)
        elif dq["Measure"] == "Positional relative (internal)":
            if st.session_state.get(f"g0_{i}_check", False):
                g0_rel_pos = st.session_state.get(f"g0_{i}_value", 0)
            if st.session_state.get(f"gt_{i}_check", False):
                gt_rel_pos = st.session_state.get(f"gt_{i}_value", 0)
    
    dacc = None
    if all(v is not None and v != 0 for v in [g0_abs_pos, g0_rel_pos, gt_abs_pos, gt_rel_pos]):
        try:
            g0_abs_pos = float(g0_abs_pos) if isinstance(g0_abs_pos, str) else g0_abs_pos
            g0_rel_pos = float(g0_rel_pos) if isinstance(g0_rel_pos, str) else g0_rel_pos
            gt_abs_pos =