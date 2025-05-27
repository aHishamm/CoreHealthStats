import streamlit as st
import pandas as pd
import datetime as dt
import os
from exporter import (
    extract_zip,
    parse_xml,
    filter_workout_data,
    filter_by_date,
    get_heartrate_for_workout,
    calculate_heartrate_stats,
    nightly_respiratory_rate_stats,
    nightly_spo2_stats,
    daily_step_count,
    daily_resting_hr,
    vo2max_trend,
    walking_efficiency,
    daily_hrv,
    nightly_temp_deviation,
    daily_met_minutes,
    daily_energy,
    add_trimp_column,
)

st.set_page_config(page_title="CoreHealthStats", layout="wide")
st.title("CoreHealthStats: Apple Health Data Explorer")

st.sidebar.header("1. Load or Upload Apple Health Data")
data_source = st.sidebar.radio(
    "Select data source", ["Upload ZIP/XML", "Load from data/ folder"]
)

zip_file = xml_file = None
folder_xml_path = os.path.join(
    os.path.dirname(__file__), "data/apple_health_export", "export.xml"
)

if data_source == "Upload ZIP/XML":
    zip_file = st.sidebar.file_uploader("Upload Apple Health Export ZIP", type=["zip"])
    xml_file = st.sidebar.file_uploader("Or upload export.xml directly", type=["xml"])


@st.cache_data(show_spinner=True)
def load_data_from_xml(xml_path):
    data, workouts = parse_xml(xml_path)
    return data, workouts


def save_uploaded_file(uploaded_file, save_path):
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())


data, workouts = None, None
if data_source == "Load from data/ folder":
    if os.path.exists(folder_xml_path):
        data, workouts = load_data_from_xml(folder_xml_path)
    else:
        st.error(f"No export.xml found in {os.path.dirname(folder_xml_path)}.")
else:
    if zip_file:
        save_uploaded_file(zip_file, "data_upload.zip")
        extract_zip("data_upload.zip")
        xml_path = os.path.join(os.path.dirname(__file__), "data", "export.xml")
        if os.path.exists(xml_path):
            data, workouts = load_data_from_xml(xml_path)
        else:
            st.error("export.xml not found in ZIP.")
    elif xml_file:
        save_uploaded_file(xml_file, "uploaded_export.xml")
        data, workouts = load_data_from_xml("uploaded_export.xml")

