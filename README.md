# 📊 Design of Experiments (DoE): Taguchi & ANOVA Process Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_STREAMLIT_APP_URL.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An interactive web application built for materials engineers, researchers, and manufacturing quality analysts to automate **Taguchi Orthogonal Array design**, **Signal-to-Noise (S/N) Ratio analysis**, **Analysis of Variance (ANOVA)**, and **optimal parameter prediction**.

---

## 🚀 Live Demo

👉 **[Launch Interactive Web App](https://doe-taguchi-optimizer-ldxsp742sbggj8zd4earfp.streamlit.app/)**

*(Includes a built-in L<sub>9</sub> case study for ZnO nanoparticle photocatalytic synthesis optimization so you can test the interactive data editor and ANOVA results immediately.)*

---

## ✨ Key Features

- **Standard Orthogonal Arrays:** Automatically generates Taguchi experimental matrices for **L<sub>4</sub> (2³)**, **L<sub>8</sub> (2⁷)**, **L<sub>9</sub> (3⁴)**, and **L<sub>16</sub> (4⁵)** designs.
- **Interactive Experimental Data Grid:** Customize factor names, level settings, replicates, and experimental responses directly inside the browser.
- **Three Quality Characteristics:** Supports **Larger is Better**, **Smaller is Better**, and **Nominal is Best** S/N ratio formulations.
- **Main Effects & Factor Ranking:** Computes level averages, Delta (Max − Min) values, and ranks control factors by statistical impact alongside interactive Plotly Main Effects charts.
- **Full ANOVA Decomposition:** Calculates Degrees of Freedom (DF), Sequential Sum of Squares (Seq SS), Adjusted Mean Squares (Adj MS), F-Values, and Percentage Contribution (%).
- **Optimal Parameter Prediction:** Identifies the optimal factor level combination and predicts the expected S/N ratio (dB) and mean response using the additive Taguchi model.
- **One-Click CSV Export:** Download the complete orthogonal array along with trial means and S/N ratios for lab reports or manuscripts.

---

## 📐 Theoretical Background & Equations

### 1. Taguchi Signal-to-Noise (S/N) Ratios
For *n* replicate measurements (*y₁, y₂, ..., yₙ*) in each experimental trial:

- **Larger is Better** (e.g., yield, efficiency, tensile strength):
  > **S/N = −10 log₁₀ [ (1 / n) ∑ (1 / yᵢ²) ]**

- **Smaller is Better** (e.g., defect rate, surface roughness, impurity level):
  > **S/N = −10 log₁₀ [ (1 / n) ∑ yᵢ² ]**

- **Nominal is Best** (targeting a specific nominal dimension or property):
  > **S/N = 10 log₁₀ ( ȳ² / s² )**  *(where s² is the sample variance)*

### 2. Analysis of Variance (ANOVA)
- **Total Sum of Squares:**
  > **SS<sub>T</sub> = ∑ (SNⱼ − SN̄)²**
- **Factor Sum of Squares** (with *r* trials per level):
  > **SS<sub>A</sub> = ∑ r (SN̄<sub>A,k</sub> − SN̄)²**
- **Percentage Contribution:**
  > **P<sub>A</sub> (%) = (SS<sub>A</sub> / SS<sub>T</sub>) × 100**

### 3. Additive Optimal Prediction
Using the optimal level *k\** for each of the *p* control factors:
> **η̂<sub>opt</sub> = SN̄ + ∑ (SN̄<sub>i,k\*</sub> − SN̄)**

---

## 🛠️ Tech Stack

- **Frontend & Hosting:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Scientific Computing:** SciPy
- **Interactive Visualization:** Plotly

---

## 💻 Local Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/DulsaraPrasad/doe-taguchi-optimizer.git](https://github.com/DulsaraPrasad/doe-taguchi-optimizer.git)
   cd doe-taguchi-optimizer
