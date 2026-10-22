import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st._config.set_option("theme.base", "dark")
st._config.set_option("theme.primaryColor", "#1F6FD1")
st.set_page_config(
    page_title="Dashboard PERFORMA SISWA",
    page_icon="📊",
    layout="wide"
)

LABEL = {
    "gender": "Gender",
    "parental_education": "Parental Education",
    "internet_access" : "Internet Access",
    "extracurricular_activities": "Extracurricular Activity",
    "part_time_job": "Part-time Job",
    "final_grade": "Final Grade",
    "study_time_hours": "Study Time (Hour)",
    "attendance_percent": "Attendance (%)",
    "sleep_hours": "Sleep Hours",
    "previous_grade": "Previous Grade",
    "final_exam_score": "Final Exam Score",
    "student_id": "Student ID",
}

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("student_performance_dataset.csv", keep_default_na=False, na_values=[""])
    df["improvement"] = df["final_exam_score"] - df["previous_grade"]
    return df

df = load_data()

# -----------------------------
# Sidebar filter
# -----------------------------
st.sidebar.header("Filter Data")

gender = st.sidebar.multiselect(
    "Gender", sorted(df["gender"].unique()), default=sorted(df["gender"].unique())
)
parental = st.sidebar.multiselect(
    "Parental Education",
    sorted(df["parental_education"].unique()),
    default=sorted(df["parental_education"].unique()),
)
internet = st.sidebar.multiselect(
    "Internet Access",
    sorted(df["internet_access"].unique()),
    default=sorted(df["internet_access"].unique()),
)
extra = st.sidebar.multiselect(
    "Extracurricular Activity",
    sorted(df["extracurricular_activities"].unique()),
    default=sorted(df["extracurricular_activities"].unique()),
)
job = st.sidebar.multiselect(
    "Part-time Job",
    sorted(df["part_time_job"].unique()),
    default=sorted(df["part_time_job"].unique()),
)
grade = st.sidebar.multiselect(
    "Final Grade", sorted(df["final_grade"].unique()), default=sorted(df["final_grade"].unique())
)
s_min, s_max = float(df["study_time_hours"].min()), float(df["study_time_hours"].max())
study = st.sidebar.slider("Study Time (Hour)", s_min, s_max, (s_min, s_max))

a_min, a_max = float(df["attendance_percent"].min()), float(df["attendance_percent"].max())
attendance = st.sidebar.slider("Attendance (%)", a_min, a_max, (a_min, a_max))

data = df[
    df["gender"].isin(gender)
    & df["parental_education"].isin(parental)
    & df["internet_access"].isin(internet)
    & df["extracurricular_activities"].isin(extra)
    & df["part_time_job"].isin(job)
    & df["final_grade"].isin(grade)
    & df["study_time_hours"].between(*study)
    & df["attendance_percent"].between(*attendance)
]

if data.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

CHART_H = 340
LAYOUT = dict(margin=dict(l=10, r=10, t=10, b=10), height=CHART_H)

# -----------------------------
# Judul & Deskirpsi
# -----------------------------
with st.container(border=True):
    st.markdown(
        "<h1 style='text-align:center;margin:0'>DASHBOARD PERFORMA SISWA</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;margin:0'>Dashboard ini menampilkan performa akademik siswa "
        "berdasarkan jam belajar, kehadiran, jam tidur, dan latar belakang pendidikan orang tua siswa.</p>",
        unsafe_allow_html=True,
    )

# -----------------------------
# KPI
# -----------------------------
k1, k2, k3 = st.columns(3)

with k1, st.container(border=True):
    st.metric(
        "Rata-rata Final Exam Score",
        f"{data['final_exam_score'].mean():.1f}",
        delta=f"{data['final_exam_score'].mean() - df['final_exam_score'].mean():+.1f} dibanding semua siswa")

with k2, st.container(border=True):
    st.metric(
        "Rata-rata Attendance",
        f"{data['attendance_percent'].mean():.1f}%",
        delta=f"{data['attendance_percent'].mean() - df['attendance_percent'].mean():+.1f} dibanding semua siswa")

with k3, st.container(border=True):
    st.metric(
        "Rata-rata Peningkatan Nilai",
        f"{data['improvement'].mean():+.1f} poin",
        delta=f"{data['improvement'].mean() - df['improvement'].mean():+.1f} dibanding semua siswa")


# -----------------------------
# Study Time vs Final Exam Score
# -----------------------------
with st.container(border=True):
    st.subheader("Study Time vs Final Exam Score")
    fig = px.scatter(
        data, x="study_time_hours", y="final_exam_score",
        color="part_time_job", opacity=0.6,
        hover_data=["student_id", "attendance_percent", "final_grade"],
        labels={**LABEL, "study_time_hours": "Study Time (Hour)"},
    )
    if len(data) > 1 and data["study_time_hours"].nunique() > 1:
        slope, intercept = np.polyfit(data["study_time_hours"], data["final_exam_score"], 1)
        xs = np.array([data["study_time_hours"].min(), data["study_time_hours"].max()])
        fig.add_scatter(x=xs, y=slope * xs + intercept, mode="lines",
                        name="Garis Tren", line=dict(color="white", dash="dash"))
    fig.update_layout(**LAYOUT)
    st.plotly_chart(fig, width="stretch")

# -----------------------------
# Distribusi Grade
# -----------------------------
with st.container(border=True):
    st.subheader("Distribusi Grade")
    per_grade = (
        data.groupby("final_grade")
        .agg(Siswa=("student_id", "count"),
             Rata_rata_Nilai=("final_exam_score", "mean"),
             Rata_rata_Attendance=("attendance_percent", "mean"))
        .round(1)
        .reset_index()
        .rename(columns={"final_grade": "Grade",
                         "Rata_rata_Nilai": "Rata-rata Nilai",
                         "Rata_rata_Attendance": "Rata-rata Attendance"})
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = px.pie(
            per_grade, names="Grade", values="Siswa", hole=0.45,
            category_orders={"Grade": sorted(per_grade["Grade"])},
        )
        fig.update_traces(sort=False, textinfo="label+percent")
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.dataframe(
            per_grade, hide_index=True, width="stretch", height=CHART_H,
        )
# -----------------------------
# Chart
# -----------------------------
a1, a2 = st.columns(2)
with a1, st.container(border=True):
    st.subheader("Rata-rata Nilai per Parental Education")
    group_col = "parental_education"
    grp = data.groupby(group_col, as_index=False)["final_exam_score"].mean()
    fig = px.bar(grp, x=group_col, y="final_exam_score",
                 text=grp["final_exam_score"].round(1),
                 color_discrete_sequence=["#1F6FD1"],
                 labels={group_col: "", "final_exam_score": "Rata-rata Nilai Final Exam Score"})
    fig.update_layout(showlegend=False, **LAYOUT)
    st.plotly_chart(fig, width="stretch")
with a2, st.container(border=True):
    st.subheader("Heatmap Korelasi")
    num_cols = ["study_time_hours", "attendance_percent", "sleep_hours",
                "previous_grade", "final_exam_score"]
    corr = data[num_cols].corr().round(2).rename(index=LABEL, columns=LABEL)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(**LAYOUT)
    st.plotly_chart(fig, width="stretch")