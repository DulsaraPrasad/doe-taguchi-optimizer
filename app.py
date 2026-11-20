import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="DoE & Taguchi Process Optimizer", layout="wide")

st.title("📊 Design of Experiments (DoE): Taguchi & ANOVA Optimizer")
st.markdown(
    "Generate **Taguchi Orthogonal Arrays**, compute **Signal-to-Noise (S/N) Ratios**, "
    "perform **ANOVA**, and identify optimal process parameters."
)

# Standard Taguchi Orthogonal Arrays (0-indexed level indices)
ORTHOGONAL_ARRAYS = {
    "L4 (2³ — Up to 3 Factors, 2 Levels)": {
        "levels": 2,
        "max_factors": 3,
        "matrix": np.array([
            [0, 0, 0],
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ]),
    },
    "L8 (2⁷ — Up to 7 Factors, 2 Levels)": {
        "levels": 2,
        "max_factors": 7,
        "matrix": np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [0, 1, 1, 1, 1, 0, 0],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 0],
            [1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 0, 0, 1],
        ]),
    },
    "L9 (3⁴ — Up to 4 Factors, 3 Levels)": {
        "levels": 3,
        "max_factors": 4,
        "matrix": np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 1],
            [0, 2, 2, 2],
            [1, 0, 1, 2],
            [1, 1, 2, 0],
            [1, 2, 0, 1],
            [2, 0, 2, 1],
            [2, 1, 0, 2],
            [2, 2, 1, 0],
        ]),
    },
    "L16 (4⁵ — Up to 5 Factors, 4 Levels)": {
        "levels": 4,
        "max_factors": 5,
        "matrix": np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 2, 2, 2, 2],
            [0, 3, 3, 3, 3],
            [1, 0, 1, 2, 3],
            [1, 1, 0, 3, 2],
            [1, 2, 3, 0, 1],
            [1, 3, 2, 1, 0],
            [2, 0, 2, 3, 1],
            [2, 1, 3, 2, 0],
            [2, 2, 0, 1, 3],
            [2, 3, 1, 0, 2],
            [3, 0, 3, 1, 2],
            [3, 1, 2, 0, 3],
            [3, 2, 1, 3, 0],
            [3, 3, 0, 2, 1],
        ]),
    },
}

# Built-in realistic materials engineering preset (L9 ZnO Photocatalytic Degradation Optimization)
DEMO_L9_DATA = {
    "array": "L9 (3⁴ — Up to 4 Factors, 3 Levels)",
    "goal": "Larger is Better",
    "factors": [
        {"name": "Calcination Temp (°C)", "levels": ["400", "500", "600"]},
        {"name": "Ag Dopant (wt%)", "levels": ["1.0", "2.5", "4.0"]},
        {"name": "Solution pH", "levels": ["5", "7", "9"]},
        {"name": "Stirring Time (min)", "levels": ["30", "60", "90"]},
    ],
    "responses": [
        [72.4, 73.1],
        [84.2, 85.0],
        [79.5, 78.9],
        [81.0, 81.8],
        [93.6, 94.2],
        [88.1, 87.5],
        [76.8, 77.4],
        [86.5, 85.9],
        [82.3, 83.0],
    ],
}

# Sidebar Configuration
st.sidebar.header("1. Experiment Setup")
use_demo = st.sidebar.checkbox("Load Sample Case Study (ZnO Synthesis L9)", value=True)

if use_demo:
    array_choice = DEMO_L9_DATA["array"]
    goal = st.sidebar.selectbox(
        "Quality Characteristic (Objective)",
        ["Larger is Better", "Smaller is Better", "Nominal is Best"],
        index=0,
    )
    num_factors = 4
    num_replicates = 2
else:
    array_choice = st.sidebar.selectbox("Select Orthogonal Array", list(ORTHOGONAL_ARRAYS.keys()), index=2)
    spec = ORTHOGONAL_ARRAYS[array_choice]
    num_factors = st.sidebar.slider("Number of Control Factors", 2, spec["max_factors"], min(3, spec["max_factors"]))
    num_replicates = st.sidebar.number_input("Replicates per Trial (n)", min_value=1, max_value=10, value=2)
    goal = st.sidebar.selectbox(
        "Quality Characteristic (Objective)",
        ["Larger is Better", "Smaller is Better", "Nominal is Best"],
    )

spec = ORTHOGONAL_ARRAYS[array_choice]
n_levels = spec["levels"]
matrix = spec["matrix"][:, :num_factors]

# Factor & Level Definition
st.subheader("1. Control Factors & Levels")
factor_configs = []
cols = st.columns(num_factors)

