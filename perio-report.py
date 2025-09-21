import streamlit as st
import pandas as pd
import datetime
import math
import time
import plotly.express as px

# Relative Risk (RR) mappings for "No" responses
diabetes_rr_map = {
    ("Stage I", "Grade A"): (1.0, "Normal risk; healthy periodontium",
                             "Maintaining good oral Hygiene may reduce your risk of developing diabetes"),
    ("Stage I", "Grade B"): (1.1, "Slight increase in systemic inflammation",
                             "Maintaining good oral Hygiene may reduce your risk of developing diabetes"),
    ("Stage I", "Grade C"): (1.3, "Mild inflammatory burden; early systemic impact",
                             "Improving your oral hygiene and coordinated dental care may reduce your risk of developing diabetes"),
    ("Stage II", "Grade A"): (1.5, "Moderate inflammation; measurable risk increase",
                              "Improving your oral hygiene and coordinated dental care may reduce your risk of developing diabetes"),
    ("Stage II", "Grade B"): (1.7, "Ongoing periodontal damage; higher glucose dysregulation risk",
                              "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage II", "Grade C"): (1.9, "Elevated systemic cytokine load; prediabetes possible",
                              "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage III", "Grade A"): (2.1, "Advanced disease; consistent with studies showing 2× diabetes risk",
                               "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage III", "Grade B"): (2.3, "High systemic inflammation; metabolic complications likely",
                               "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage III", "Grade C"): (2.5, "Known strong association with insulin resistance",
                               "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage IV", "Grade A"): (2.8, "Systemic inflammation persistent; diabetes onset likely",
                              "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage IV", "Grade B"): (3.0, "Significant periodontal destruction: poor glycemic control expected",
                              "Treating gum disease may reduce your risk of developing diabetes"),
    ("Stage IV", "Grade C"): (3.2, "Maximal systemic burden; risk equivalent to other high-risk metabolic conditions",
                              "Treating gum disease may reduce your risk of developing diabetes")
}