if data is not None and workouts is not None:
    st.sidebar.success("Data loaded successfully!")
    st.sidebar.header("2. Filter Options")
    min_date = data["startDate"].min().date()
    max_date = data["endDate"].max().date()
    date_range = st.sidebar.date_input(
        "Select date range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
    tz = data["startDate"].dt.tz if hasattr(data["startDate"].dt, "tz") else None
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        if tz is not None:
            if start_date.tzinfo is None:
                start_date = start_date.tz_localize(tz)
            else:
                start_date = start_date.tz_convert(tz)
            if end_date.tzinfo is None:
                end_date = end_date.tz_localize(tz)
            else:
                end_date = end_date.tz_convert(tz)
        data = filter_by_date(data, start_date, end_date)
        workouts = filter_by_date(workouts, start_date, end_date)
    st.sidebar.header("3. Select Analysis")
    analysis = st.sidebar.radio(
        "Choose analysis",
        [
            "Overview",
            "Workouts",
            "Heart Rate",
            "Respiratory Rate",
            "SpO2",
            "Steps",
            "Energy",
            "VO2Max",
            "HRV",
            "Temperature",
            "MET Minutes",
        ],
    )
    st.sidebar.markdown("---")

    if analysis == "Overview":
        st.header("Health Data Overview")
        st.write("**Records:**", len(data))
        st.write("**Workouts:**", len(workouts))
        st.dataframe(data.head(100))
    elif analysis == "Workouts":
        st.header("Workout Summary")
        st.dataframe(workouts)
        workout_types = workouts["workoutActivityType"].unique()
        selected_type = st.selectbox("Select workout type", workout_types)
        filtered = filter_workout_data(workouts, selected_type)
        st.write(f"Showing {len(filtered)} {selected_type} workouts.")
        st.dataframe(filtered)
        st.line_chart(filtered.set_index("startDate")["duration"])
        # gender = st.selectbox("Select gender for TRIMP", ["male", "female"])
        # try:
        #     trimp_df = add_trimp_column(filtered, data, gender)
        #     st.subheader("TRIMP Score per Workout")
        #     st.dataframe(trimp_df[['startDate', 'duration', 'avg_hr', 'TRIMP']])
        #     st.line_chart(trimp_df.set_index('startDate')['TRIMP'])
        # except NotImplementedError as e:
        #     st.warning(str(e))
        st.subheader("Per-Workout Detailed Stats")
        selected_workout_idx = st.selectbox(
            "Select a workout to view details",
            filtered.index,
            format_func=lambda i: f"{filtered.loc[i, 'startDate']} - {filtered.loc[i, 'workoutActivityType']}",
        )
        selected_workout = filtered.loc[[selected_workout_idx]]
        st.write("**Workout Details:**")
        st.write(selected_workout.T)

        # Heart Rate per workout
        hr_data = data[data["type"] == "HeartRate"]
        hr_for_workout = get_heartrate_for_workout(hr_data, selected_workout)
        st.write(f"Heart Rate samples: {len(hr_for_workout)}")
        if not hr_for_workout.empty:
            st.line_chart(hr_for_workout.set_index("startDate")["value"])
            hr_stats = calculate_heartrate_stats(hr_for_workout)
            st.write("**Heart Rate Stats:**", hr_stats)
        else:
            st.info("No heart rate data for this workout.")

        # HRV per workout
        hrv_data = data[data["type"] == "HeartRateVariabilitySDNN"]
        hrv_for_workout = hrv_data[
            (hrv_data["startDate"] >= selected_workout["startDate"].item())
            & (hrv_data["endDate"] <= selected_workout["endDate"].item())
        ]
        st.write(f"HRV samples: {len(hrv_for_workout)}")
        if not hrv_for_workout.empty:
            st.line_chart(hrv_for_workout.set_index("startDate")["value"])
            st.write("HRV Median:", hrv_for_workout["value"].median())
        else:
            st.info("No HRV data for this workout.")

        # Respiratory Rate per workout
        rr_data = data[data["type"] == "RespiratoryRate"]
        rr_for_workout = rr_data[
            (rr_data["startDate"] >= selected_workout["startDate"].item())
            & (rr_data["endDate"] <= selected_workout["endDate"].item())
        ]
        st.write(f"Respiratory Rate samples: {len(rr_for_workout)}")
        if not rr_for_workout.empty:
            st.line_chart(rr_for_workout.set_index("startDate")["value"])
            st.write("Respiratory Rate Mean:", rr_for_workout["value"].mean())
        else:
            st.info("No Respiratory Rate data for this workout.")

        # SpO2 per workout
        spo2_data = data[data["type"] == "OxygenSaturation"]
        spo2_for_workout = spo2_data[
            (spo2_data["startDate"] >= selected_workout["startDate"].item())
            & (spo2_data["endDate"] <= selected_workout["endDate"].item())
        ]
        st.write(f"SpO2 samples: {len(spo2_for_workout)}")
        if not spo2_for_workout.empty:
            st.line_chart(spo2_for_workout.set_index("startDate")["value"])
            st.write("SpO2 Median:", spo2_for_workout["value"].median())
        else:
            st.info("No SpO2 data for this workout.")

        # VO2Max per workout
        vo2_data = data[data["type"] == "VO2Max"]
        vo2_for_workout = vo2_data[
            (vo2_data["startDate"] >= selected_workout["startDate"].item())
            & (vo2_data["endDate"] <= selected_workout["endDate"].item())
        ]
        st.write(f"VO2Max samples: {len(vo2_for_workout)}")
        if not vo2_for_workout.empty:
            st.line_chart(vo2_for_workout.set_index("startDate")["value"])
            st.write("VO2Max Max:", vo2_for_workout["value"].max())
        else:
            st.info("No VO2Max data for this workout.")

        # Energy per workout
        energy_data = data[
            data["type"].isin(["ActiveEnergyBurned", "BasalEnergyBurned"])
        ]
        energy_for_workout = energy_data[
            (energy_data["startDate"] >= selected_workout["startDate"].item())
            & (energy_data["endDate"] <= selected_workout["endDate"].item())
        ]
        st.write(f"Energy samples: {len(energy_for_workout)}")
        if not energy_for_workout.empty:
            st.line_chart(energy_for_workout.set_index("startDate")["value"])
            st.write("Total Energy (sum):", energy_for_workout["value"].sum())
        else:
            st.info("No Energy data for this workout.")
    elif analysis == "Heart Rate":
        st.header("Heart Rate Analysis")
        hr_data = data[data["type"] == "HeartRate"]
        st.write(f"Total heart rate records: {len(hr_data)}")
        st.line_chart(hr_data.set_index("startDate")["value"])
        st.subheader("Resting Heart Rate (Daily Median)")
        rhr = daily_resting_hr(data)
        st.line_chart(rhr)
        st.subheader("Heart Rate Variability (SDNN)")
        hrv = daily_hrv(data)
        st.line_chart(hrv["sdnn"])
    elif analysis == "Respiratory Rate":
        st.header("Nightly Respiratory Rate")
        rr_stats = nightly_respiratory_rate_stats(data)
        st.line_chart(rr_stats["RR_mean"])
        st.line_chart(rr_stats["RR_z"])
        st.write(rr_stats[rr_stats["elevated"]])
    elif analysis == "SpO2":
        st.header("Nightly SpO2 Stats")
        spo2_stats = nightly_spo2_stats(data)
        st.line_chart(spo2_stats["SpO2_median"])
        st.line_chart(spo2_stats["pct_time_below_90"])
        st.write(spo2_stats)
    elif analysis == "Steps":
        st.header("Daily Step Count")
        steps = daily_step_count(data)
        st.line_chart(steps["steps"])
        st.line_chart(steps["rolling7"])
        st.write(steps)
    elif analysis == "Energy":
        st.header("Daily Energy Expenditure")
        energy = daily_energy(data)
        st.line_chart(energy["total_kcal"])
        st.write(energy)
    elif analysis == "VO2Max":
        st.header("VO2Max Trend")
        vo2 = vo2max_trend(data)
        st.line_chart(vo2)
        st.write(vo2)
    elif analysis == "HRV":
        st.header("Daily Heart Rate Variability (SDNN)")
        hrv = daily_hrv(data)
        st.line_chart(hrv["sdnn"])
        st.line_chart(hrv["z_score"])
        st.write(hrv)
    elif analysis == "Temperature":
        st.header("Nightly Wrist Temperature Deviation")
        temp = nightly_temp_deviation(data)
        st.line_chart(temp["wrist_temp"])
        st.line_chart(temp["delta"])
        st.write(temp)
    elif analysis == "MET Minutes":
        st.header("Daily MET Minutes (Physical Effort)")
        met = daily_met_minutes(data)
        st.line_chart(met)
        st.write(met)
else:
    st.info("Please upload your Apple Health export ZIP or XML file to begin.")