for i in range(num_factors):
    with cols[i]:
        if use_demo:
            default_name = DEMO_L9_DATA["factors"][i]["name"]
            default_levels = DEMO_L9_DATA["factors"][i]["levels"]
        else:
            default_name = f"Factor {chr(65 + i)}"
            default_levels = [f"Level {lvl + 1}" for lvl in range(n_levels)]

        fname = st.text_input(f"Factor {chr(65 + i)} Name", value=default_name, key=f"fname_{i}")
        flevels = []
        for lvl in range(n_levels):
            val = st.text_input(
                f"L{lvl + 1}",
                value=default_levels[lvl],
                key=f"f_{i}_l_{lvl}",
            )
            flevels.append(val)
        factor_configs.append({"name": fname, "levels": flevels})

# Build Experiment Design Matrix DataFrame
design_rows = []
for trial_idx in range(matrix.shape[0]):
    row = {"Trial": trial_idx + 1}
    for f_idx in range(num_factors):
        lvl_idx = matrix[trial_idx, f_idx]
        row[factor_configs[f_idx]["name"]] = factor_configs[f_idx]["levels"][lvl_idx]
    for r_idx in range(num_replicates):
        if use_demo:
            row[f"Run {r_idx + 1}"] = DEMO_L9_DATA["responses"][trial_idx][r_idx]
        else:
            row[f"Run {r_idx + 1}"] = 10.0 + trial_idx * 1.5 + r_idx * 0.2
    design_rows.append(row)

design_df = pd.DataFrame(design_rows)

st.subheader("2. Orthogonal Array & Experimental Responses")
st.caption("Edit the response values directly in the table below to run live Taguchi & ANOVA calculations.")

factor_col_names = [fc["name"] for fc in factor_configs]
edited_df = st.data_editor(
    design_df,
    disabled=["Trial"] + factor_col_names,
    use_container_width=True,
    hide_index=True,
)

# Calculate Mean Response and S/N Ratio per trial
run_cols = [f"Run {r + 1}" for r in range(num_replicates)]
responses_arr = edited_df[run_cols].to_numpy(dtype=float)

# Guard against zero/negative values in log calculations
safe_responses = np.where(np.abs(responses_arr) < 1e-12, 1e-12, responses_arr)
mean_y = np.mean(responses_arr, axis=1)

if goal == "Larger is Better":
    sn_ratios = -10.0 * np.log10(np.mean(1.0 / (safe_responses ** 2), axis=1))
elif goal == "Smaller is Better":
    sn_ratios = -10.0 * np.log10(np.mean(safe_responses ** 2, axis=1))
else:  # Nominal is Best
    if num_replicates < 2:
        st.error("'Nominal is Best' requires at least 2 replicates per trial to compute sample variance.")
        st.stop()
    var_y = np.var(responses_arr, axis=1, ddof=1)
    safe_var = np.where(var_y < 1e-12, 1e-12, var_y)
    sn_ratios = 10.0 * np.log10((mean_y ** 2) / safe_var)

results_df = edited_df.copy()
results_df["Mean Response"] = np.round(mean_y, 4)
results_df["S/N Ratio (dB)"] = np.round(sn_ratios, 4)

with st.expander("View Computed Trial Means & S/N Ratios", expanded=False):
    st.dataframe(results_df, use_container_width=True, hide_index=True)

# Main Effects Response Table (S/N Ratio)
overall_sn_mean = float(np.mean(sn_ratios))
overall_y_mean = float(np.mean(mean_y))

response_table_rows = []
optimal_levels = {}
optimal_sn_contributions = []
optimal_y_contributions = []

for f_idx in range(num_factors):
    fname = factor_configs[f_idx]["name"]
    flevels = factor_configs[f_idx]["levels"]
    level_sn_means = []
    level_y_means = []

    for lvl_idx in range(n_levels):
        mask = matrix[:, f_idx] == lvl_idx
        level_sn_means.append(float(np.mean(sn_ratios[mask])))
        level_y_means.append(float(np.mean(mean_y[mask])))

    delta = max(level_sn_means) - min(level_sn_means)
    best_lvl_idx = int(np.argmax(level_sn_means))  # Higher S/N is always optimal in Taguchi
    optimal_levels[fname] = flevels[best_lvl_idx]
    optimal_sn_contributions.append(level_sn_means[best_lvl_idx] - overall_sn_mean)
    optimal_y_contributions.append(level_y_means[best_lvl_idx] - overall_y_mean)

    row_dict = {"Factor": fname}
    for lvl_idx in range(n_levels):
        row_dict[f"Level {lvl_idx + 1} ({flevels[lvl_idx]})"] = round(level_sn_means[lvl_idx], 3)
    row_dict["Delta (Max − Min)"] = round(delta, 3)
    response_table_rows.append(row_dict)

resp_table_df = pd.DataFrame(response_table_rows)
resp_table_df["Rank"] = resp_table_df["Delta (Max − Min)"].rank(ascending=False, method="min").astype(int)