cardio_rr_map = {
    ("Stage I", "Grade A"): (1.0, "Healthy periodontium; baseline CVD risk",
                             "Maintaining good oral Hygiene may reduce your risk of developing Cardiovascular Disease"),
    ("Stage I", "Grade B"): (1.1, "Slight systemic inflammation; minimal vascular impact",
                             "Maintaining good oral Hygiene may reduce your risk of developing Cardiovascular Disease"),
    ("Stage I", "Grade C"): (1.2, "Early inflammatory burden; low but measurable vascular risk",
                             "Improving your oral hygiene and coordinated dental care may reduce your risk of developing Cardiovascular Disease"),
    ("Stage II", "Grade A"): (1.4, "Localized chronic inflammation; linked to early endothelial dysfunction",
                              "Improving your oral hygiene and coordinated dental care may reduce your risk of developing Cardiovascular Disease"),
    ("Stage II", "Grade B"): (1.6, "Systemic inflammatory markers rising; moderate vascular risk",
                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage II", "Grade C"): (1.8, "Atherosclerotic changes more likely; moderate to high risk",
                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage III", "Grade A"): (2.0, "Strong correlation with atherosclerosis and plaque instability",
                               "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage III", "Grade B"): (2.2, "Elevated hs-CRP, IL-6; increased risk of MI and stroke",
                               "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage III", "Grade C"): (2.4, "High-risk zone for cardiac events; inflammation contributes to vascular injury",
                               "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage IV", "Grade A"): (2.7, "Chronic systemic inflammation may accelerate arterial calcification",
                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage IV", "Grade B"): (2.9, "Significant vascular impact; commonly co-presents with other CVD risk factors",
                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease"),
    ("Stage IV", "Grade C"): (3.2, "Highest CVD risk tier; vascular insult comparable to smoking or diabetes",
                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease")
}

kidney_rr_map = {
    ("Stage I", "Grade A"): (1.0, "No increased renal risk",
                             "Maintaining good oral Hygiene may reduce your risk of developing Kidney Disease"),
    ("Stage I", "Grade B"): (1.1, "Early inflammation; slight risk",
                             "Maintaining good oral Hygiene may reduce your risk of developing Kidney Disease"),
    ("Stage I", "Grade C"): (1.3, "Gingival inflammation may influence systemic inflammatory load",
                             "Improving your oral hygiene and coordinated dental care may reduce your risk of developing Kidney Disease"),
    ("Stage II", "Grade A"): (1.5, "Periodontal inflammation may begin to affect renal filtration via cytokine release",
                              "Improving your oral hygiene and coordinated dental care may reduce your risk of developing Kidney Disease"),
    ("Stage II", "Grade B"): (1.7,
                              "Moderate risk of renal function decline, particularly in patients with diabetes or hypertension",
                              "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage II", "Grade C"): (1.9, "Subclinical kidney changes more likely; GFR may be impacted",
                              "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage III", "Grade A"): (2.2, "Studies show accelerated GFR decline and higher albuminuria incidence",
                               "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage III", "Grade B"): (2.4, "Chronic inflammation increases renal endothelial dysfunction",
                               "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage III", "Grade C"): (2.6, "Elevated risk of stage 2–3 CKD onset",
                               "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage IV", "Grade A"): (2.9, "Strong correlation with reduced eGFR and higher creatinine levels",
                              "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage IV", "Grade B"): (3.1, "Increased burden on filtration; dialysis risk may rise if unmanaged",
                              "Treating gum disease may reduce your risk of developing Kidney Disease"),
    ("Stage IV", "Grade C"): (3.4, "Very high systemic inflammation; highest risk tier for renal complications",
                              "Treating gum disease may reduce your risk of developing Kidney Disease")
}

dementia_rr_map = {
    ("Stage I", "Grade A"): (1.0, "No increased cognitive risk",
                             "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage I", "Grade B"): (1.1, "Early inflammation; negligible cognitive effect",
                             "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage I", "Grade C"): (1.2, "Mild systemic burden; unclear effect",
                             "Improving your oral hygiene and coordinated dental care may reduce your risk of developing dementia"),
    ("Stage II", "Grade A"): (1.4, "Periodontal inflammation may increase blood-brain barrier permeability",
                              "Improving your oral hygiene and coordinated dental care may reduce your risk of developing dementia"),
    ("Stage II", "Grade B"): (1.6, "Oral pathogens like P. gingivalis and inflammation linked to amyloid accumulation",
                              "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage II", "Grade C"): (1.8, "Increased inflammatory cytokines may accelerate neurodegeneration",
                              "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage III", "Grade A"): (2.0, "Observed correlation with memory decline in longitudinal studies",
                               "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage III", "Grade B"): (2.3, "Chronic oral infection associated with early onset dementia in some cohorts",
                               "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage III", "Grade C"): (2.6, "Inflammation and bacterial toxins implicated in tau and amyloid pathology",
                               "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage IV", "Grade A"): (2.9, "Consistently elevated inflammatory biomarkers; neuroinflammatory cascade likely",
                              "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage IV", "Grade B"): (3.1, "Cognitive decline is frequently seen in elderly with advanced periodontal disease",
                              "Treating gum disease may reduce your risk of developing dementia"),
    ("Stage IV", "Grade C"): (3.4, "High brain exposure to inflammatory mediators and periodontal pathogens",
                              "Treating gum disease may reduce your risk of developing dementia")
}

# Preterm birth map for summary and recommendations
preterm_map = {
    ("Stage I", "Grade A"): ("Gum tissues are healthy, with no known added risk for pregnancy.",
                             "Maintaining routine dental cleanings helps support a healthy pregnancy."),
    ("Stage I", "Grade B"): ("Mild gum irritation is present but not likely to affect pregnancy.",
                             "Improving home care and removing plaque can reverse early gum changes."),
    ("Stage I", "Grade C"): ("Early-stage gum inflammation may slightly increase inflammatory load.",
                             "A professional cleaning can reduce inflammation and support pregnancy health."),
    ("Stage II", "Grade A"): ("Signs of moderate gum infection may modestly increase systemic stress.",
                              "Treatment can reduce bacteria and inflammation to lower risk during pregnancy."),
    ("Stage II", "Grade B"): ("Ongoing gum disease may begin to impact pregnancy-related inflammatory markers.",
                              "A thorough cleaning and good home care can restore gum health."),
    ("Stage II", "Grade C"): ("Moderate inflammation may contribute to pregnancy complications if untreated.",
                              "Addressing gum disease now helps promote full-term delivery."),
    ("Stage III", "Grade A"): ("Advanced periodontal disease can elevate inflammatory markers tied to early labor.",
                               "Timely dental care can reduce this risk and benefit both mother and baby."),
    ("Stage III", "Grade B"): ("Deeper infection increases systemic inflammation that may influence delivery timing.",
                               "Targeted treatment can help reduce potential pregnancy complications."),
    ("Stage III", "Grade C"): ("Severe gum disease is linked with greater risk for preterm birth in research.",
                               "Working with your dental team now helps protect maternal and fetal health."),
    ("Stage IV", "Grade A"): ("Extensive inflammation and tissue damage may contribute to adverse pregnancy outcomes.",
                              "Specialized treatment can significantly reduce inflammation and risk."),
    ("Stage IV", "Grade B"): ("Chronic oral infection is likely influencing your overall health during pregnancy.",
                              "Managing gum disease can improve outcomes for both you and your baby."),
    ("Stage IV", "Grade C"): (
        "Advanced periodontitis is associated with higher risk for early labor and low birth weight.",
        "Comprehensive gum care now is a powerful step toward a safer pregnancy."),
}


# Function to interpolate gauge color based on score or RR
def get_gauge_color(score, min_value=0, max_value=10, is_rr=False):
    if is_rr:
        if max_value == min_value:
            normalized_score = 0
        else:
            normalized_score = min(10, ((score - min_value) / (max_value - min_value)) * 10)
    else:
        normalized_score = min(max(score, 0), 10)
    if normalized_score <= 5:
        r = int(255 * (normalized_score / 5))
        g = 255
        b = 0
    else:
        r = 255
        g = int(255 * (1 - (normalized_score - 5) / 5))
        b = 0
    return f"#{r:02x}{g:02x}{b:02x}"


# Function to generate speedometer SVG
def generate_speedometer(score, label, min_value=0, max_value=10, is_rr=False, key=None):
    if max_value == min_value:
        normalized_score = 0
    else:
        normalized_score = (score - min_value) / (max_value - min_value)
    angle = normalized_score * 180 - 90
    rad = angle * (3.14159 / 180)

    if is_rr:
        num_ticks = 5
        tick_values = [min_value + i * (max_value - min_value) / (num_ticks - 1) for i in range(num_ticks)]
        tick_marks = ""
        tick_labels = ""
        for i, tick_value in enumerate(tick_values):
            tick_angle = (i / (num_ticks - 1)) * 180 - 90
            rad_tick = tick_angle * (3.14159 / 180)
            inner_x = 120 + 85 * math.sin(rad_tick)
            inner_y = 140 - 85 * math.cos(rad_tick)
            outer_x = 120 + 95 * math.sin(rad_tick)
            outer_y = 140 - 95 * math.cos(rad_tick)
            label_x = 120 + 100 * math.sin(rad_tick)
            label_y = 140 - 100 * math.cos(rad_tick)
            if i == 0:
                label_y += 8
            elif i == num_ticks - 1:
                label_y -= 8
            elif i in [1, 3]:
                label_y -= 4
            elif i == 2:
                label_y += 4
            tick_marks += f'<line x1="{inner_x}" y1="{inner_y}" x2="{outer_x}" y2="{outer_y}" stroke="black" stroke-width="2"/>'
            tick_labels += f'<text x="{label_x}" y="{label_y}" font-size="12" font-family="Roboto, sans-serif" fill="white" text-anchor="middle">{tick_value:.1f}</text>'
    else:
        tick_marks = ""
        tick_labels = ""
        for i in range(0, 11, 2):
            tick_angle = (i / 10) * 180 - 90
            rad_tick = tick_angle * (3.14159 / 180)
            inner_x = 120 + 85 * math.sin(rad_tick)
            inner_y = 140 - 85 * math.cos(rad_tick)
            outer_x = 120 + 95 * math.sin(rad_tick)
            outer_y = 140 - 95 * math.cos(rad_tick)
            label_x = 120 + 100 * math.sin(rad_tick)
            label_y = 140 - 100 * math.cos(rad_tick)
            if i == 0:
                label_y += 8
            elif i == 10:
                label_y -= 8
            elif i in [4, 6]:
                label_y += 4
            elif i in [2, 8]:
                label_y -= 4
            tick_marks += f'<line x1="{inner_x}" y1="{inner_y}" x2="{outer_x}" y2="{outer_y}" stroke="black" stroke-width="2"/>'
            tick_labels += f'<text x="{label_x}" y="{label_y}" font-size="12" font-family="Roboto, sans-serif" fill="white" text-anchor="middle">{i}</text>'

    needle_tip_x = 120 + 80 * math.sin(rad)
    needle_tip_y = 140 - 80 * math.cos(rad)
    base_width = 10
    base_angle = (angle + 90) * (3.14159 / 180)
    base_x1 = 120 + base_width * math.cos(base_angle)
    base_y1 = 140 + base_width * math.sin(base_angle)
    base_x2 = 120 - base_width * math.cos(base_angle)
    base_y2 = 140 - base_width * math.sin(base_angle)
    needle_path = f"M {needle_tip_x},{needle_tip_y} L {base_x1},{base_y1} L {base_x2},{base_y2} Z"

    svg = f"""
    <div class="speedometer-wrapper">
        <svg class="speedometer-svg" viewBox="0 0 240 200">
            <path d="M40,140 A80,80 0 0,1 200,140" fill="none" stroke="url(#grad)" stroke-width="20"/>
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:green"/>
                    <stop offset="50%" style="stop-color:yellow"/>
                    <stop offset="100%" style="stop-color:red"/>
                </linearGradient>
            </defs>
            {tick_marks}
            {tick_labels}
            <path d="{needle_path}" fill="white" stroke="white" stroke-width="3"/>
            <circle cx="120" cy="140" r="5" fill="black"/>
        </svg>
    </div>
    """
    score_text = f"{score:.1f}x" if is_rr else f"{score:.1f}"  # Decimal for all, 'x' for RR
    return svg, score_text


# Custom CSS for styling
st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 3px;
    font-family: Roboto, sans-serif;
    color: white;
}
.subtitle {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 20px;
    text-align: center;
    margin-bottom: 6px;
}
.speedometer-wrapper {
    display: flex;
    justify-content: center;
    margin: 3px 0;
}
.speedometer-svg {
    width: 240px;
    height: 200px;
}
.report-container {
    margin: 3px 0;
}
.chart-container {
    margin-bottom: 3px;
    display: flex;
    flex-direction: row;
    align-items: center;
    vertical-align: middle;
}
.chart-label {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 14px;
    text-align: center;
    margin-top: 3px;
}
.bp-reading {
    font-family: Roboto, sans-serif;
    font-size: 14px;
    border: 2px solid;
    padding: 14px;
    margin-right: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 80px;
    max-width: 120px;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
.bp-reading-with-eag {
    margin-top: 40px;
}
.bp-reading-without-eag {
    margin-top: 20px;
}
.gauge-score {
    font-family: Roboto, sans-serif;
    font-size: 20px;
    padding: 5px;
    margin-left: 10px;
    display: inline-block;
    vertical-align: middle;
}
.section-title {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 20px;
    text-decoration: underline;
    margin-bottom: 3px;
}
.section-title-after-visit {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 22px;
    text-decoration: underline;
    margin-bottom: 3px;
}
.section-divider {
    width: 50%;
    margin: 3px auto;
    border: 1px solid white;
}
.gauge-row-divider {
    width: 50%;
    margin: 3px auto;
    border: 1px solid white;
}
.gauge-label {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 3px;
}
.gauge-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 10px;
}
.gauge-divider {
    width: 1px;
    height: 600px;
    background-color: white;
    margin: 0 10px;
    margin-top: 0px;
}
.sleep-apnea-recommendation {
    font-family: Roboto, sans-serif;
    color: #FFFF00;
}
.smoking-cessation-recommendation {
    font-family: Roboto, sans-serif;
    color: #00FF00;
    font-weight: bold;
}
.input-container {
    padding: 2px;
    margin: 0;
}
.input-container .stTextInput > div > div > input,
.input-container .stTextArea > div > div > textarea,
.input-container .stSelectbox > div > div > select,
.input-container .stNumberInput > div > div > input {
    font-family: Roboto, sans-serif;
    font-size: 11px;
}
.input-container .stTextArea > div > div > textarea {
    max-height: 80px;
}
.stApp {
    margin: 0;
    padding: 5px;
}
.st-emotion-cache-1wmy9hl:nth-child(1) {
    left: 0 !important;
    width: 450px !important;
    min-width: 400px !important;
}
.st-emotion-cache-1wmy9hl:nth-child(2) {
    margin: 0 auto !important;
    width: 450px !important;
    min-width: 400px !important;
}
.st-emotion-cache-1wmy9hl:nth-child(3) {
    right: 0 !important;
    width: 450px !important;
    min-width: 400px !important;
}
.st-emotion-cache-1wmy9hl h2 {
    font-family: Roboto, sans-serif;
    color: white;
    font-size: 20px;
    white-space: nowrap;
}
.error-message {
    font-family: Roboto, sans-serif;
    color: #FF0000;
    font-size: 14px;
    text-align: center;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# JavaScript to adjust column positions
st.markdown("""
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const columns = document.querySelectorAll('.st-emotion-cache-1wmy9hl');
        if (columns.length >= 3) {
            columns[0].style.left = '0';
            columns[0].style.position = 'relative';
            columns[1].style.margin = '0 auto';
            columns[2].style.right = '0';
            columns[2].style.position = 'relative';
        }
    });
</script>
""", unsafe_allow_html=True)


# Function to determine blood pressure category
def get_blood_pressure_category(systolic, diastolic):
    systolic = float(systolic) if systolic is not None else 120
    diastolic = float(diastolic) if diastolic is not None else 80
    if systolic <= 0 or diastolic <= 0:
        return "Unknown", "Invalid blood pressure values. Please enter valid numbers.", "#808080", 120, 80
    if systolic > 180 or diastolic > 120:
        return "Hypertensive Crisis", "Seek immediate medical help (can lead to stroke/heart attack).", "#8B0000", systolic, diastolic
    elif systolic >= 140 or diastolic >= 90:
        return "Hypertension Stage 2", "High risk; requires medication + lifestyle changes.", "#FF0000", systolic, diastolic
    elif systolic >= 130 or diastolic >= 80:
        return "Hypertension Stage 1", "Early high blood pressure. Lifestyle changes + possible medication.", "#FFA500", systolic, diastolic
    elif systolic >= 120 and diastolic < 80:
        return "Elevated", "Risk of developing hypertension. Lifestyle changes recommended.", "#FFFF00", systolic, diastolic
    elif systolic < 120 and diastolic < 80:
        return "Normal", "Healthy range. Maintain lifestyle habits (diet, exercise).", "#00FF00", systolic, diastolic
    return "Unknown", "Please consult a healthcare provider.", "#808080", 120, 80


# Function to determine glucose category
def get_glucose_category(latest_glucose_mgdl):
    glucose = float(latest_glucose_mgdl) if latest_glucose_mgdl is not None else 100.0
    if glucose < 0:
        return "Invalid", "Invalid glucose value. Please enter a valid number.", "#808080"
    if glucose < 70:
        return "Hypoglycemia", "Hypoglycemia (too low; may cause shakiness, confusion)", "#FF0000"
    elif 70 <= glucose <= 79:
        return "Low", "Low; possible hypoglycemia symptoms, especially if symptomatic", "#00FF00"
    elif 80 <= glucose <= 89:
        return "Below Target", "Below usual target for diabetes; rare post-meal, monitor", "#00FF00"
    elif 90 <= glucose <= 99:
        return "Lower Edge", "At lower edge of diabetes target; safe, but rare after meals", "#00FF00"
    elif 100 <= glucose <= 109:
        return "Lower Non-Fasting", "Lower-than-typical non-fasting for diabetes; rarely post-meal", "#ADFF2F"
    elif 110 <= glucose <= 119:
        return "Slightly Low", "Slightly low post-meal for diabetes; usually safe", "#ADFF2F"
    elif 120 <= glucose <= 129:
        return "Below Post-Meal", "Below target post-meal, but not dangerous", "#FFFF00"
    elif 130 <= glucose <= 139:
        return "Near Bottom", "Slightly below/near bottom of post-meal goal", "#FFFF00"
    elif 140 <= glucose <= 149:
        return "Acceptable", "Acceptable (1–2hr post-meal); excellent diabetes control", "#FFFF00"
    elif 150 <= glucose <= 159:
        return "Well-Controlled", "Well-controlled (within post-meal target)", "#FFCC00"
    elif 160 <= glucose <= 169:
        return "Well-Controlled", "Well-controlled (within post-meal target)", "#FFCC00"
    elif 170 <= glucose <= 179:
        return "Upper End", "At the upper end of post-meal (peak) target", "#FFA500"
    elif 180 <= glucose <= 189:
        return "Target Maximum", "At target maximum; intervention may be considered if frequent", "#FFA500"
    elif 190 <= glucose <= 199:
        return "Mildly Above", "Mildly above optimal; could indicate need for therapy review", "#FFA500"
    elif 200 <= glucose <= 209:
        return "Above Ideal", "Higher than ideal; diabetes not optimally controlled", "#FF4500"
    elif 210 <= glucose <= 219:
        return "Too High", "Too high; increased risk of complications if sustained", "#FF4500"
    elif 220 <= glucose <= 229:
        return "Too High", "Too high; requires prompt evaluation for medication/insulin", "#FF0000"
    elif 230 <= glucose <= 239:
        return "Much Too High", "Much too high; risk of acute hyperglycemic symptoms", "#FF0000"
    else:
        return "Dangerously High", "Dangerously high; urgent attention required", "#FF0000"


# Function to calculate gum disease score, risk, and verbiage
def calculate_gum_disease_score(stage, grade, smoking, latest_glucose_mgdl):
    stage_grade_ranges = {
        ("Stage I", "Grade A"): (1.0, 1.8, 1.45,
                                 "Your gums show minimal signs of inflammation and almost no bone loss. With good home care and regular cleanings, your risk of progression is very low."),
        ("Stage I", "Grade B"): (1.9, 2.7, 2.3,
                                 "You have mild gum inflammation and slight bone loss. Without improved brushing/flossing and professional cleanings, there’s a low–moderate chance of worsening."),
        ("Stage I", "Grade C"): (2.8, 3.5, 3.15,
                                 "Early periodontitis is present, with measurable bone loss. You’re at moderate risk of disease progression unless you step up daily gum care and see your dentist for deeper cleanings."),
        ("Stage II", "Grade A"): (3.6, 4.4, 4.0,
                                  "Moderate periodontitis—some pockets and bone loss—are evident. Your gums may worsen gradually if daily plaque control and routine maintenance are not improved."),
        ("Stage II", "Grade B"): (4.5, 5.2, 4.85,
                                  "You have moderate gum and bone damage. Without targeted periodontal therapy and strict hygiene, your risk of further bone loss and pocket deepening is substantial."),
        ("Stage II", "Grade C"): (5.3, 6.0, 5.65,
                                  "Active moderate disease with signs of progression. There’s a significant likelihood of worsening bone and tissue damage without intensive treatment and rigorous self-care."),
        ("Stage III", "Grade A"): (6.1, 6.9, 6.5,
                                   "Advanced periodontitis: deep pockets, recession, and some tooth mobility. Your gums are at high risk of further deterioration without periodontal intervention."),
        ("Stage III", "Grade B"): (7.0, 7.7, 7.35,
                                   "You have advanced disease with clear evidence of progression. Prompt periodontal therapy and very vigilant home care are critical to prevent tooth loss."),
        ("Stage III", "Grade C"): (7.8, 8.5, 8.15,
                                   "Rapidly progressing advanced periodontitis. There’s a very high risk of continuing bone loss and potential tooth loss unless you receive specialized periodontal treatment immediately."),
        ("Stage IV", "Grade A"): (8.6, 9.3, 8.95,
                                  "Severe periodontitis with significant bone loss and multiple loose teeth. Without comprehensive surgical/perio therapy, you face a very high likelihood of further tooth loss."),
        ("Stage IV", "Grade B"): (9.4, 9.2, 9.3,
                                  "Complex, severe disease that is actively worsening. Intensive surgical care and lifelong maintenance are essential to stabilize your condition and preserve remaining teeth."),
        ("Stage IV", "Grade C"): (9.3, 10.0, 9.65,
                                  "Extreme periodontal destruction with high progression risk. Urgent, multidisciplinary care is needed—otherwise continued bone loss and tooth loss are almost certain.")
    }
    base_score, max_score, avg_score, verbiage = stage_grade_ranges.get((stage, grade), (4.5, 5.2, 4.85,
                                                                                         "You have moderate gum and bone damage. Without targeted periodontal therapy and strict hygiene, your risk of further bone loss and pocket deepening is substantial."))
    smoking_adj = 0 if smoking == "Non-smoker" else 0.2 if smoking == "<10 cigarettes/day" else 0.5
    diabetes_adj = 0 if latest_glucose_mgdl is None else (0.2 if latest_glucose_mgdl < 150 else 0.5)
    gum_disease_score = min(10.0, avg_score + smoking_adj + diabetes_adj)
    gum_disease_risk = min(10.0, gum_disease_score + 1.0)
    return gum_disease_score, gum_disease_risk, verbiage


# Function to display diabetes scores
def display_diabetes_scores(diabetes, latest_glucose_mgdl, stage, grade, col):
    timestamp = str(time.time())
    if diabetes == "Yes" and latest_glucose_mgdl is not None:
        # Dynamic score based on glucose level and periodontal severity
        glucose_impact = min(10.0, (latest_glucose_mgdl - 70) / 17)  # Scales 70-240 mg/dL to 0-10, but min 1
        stage_weight = {"Stage I": 0.2, "Stage II": 0.5, "Stage III": 0.8, "Stage IV": 1.0}.get(stage, 0.5)
        grade_weight = {"Grade A": 0.2, "Grade B": 0.5, "Grade C": 1.0}.get(grade, 0.5)
        diabetes_impact = min(10.0, glucose_impact * (stage_weight + grade_weight) / 2)
        label = "Diabetes Management Score"
        min_value = 0
        max_value = 10
        is_rr = False
        verbiage = f"""
{'Severe periodontal disease may worsen glycemic control.' if diabetes_impact >= 5 else 'No significant diabetes-related concerns.'}<br>
The interaction between diabetes and periodontal disease is bidirectional. Managing both is key—healthy gums can help control blood sugar, and better diabetes control supports gum health. This relationship underscores the critical need for managing both conditions simultaneously to mitigate their impact.<br>
<strong>Potential improvement after periodontal treatment:</strong> Treating periodontal disease may improve diabetes management, potentially reducing your risk score.
"""
    else:
        rr, summary, rec = diabetes_rr_map.get((stage, grade),
                                               (1.7, "Ongoing periodontal damage; higher glucose dysregulation risk",
                                                "Treating gum disease may reduce your risk of developing diabetes"))
        diabetes_impact = rr
        label = "Diabetes Risk Score"
        min_value = 1.0
        max_value = 3.2
        is_rr = True
        verbiage = f"""
{summary}<br>
The interaction between periodontal disease and diabetes risk is significant. Even without a current diabetes diagnosis, poor gum health can increase your risk of developing diabetes.<br>
<strong>Potential improvement after periodontal treatment:</strong> {rec}
"""
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(diabetes_impact, label, min_value=min_value,
                                                           max_value=max_value, is_rr=is_rr,
                                                           key=f"diabetes_unique_{timestamp}")
        score_color = get_gauge_color(diabetes_impact, min_value=1.0 if is_rr else 0,
                                      max_value=max_value if is_rr else 10, is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
{verbiage}
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display cardiovascular scores
def display_cardio_scores(cardio, systolic_bp, stage, grade, col):
    if cardio == "Yes":
        bp_impact = min(10.0, (systolic_bp - 90) / 9) if systolic_bp else 5.0  # Scales 90-180 mmHg to 0-10, but min 1
        stage_weight = {"Stage I": 0.2, "Stage II": 0.5, "Stage III": 0.8, "Stage IV": 1.0}.get(stage, 0.5)
        grade_weight = {"Grade A": 0.2, "Grade B": 0.5, "Grade C": 1.0}.get(grade, 0.5)
        cv_impact = min(10.0, (bp_impact + (stage_weight + grade_weight) * 2.5) / 2)
        label = "Cardiovascular Disease Impact Score"
        min_value = 0
        max_value = 10
        is_rr = False
        verbiage = f"""
Studies have shown that treating gum disease can lead to improvements in markers of cardiovascular health, such as reduced arterial inflammation and lower systemic inflammatory markers, supporting the link between these conditions.<br>
<strong>Potential improvement after periodontal treatment:</strong> Periodontal treatment can reduce inflammation, potentially lowering your risk of heart disease or stroke.
"""
    else:
        rr, summary, rec = cardio_rr_map.get((stage, grade),
                                             (1.6, "Systemic inflammatory markers rising; moderate vascular risk",
                                              "Treating gum disease may reduce your risk of developing Cardiovascular Disease"))
        cv_impact = rr
        label = "Cardiovascular Disease Risk Score"
        min_value = 1.0
        max_value = 3.2
        is_rr = True
        verbiage = f"""
{summary}<br>
Periodontal disease can increase cardiovascular risk through systemic inflammation, even without a current diagnosis.<br>
<strong>Potential improvement after periodontal treatment:</strong> {rec}
"""
    timestamp = str(time.time())
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(cv_impact, label, min_value=min_value, max_value=max_value,
                                                           is_rr=is_rr, key=f"cardio_unique_{timestamp}")
        score_color = get_gauge_color(cv_impact, min_value=1.0 if is_rr else 0, max_value=max_value if is_rr else 10,
                                      is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
{verbiage}
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display kidney scores
def display_kidney_scores(kidney, stage, grade, col):
    if kidney == "Yes":
        stage_weight = {"Stage I": 0.2, "Stage II": 0.5, "Stage III": 0.8, "Stage IV": 1.0}.get(stage, 0.5)
        grade_weight = {"Grade A": 0.2, "Grade B": 0.5, "Grade C": 1.0}.get(grade, 0.5)
        kidney_impact = min(10.0, (stage_weight + grade_weight) * 2.5)  # Scales 0.4-2.0 to 0-5, but adjusted to 1-10
        label = "Chronic Kidney Disease Management Score"
        min_value = 0
        max_value = 10
        is_rr = False
        verbiage = f"""
Studies have shown that gum disease is associated with increased complications in chronic kidney disease (CKD). Treating gum disease may improve kidney function, potentially reducing your score.<br>
<strong>Potential improvement after periodontal treatment:</strong> Treating periodontal disease may improve kidney function, potentially reducing your risk score.
"""
    else:
        rr, summary, rec = kidney_rr_map.get((stage, grade), (1.7,
                                                              "Moderate risk of renal function decline, particularly in patients with diabetes or hypertension",
                                                              "Treating gum disease may reduce your risk of developing Kidney Disease"))
        kidney_impact = rr
        label = "Kidney Disease Risk Score"
        min_value = 1.0
        max_value = 3.4
        is_rr = True
        verbiage = f"""
{summary}<br>
Periodontal disease can increase kidney disease risk through systemic inflammation, even without a current diagnosis.<br>
<strong>Potential improvement after periodontal treatment:</strong> {rec}
"""
    timestamp = str(time.time())
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(kidney_impact, label, min_value=min_value,
                                                           max_value=max_value, is_rr=is_rr,
                                                           key=f"kidney_unique_{timestamp}")
        score_color = get_gauge_color(kidney_impact, min_value=1.0 if is_rr else 0,
                                      max_value=max_value if is_rr else 10, is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center; justify-content: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
{verbiage}
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display dementia scores (always "No")
def display_dementia_scores(stage, grade, col):
    rr, summary, rec = dementia_rr_map.get((stage, grade), (1.6,
                                                            "Oral pathogens like P. gingivalis and inflammation linked to amyloid accumulation",
                                                            "Treating gum disease may reduce your risk of developing dementia"))
    dementia_impact = rr
    label = "Dementia Risk Score"
    min_value = 1.0
    max_value = 3.4
    is_rr = True
    verbiage = f"""
{summary}<br>
<strong>Potential improvement after periodontal treatment:</strong> {rec}
"""
    timestamp = str(time.time())
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(dementia_impact, label, min_value=min_value,
                                                           max_value=max_value, is_rr=is_rr,
                                                           key=f"dementia_unique_{timestamp}")
        score_color = get_gauge_color(dementia_impact, min_value=1.0 if is_rr else 0,
                                      max_value=max_value if is_rr else 10, is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center; justify-content: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
{verbiage}
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display preterm scores
def display_preterm_scores(stage, grade, preterm_risk, col):
    label = "Pre-Term Birth Risk Score"
    min_value = 0
    max_value = 10
    is_rr = False
    timestamp = str(time.time())
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(preterm_risk, label, min_value=min_value,
                                                           max_value=max_value, is_rr=is_rr,
                                                           key=f"preterm_unique_{timestamp}")
        score_color = get_gauge_color(preterm_risk, min_value=1.0 if is_rr else 0, max_value=max_value if is_rr else 10,
                                      is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        summary, rec = preterm_map.get((stage, grade), ("Default summary", "Default recommendations"))
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
Research published in the American Journal of Obstetrics and Gynecology shows that getting your gums treated during pregnancy might actually lower the risk of preterm birth—just one more reason to take dental health seriously when you’re expecting.<br>
{summary}<br>
<strong>Treatment Recommendations:</strong> {rec}<br>
<strong>Potential improvement after periodontal treatment:</strong> Periodontal treatment may reduce the risk of preterm birth by approximately 22%.
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display sleep apnea scores
def display_sleep_apnea_scores(col):
    sleep_impact = 8.0
    label = "Potential Risk for Sleep Apnea"
    min_value = 0
    max_value = 10
    is_rr = False
    timestamp = str(time.time())
    with col:
        st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
        st.markdown(f'<div class="gauge-label"><strong>{label}</strong></div>', unsafe_allow_html=True)
        speedometer_svg, score_text = generate_speedometer(sleep_impact, label, min_value=min_value,
                                                           max_value=max_value, is_rr=is_rr,
                                                           key=f"sleep_unique_{timestamp}")
        score_color = get_gauge_color(sleep_impact, min_value=1.0 if is_rr else 0, max_value=max_value if is_rr else 10,
                                      is_rr=is_rr)
        if speedometer_svg:
            st.markdown(
                f'<div style="display: flex; align-items: center; justify-content: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                unsafe_allow_html=True)
        st.markdown(
            '<div class="sleep-apnea-recommendation">Consider a sleep test for obstructive sleep apnea due to reported snoring.</div>',
            unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
Sleep apnea is associated with an increased risk of cardiovascular disease, chronic fatigue, insulin resistance, and depression. Based on our clinical observations and your reported symptoms, there is a significant possibility that you may be affected by this condition. We strongly recommend undergoing a sleep study to confirm a diagnosis and ensure timely, effective treatment.
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Function to display gauges in rows of 2 with divider
def display_in_rows(gauges_list):
    for i in range(0, len(gauges_list), 2):
        if i + 1 < len(gauges_list):
            col1, div, col2 = st.columns([2, 0.1, 2])
            gauges_list[i](col1)
            with div:
                st.markdown('<div class="gauge-divider"></div>', unsafe_allow_html=True)
            gauges_list[i + 1](col2)
        else:
            col, = st.columns(1)
            gauges_list[i](col)
        if i + 2 < len(gauges_list):
            st.markdown('<hr class="gauge-row-divider">', unsafe_allow_html=True)


# Streamlit app
st.markdown('<div class="title">Nesso Health Overall Health Assessment</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Based on AAP 2017 Guidelines and Patient Health Data</div>', unsafe_allow_html=True)

# Input Form (Streamlit Columns)
with st.container():
    col_patient, col_health, col_periodontitis = st.columns([1, 1, 1])

    # Patient Information (default values)
    with col_patient:
        st.header("Patient Information")
        patient_name = st.text_input("Patient Name", "Joe Smith", key="patient_name")
        exam_date = st.date_input("Exam Date", datetime.date.today(), key="exam_date")
        prepared_by = st.text_input("Prepared By", "Ebon Turner", key="prepared_by")
        practice_name = st.text_input("Practice Name", "Smile Family Dental", key="practice_name")
        practice_phone = st.text_input("Practice Phone", "(555) 123-4567", key="practice_phone")
        practice_address = st.text_area("Practice Address", "123 Dental St\nCity, State ZIP", key="practice_address")
        age = st.number_input("Age", min_value=0, max_value=120, value=None, key="age")

    # Health Information
    with col_health:
        st.header("Health Information")
        diabetes = st.selectbox("Diabetes? *", ["", "Yes", "No"], key="diabetes")
        latest_glucose_mgdl = st.number_input("Latest Glucose (mg/dL)", min_value=0.0, value=None,
                                              key="latest_glucose_mgdl") if diabetes == "Yes" else None
        if diabetes == "Yes":
            st.markdown("Note: If you have mmol/L, convert by multiplying by 18.")
        cardiovascular_disease = st.selectbox("Cardiovascular Disease?", ["", "Yes", "No"],
                                              key="cardiovascular_disease")
        systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=0, value=None, key="systolic_bp")
        diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=0, value=None, key="diastolic_bp")
        kidney_disease = st.selectbox("Kidney Disease?", ["", "Yes", "No"], key="kidney_disease")
        pregnancy = st.selectbox("Pregnancy?", ["", "Yes", "No"], key="pregnancy")
        trimester = st.selectbox("Trimester", ["", "1st", "2nd", "3rd"], key="trimester") if pregnancy == "Yes" else ""
        snoring = st.selectbox("Snoring?", ["", "Yes", "No"], key="snoring")
        sleep_apnea = st.selectbox("Sleep Apnea?", ["", "Yes", "No"], key="sleep_apnea") if snoring == "Yes" else ""
        smoking = st.selectbox("Smoking?", ["", "Non-smoker", "<10 cigarettes/day", ">=10 cigarettes/day"],
                               key="smoking")

    # Periodontitis Staging/Grading
    with col_periodontitis:
        st.header("Periodontitis Staging/Grading")
        stage = st.selectbox("Stage *", ["", "Stage I", "Stage II", "Stage III", "Stage IV"], key="stage")
        grade = st.selectbox("Grade *", ["", "Grade A", "Grade B", "Grade C"], key="grade")

    # Validate required fields
    error_message = ""
    required_fields = {
        "Diabetes": diabetes,
        "Stage": stage,
        "Grade": grade
    }
    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        error_message = f"Please fill out the following required fields: {', '.join(missing_fields)}."
    if error_message:
        st.markdown(f'<div class="error-message">{error_message}</div>', unsafe_allow_html=True)
    else:
        # Effective values for conditions (treat blank as "No")
        effective_diabetes = diabetes if diabetes else "No"
        effective_cardio_disease = cardiovascular_disease if cardiovascular_disease else "No"
        effective_kidney_disease = kidney_disease if kidney_disease else "No"
        effective_pregnancy = pregnancy if pregnancy else "No"
        effective_snoring = snoring if snoring else "No"
        effective_sleep_apnea = sleep_apnea if sleep_apnea else "No"

        # Handle latest_glucose_mgdl_final
        latest_glucose_mgdl_final = latest_glucose_mgdl

        # Blood Pressure and Glucose
        bp_category, bp_recommendation, bp_color, systolic_bp_final, diastolic_bp_final = get_blood_pressure_category(
            systolic_bp, diastolic_bp)
        glucose_category, glucose_description, glucose_color = get_glucose_category(
            latest_glucose_mgdl_final) if effective_diabetes == "Yes" else ("N/A", "Not applicable (no diabetes)",
                                                                            "#808080")

        # Gum Disease Score
        gum_disease_score, gum_disease_risk, gum_verbiage = calculate_gum_disease_score(stage, grade, smoking,
                                                                                        latest_glucose_mgdl_final)

        # Pre-Term Birth Risk
        if effective_pregnancy == "Yes":
            preterm_risk = gum_disease_score
        else:
            preterm_risk = None

        # Generate Report
        st.markdown('<div class="section-title">Oral Health Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            formatted_address = practice_address.replace('\n', '<br>').replace(',', '')
            address_lines = formatted_address.split('<br>')
            if len(address_lines) >= 2:
                city_state_zip = address_lines[1].strip().split()
                if len(city_state_zip) >= 3:
                    city = ' '.join(city_state_zip[:-2])
                    state = city_state_zip[-2]
                    zip_code = city_state_zip[-1]
                else:
                    city, state, zip_code = "", "", ""
            else:
                city, state, zip_code = "", "", ""
            st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
{practice_name}<br>
{practice_phone}<br>
{address_lines[0] if address_lines else ''}<br>
{city}<br>
{state}<br>
{zip_code}<br>
</div>
""", unsafe_allow_html=True)
        with col_info2:
            st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
<strong>Exam Information</strong><br>
Prepared For: {patient_name}<br>
Prepared By: {prepared_by}<br>
Exam Date: {exam_date}<br>
Submitted To: {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}
</div>
""", unsafe_allow_html=True)

        # Blood Pressure and Glucose Charts
        if effective_diabetes == "Yes":
            col1, col2 = st.columns(2)
            bp_class = "bp-reading bp-reading-with-eag"
        else:
            col1, = st.columns(1)
            bp_class = "bp-reading bp-reading-without-eag"
        with col1:
            bp_fig = px.bar(x=[bp_category], y=[systolic_bp_final], title="Blood Pressure Category",
                            labels={"x": "", "y": "Systolic (mm Hg)"}, color=[bp_category],
                            color_discrete_map={bp_category: bp_color})
            bp_fig.update_layout(
                title_font=dict(family="Roboto, sans-serif", size=18, color="white"),
                font=dict(family="Roboto, sans-serif", color="white"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=240,
                margin=dict(l=40, r=40, t=40, b=40),
                yaxis=dict(dtick=20),
                showlegend=False,
                bargap=0.6
            )
            col_bp1, col_bp2 = st.columns([1, 3])
            with col_bp1:
                st.markdown(
                    f'<div class="{bp_class}" style="color: {bp_color}; border-color: {bp_color};">{systolic_bp_final}/{diastolic_bp_final}</div>',
                    unsafe_allow_html=True)
            with col_bp2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(bp_fig, use_container_width=True)
                st.markdown(f'<div class="chart-label">{bp_category}<br>Risk: {bp_recommendation}</div>',
                            unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if effective_diabetes == "Yes":
            with col2:
                glucose_fig = px.bar(x=[glucose_category], y=[latest_glucose_mgdl_final], title="Glucose Category",
                                     labels={"x": "", "y": "Latest Glucose (mg/dL)"}, color=[glucose_category],
                                     color_discrete_map={glucose_category: glucose_color})
                glucose_fig.update_layout(
                    title_font=dict(family="Roboto, sans-serif", size=18, color="white"),
                    font=dict(family="Roboto, sans-serif", color="white"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=240,
                    margin=dict(l=40, r=40, t=40, b=40),
                    yaxis=dict(dtick=50),
                    showlegend=False,
                    bargap=0.6
                )
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(glucose_fig, use_container_width=True)
                st.markdown(f"""
<div class="chart-label">{glucose_category}<br>{glucose_description}<br>
Note:<br>
• Targets may be adjusted for age, comorbidities, pregnancy, or individual circumstances.<br>
• Glucose scores can be affected by a variety of items, meals, medication, exercise, etc. Always consult your healthcare provider for guidance tailored to your needs.
</div>
""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Gum Disease Assessment
        st.markdown('<div class="section-title">Gum Disease Assessment</div>', unsafe_allow_html=True)
        col_gum1, col_gum2 = st.columns(2)  # Corrected order: Health Index on left, Risk Index on right
        with col_gum1:
            st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
            st.markdown(f'<div class="gauge-label"><strong>Gingiva Health Index</strong></div>', unsafe_allow_html=True)
            speedometer_svg, score_text = generate_speedometer(gum_disease_score, "Gingiva Health Index", min_value=0,
                                                               max_value=10, is_rr=False,
                                                               key=f"gingiva_health_unique_{time.time()}")
            score_color = get_gauge_color(gum_disease_score, min_value=0, max_value=10)
            if speedometer_svg:
                st.markdown(
                    f'<div style="display: flex; align-items: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                    unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_gum2:
            st.markdown('<div class="gauge-column">', unsafe_allow_html=True)
            st.markdown(f'<div class="gauge-label"><strong>Gingiva Health Risk Index</strong></div>',
                        unsafe_allow_html=True)
            speedometer_svg, score_text = generate_speedometer(gum_disease_risk, "Gingiva Health Risk Index",
                                                               min_value=0, max_value=10, is_rr=False,
                                                               key=f"gingiva_risk_unique_{time.time()}")
            score_color = get_gauge_color(gum_disease_risk, min_value=0, max_value=10)
            if speedometer_svg:
                st.markdown(
                    f'<div style="display: flex; align-items: center;">{speedometer_svg}<div class="gauge-score" style="color: {score_color}; border: 2px solid {score_color};">{score_text}</div></div>',
                    unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-family: Roboto, sans-serif; color: white;">
<strong>Periodontitis Stage: {stage}</strong><br>
<strong>Periodontitis Grade: {grade}</strong><br>
<strong>What This Means for You:</strong> {gum_verbiage}
</div>
""", unsafe_allow_html=True)

        # Section Divider
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Impact of Gum Health on Overall Health
        st.markdown('<div class="section-title">Impact of Gum Health on Overall Health</div>', unsafe_allow_html=True)
        st.markdown("""
<div style="font-family: Roboto, sans-serif; color: white;">
Your gum health is closely tied to your overall health. Research links gum disease to serious conditions like dementia, diabetes, heart and kidney disease, and autoimmune disorders. If you’re managing a chronic illness or at risk, the following provides insight on the impact of gum disease and the opportunity to manage it with better oral care.
</div>
""", unsafe_allow_html=True)

        # Collect YES gauges
        yes_gauges = []
        if effective_diabetes == "Yes":
            yes_gauges.append(
                lambda col: display_diabetes_scores(effective_diabetes, latest_glucose_mgdl_final, stage, grade, col))
        if effective_cardio_disease == "Yes":
            yes_gauges.append(
                lambda col: display_cardio_scores(effective_cardio_disease, systolic_bp_final, stage, grade, col))
        if effective_kidney_disease == "Yes":
            yes_gauges.append(lambda col: display_kidney_scores(effective_kidney_disease, stage, grade, col))
        if effective_pregnancy == "Yes":
            yes_gauges.append(lambda col: display_preterm_scores(stage, grade, preterm_risk, col))

        # Collect NO gauges (excluding Dementia)
        no_gauges = []
        if effective_diabetes == "No":
            no_gauges.append(
                lambda col: display_diabetes_scores(effective_diabetes, latest_glucose_mgdl_final, stage, grade, col))
        if effective_cardio_disease == "No":
            no_gauges.append(
                lambda col: display_cardio_scores(effective_cardio_disease, systolic_bp_final, stage, grade, col))
        if effective_kidney_disease == "No":
            no_gauges.append(lambda col: display_kidney_scores(effective_kidney_disease, stage, grade, col))

        # Display main gauges (YES then NO)
        all_main_gauges = yes_gauges + no_gauges
        if all_main_gauges:
            display_in_rows(all_main_gauges)

        # Bottom row: Dementia and optional Sleep Apnea
        bottom_gauges = [lambda col: display_dementia_scores(stage, grade, col)]
        if effective_snoring == "Yes" and effective_sleep_apnea == "No":
            bottom_gauges.append(lambda col: display_sleep_apnea_scores(col))
        if bottom_gauges:
            if all_main_gauges:
                st.markdown('<hr class="gauge-row-divider">', unsafe_allow_html=True)
            if len(bottom_gauges) == 2:
                col_dem, col_div2, col_sleep = st.columns([2, 0.1, 2])
                bottom_gauges[0](col_dem)
                with col_div2:
                    st.markdown('<div class="gauge-divider"></div>', unsafe_allow_html=True)
                bottom_gauges[1](col_sleep)
            else:
                col_dem, = st.columns(1)
                bottom_gauges[0](col_dem)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # After Visit Summary
        oral_care_recommendations = """
1) Brush and floss daily.<br>
2) Based on your Gingiva Health Index, consult with your dentists regarding gum disease treatment options, including more frequent visits.<br>
3) Inform your dentist about persistent oral issues.
"""
        if snoring == "No" and sleep_apnea == "":
            oral_care_recommendations += '<br>4. <strong style="font-family: Roboto, sans-serif; color: #FFFF00;">Consider a sleep test for obstructive sleep apnea due to reported snoring.</strong>'
        elif snoring == "Yes" and sleep_apnea == "No":
            oral_care_recommendations += '<br><div class="sleep-apnea-recommendation">Consider a sleep test for obstructive sleep apnea due to reported snoring.</div>'
        if smoking not in ["Non-smoker", None]:
            oral_care_recommendations += '<br><div class="smoking-cessation-recommendation">A variety of smoking cessation programs are available to help with your smoking.</div>'

        st.markdown(f"""
<div class="section-title-after-visit">AFTER VISIT SUMMARY</div>
<div style="font-family: Roboto, sans-serif; color: white;">
<strong>Recommendations:</strong><br>
<strong>Oral Care:</strong><br>
{oral_care_recommendations}<br>
<strong>Medical Follow-up:</strong><br>
With your permission, we will share this report with your doctor so we can all work together to support your overall and oral health. Teaming up makes it easier to catch any issues early and keep you feeling your best. Please consult with your physician(s) regarding management of any healthcare conditions and concerns.<br><br>
<strong>Only Health/Disease Score Disclaimer:</strong><br>
The Disease Scores provided are based on a review of numerous clinical articles to achieve a general gauge of the impact of oral health on overall health and chronic conditions. These scores are intended for informational purposes only and are not a substitute for professional medical advice, diagnosis, or treatment.<br><br>
Please be aware that:<br>
1. <strong>Not a Definitive Diagnosis:</strong> The Scores are not intended to diagnose, treat, cure, or prevent any disease or health condition. They should not be used as a definitive diagnosis or status of any chronic disease.<br>
2. <strong>Consult Healthcare Providers:</strong> Always seek the advice of your physician or other qualified healthcare providers with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay seeking it because of the Total Health Scores.<br>
3. <strong>Individual Variability:</strong> Health outcomes can vary greatly among individuals. The information provided through these scores is based on population-level data and may not reflect individual-specific factors.<br>
4. <strong>No Liability:</strong> By using the Total Health Scores, you acknowledge and agree that the creators, distributors, and related entities of the Total Health Scores are not liable for any health issues or decisions that arise from the use of this information.<br>
5. <strong>Periodic Updates:</strong> Medical knowledge and recommendations change over time. The Total Health Scores are periodically updated based on the latest research, but there may be new findings not yet included in the scores.
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