# Predicted Optimal Performance
predicted_opt_sn = overall_sn_mean + sum(optimal_sn_contributions)
predicted_opt_y = overall_y_mean + sum(optimal_y_contributions)

# Summary Metrics
st.subheader("3. Optimal Parameter Combination & Prediction")
opt_cols = st.columns(num_factors + 2)
for f_idx, fname in enumerate(factor_col_names):
    with opt_cols[f_idx]:
        st.metric(f"Optimal {fname}", optimal_levels[fname])

with opt_cols[num_factors]:
    st.metric("Predicted S/N Ratio", f"{predicted_opt_sn:.2f} dB")
with opt_cols[num_factors + 1]:
    st.metric("Predicted Mean Response", f"{predicted_opt_y:.3f}")

# Main Effects Plot (Plotly)
st.subheader("4. Main Effects Plot for S/N Ratios")
fig = make_subplots(
    rows=1,
    cols=num_factors,
    subplot_titles=factor_col_names,
    shared_yaxes=True,
)

for f_idx in range(num_factors):
    fname = factor_configs[f_idx]["name"]
    flevels = factor_configs[f_idx]["levels"]
    y_vals = [resp_table_df.loc[f_idx, f"Level {lvl + 1} ({flevels[lvl]})"] for lvl in range(n_levels)]

    fig.add_trace(
        go.Scatter(
            x=flevels,
            y=y_vals,
            mode="lines+markers",
            name=fname,
            line=dict(color="#2563EB", width=2.5),
            marker=dict(size=9, color="#1D4ED8"),
        ),
        row=1,
        col=f_idx + 1,
    )
    fig.add_hline(
        y=overall_sn_mean,
        line_dash="dash",
        line_color="#DC2626",
        row=1,
        col=f_idx + 1,
    )

fig.update_yaxes(title_text="Mean S/N Ratio (dB)", row=1, col=1)
fig.update_layout(
    height=380,
    showlegend=False,
    template="plotly_white",
    title_text=f"Main Effects Plot (Red Dashed Line = Overall Mean S/N: {overall_sn_mean:.2f} dB)",
)
st.plotly_chart(fig, use_container_width=True)

# Response Table & ANOVA Table Side-by-Side
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("5. Response Table for S/N Ratios")
    st.dataframe(resp_table_df, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("6. Analysis of Variance (ANOVA on S/N)")
    N_trials = len(sn_ratios)
    ss_total = float(np.sum((sn_ratios - overall_sn_mean) ** 2))
    df_total = N_trials - 1
    runs_per_level = N_trials / n_levels

    anova_rows = []
    ss_factors_sum = 0.0
    df_factors_sum = 0

    for f_idx in range(num_factors):
        fname = factor_configs[f_idx]["name"]
        ss_f = 0.0
        for lvl_idx in range(n_levels):
            mask = matrix[:, f_idx] == lvl_idx
            lvl_mean = float(np.mean(sn_ratios[mask]))
            ss_f += runs_per_level * ((lvl_mean - overall_sn_mean) ** 2)

        df_f = n_levels - 1
        ms_f = ss_f / df_f
        contrib_pct = (ss_f / ss_total * 100.0) if ss_total > 0 else 0.0

        ss_factors_sum += ss_f
        df_factors_sum += df_f

        anova_rows.append({
            "Source": fname,
            "DF": df_f,
            "Seq SS": round(ss_f, 4),
            "Adj MS": round(ms_f, 4),
            "F-Value": None,
            "Contribution (%)": round(contrib_pct, 2),
        })

    ss_error = max(ss_total - ss_factors_sum, 0.0)
    df_error = df_total - df_factors_sum

    if df_error > 0 and ss_error > 1e-12:
        ms_error = ss_error / df_error
        for r in anova_rows:
            r["F-Value"] = round(r["Adj MS"] / ms_error, 3)
        anova_rows.append({
            "Source": "Residual Error",
            "DF": df_error,
            "Seq SS": round(ss_error, 4),
            "Adj MS": round(ms_error, 4),
            "F-Value": "—",
            "Contribution (%)": round((ss_error / ss_total * 100.0) if ss_total > 0 else 0.0, 2),
        })
    else:
        for r in anova_rows:
            r["F-Value"] = "Saturated"

    anova_rows.append({
        "Source": "Total",
        "DF": df_total,
        "Seq SS": round(ss_total, 4),
        "Adj MS": "—",
        "F-Value": "—",
        "Contribution (%)": 100.00,
    })

    anova_df = pd.DataFrame(anova_rows)
    st.dataframe(anova_df, use_container_width=True, hide_index=True)

# Export Results
csv_data = results_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Complete DoE Results (CSV)",
    data=csv_data,
    file_name="taguchi_doe_analysis.csv",
    mime="text/csv",
)