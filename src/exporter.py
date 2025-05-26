import zipfile
import os
import xml.etree.ElementTree as ET 
import pandas as pd 
import datetime as dt 
from typing import Union, Optional, Tuple, Dict, Any
import numpy as np
def extract_zip(zip_path: str) -> None:
    """
    Extract a zip file containing Apple Health data to the data directory.
    
    Args:
        zip_path: Path to the zip file to extract
        
    Returns:
        None
    """
    extract_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted {zip_path} to {extract_dir}")

def parse_xml(path: str, save_to_feather: bool = False, save_to_csv: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]: 
    """
    Parse Apple Health export XML file and extract Record and Workout data.
    
    Args:
        path: Path to the XML file to parse
        save_to_feather: Whether to save extracted data to feather format
        save_to_csv: Whether to save extracted data to CSV format
        
    Returns:
        Tuple containing two DataFrames:
        - First DataFrame contains health record data
        - Second DataFrame contains workout data
    """
    tree = ET.parse(path) 
    root = tree.getroot()
    record_list = [x.attrib for x in root.iter('Record')]
    data = pd.DataFrame(record_list)
    for col in ['creationDate', 'startDate', 'endDate']:
        data[col] = pd.to_datetime(data[col])
    data['value'] = pd.to_numeric(data['value'], errors='coerce')
    data['value'] = data['value'].fillna(1.0)
    data['type'] = data['type'].str.replace('HKQuantityTypeIdentifier', '')
    data['type'] = data['type'].str.replace('HKCategoryTypeIdentifier', '')
    workout_list = [x.attrib for x in root.iter('Workout')]
    workout_data = pd.DataFrame(workout_list)
    workout_data['workoutActivityType'] = workout_data['workoutActivityType'].str.replace('HKWorkoutActivityType', '')
    for col in ['creationDate', 'startDate', 'endDate']:
        workout_data[col] = pd.to_datetime(workout_data[col])
    workout_data['duration'] = pd.to_numeric(workout_data['duration'])
    if save_to_feather:
        data.to_feather('export/data.ftr')
        workout_data.to_feather('export/workout_data.ftr')
    if save_to_csv: 
        data.to_csv('export/data.csv', index=False)
        workout_data.to_csv('export/workout_data.csv', index=False)
    
    return data, workout_data
    
def filter_workout_data(df: pd.DataFrame, workout_type: str) -> pd.DataFrame:
    """
    Filter workout data by workout activity type.
    
    Args:
        df: DataFrame containing workout data
        workout_type: Type of workout to filter for (e.g., 'Running', 'Walking')
        
    Returns:
        DataFrame containing only workouts of the specified type
    """
    return df[df['workoutActivityType'] == workout_type]

def filter_by_date(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """
    Filter data by date range.
    
    Args:
        df: DataFrame to filter
        start_date: Start date for filtering (as pd.Timestamp)
        end_date: End date for filtering (as pd.Timestamp)
        
    Note:
        Need to pass a pd.to_datetime object for start_date and end_date.
        i.e., pd.to_datetime(dt.date(2023,12,12),utc=True)
        
    Returns:
        DataFrame filtered to include only rows between start_date and end_date
    """
    mask = (df['creationDate'] >= start_date) & (df['creationDate'] <= end_date)
    return df.loc[mask]

def get_heartrate_for_workout(heartrate: pd.DataFrame, workout: pd.DataFrame) -> pd.DataFrame:
    """
    Get heart rate measurements during a specific workout.
    
    Args:
        heartrate: DataFrame containing heart rate data
                  (filtered for heart rate, e.g., heartrate[heartrate['type'] == 'HeartRate'])
        workout: DataFrame containing a single workout (one row)
        
    Returns:
        DataFrame containing heart rate measurements that occurred during the workout
    """
    def get_heartrate_for_date(hr: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Filter heart rate data for a specific time range.
        
        Args:
            hr: Heart rate DataFrame
            start: Start time
            end: End time
            
        Returns:
            Filtered heart rate DataFrame
        """
        hr = hr[hr["startDate"] >= start]
        hr = hr[hr["endDate"] <= end]
        return hr
    
    return get_heartrate_for_date(heartrate, workout["startDate"].item(), workout["endDate"].item())

def calculate_heartrate_stats(heartrate_data: pd.DataFrame, age: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate statistics for heart rate measurements from a workout.
    
    Args:
        heartrate_data: DataFrame containing heart rate measurements
                        (typically filtered for a specific workout using get_heartrate_for_workout)
        age: Age of the user in years, used for more accurate heart rate zone calculations.
             If not provided, measured max HR will be used as reference.
    
    Returns:
        Dictionary containing the following statistics:
        - min_hr: Minimum heart rate
        - max_hr: Maximum heart rate
        - avg_hr: Average heart rate
        - median_hr: Median heart rate
        - std_hr: Standard deviation of heart rate
        - hr_zones: Dictionary with time spent in different heart rate zones
                    (resting: <60, fat burn: 60-70%, cardio: 70-80%, peak: >80% of max HR)
    """
    if heartrate_data.empty:
        return {
            "min_hr": None,
            "max_hr": None,
            "avg_hr": None,
            "median_hr": None,
            "std_hr": None,
            "hr_zones": {
                "resting": 0,
                "fat_burn": 0,
                "cardio": 0,
                "peak": 0
            }
        }
    hr_values = heartrate_data['value']
    stats = {
        "min_hr": hr_values.min(),
        "max_hr": hr_values.max(),
        "avg_hr": hr_values.mean(),
        "median_hr": hr_values.median(),
        "std_hr": hr_values.std()
    }
    if age is not None:
        estimated_max_hr = 220 - age
        stats["estimated_max_hr"] = estimated_max_hr
    else:
        estimated_max_hr = stats["max_hr"]
    heartrate_data['duration'] = (heartrate_data['endDate'] - heartrate_data['startDate']).dt.total_seconds()
    zones = {
        "resting": heartrate_data[heartrate_data['value'] < 60]['duration'].sum(),
        "fat_burn": heartrate_data[(heartrate_data['value'] >= 60) & 
                                  (heartrate_data['value'] < 0.7 * estimated_max_hr)]['duration'].sum(),
        "cardio": heartrate_data[(heartrate_data['value'] >= 0.7 * estimated_max_hr) & 
                                (heartrate_data['value'] < 0.8 * estimated_max_hr)]['duration'].sum(),
        "peak": heartrate_data[heartrate_data['value'] >= 0.8 * estimated_max_hr]['duration'].sum()
    }
    stats["hr_zones"] = zones
    stats["total_duration"] = heartrate_data['duration'].sum()
    if stats["total_duration"] > 0:
        stats["hr_zone_percentages"] = {
            zone: (duration / stats["total_duration"]) * 100 
            for zone, duration in zones.items()
        }
    else:
        stats["hr_zone_percentages"] = {zone: 0 for zone in zones}
    return stats

#Data points I need to consider with the health analysis 
# 1. RespiratoryRate 2. OxygenSaturation 3. StepCount 4. BasalEnergyBurned 5. ActiveEnergyBurned 6. RestingHeartRate 7. VO2Max  
# 8. WalkingHeartRateAverage 9. WalkingSpeed 10. AppleSleepingBreathingDisturbances 11. PhysicalEffort
# 12. HeartRateVariabilitySDNN 13. AppleSleepingWristTemperature

# For internal call 
def _daily_agg(df: pd.DataFrame, value_col: str,
               date_col: str = "startDate",
               how: str = "sum") -> pd.Series:
    """
    Group any record-level dataframe to daily granularity.

    Parameters
    ----------
    df, value_col : dataframe and column to aggregate
    how           : 'sum', 'mean', 'median', etc.

    Returns
    -------
    pd.Series indexed by date
    """
    return getattr(df.set_index(date_col)
                     .value_col
                     .resample("D"), how)()

def nightly_respiratory_rate_stats(df: pd.DataFrame) -> pd.DataFrame:
    rr = df[df["type"] == "RespiratoryRate"].copy()
    rr['date'] = rr['startDate'].dt.date
    nightly = rr.groupby('date')['value'].mean()
    baseline = nightly.rolling(21, min_periods=14).mean()
    z_score  = (nightly - baseline) / rr.groupby('date')['value'].std().rolling(21, min_periods=14).mean()
    return pd.DataFrame({"RR_mean": nightly,
                         "RR_baseline": baseline,
                         "RR_z": z_score,
                         "elevated": z_score > 2})

def nightly_spo2_stats(df: pd.DataFrame) -> pd.DataFrame:
    spo2 = df[df["type"] == "OxygenSaturation"].copy()
    spo2['date'] = spo2['startDate'].dt.date
    grouped = spo2.groupby('date')['value']
    return pd.DataFrame({
        'SpO2_median': grouped.median(),
        'SpO2_p01': grouped.quantile(0.01),
        'pct_time_below_90': (spo2['value'] < 90).groupby(spo2['date']).mean()*100
    })

def daily_step_count(df: pd.DataFrame) -> pd.DataFrame:
    steps = df[df["type"] == "StepCount"]
    daily = steps.groupby(steps['startDate'].dt.date)['value'].sum()
    rolling7 = daily.rolling(7).mean()
    streak = (daily > 0).astype(int)
    streak = streak * (streak.groupby((streak != streak.shift()).cumsum()).cumcount() + 1)
    return pd.DataFrame({'steps': daily,
                         'rolling7': rolling7,
                         'streak': streak})

def daily_resting_hr(df: pd.DataFrame) -> pd.Series:
    rhr = df[df["type"] == "RestingHeartRate"]
    return rhr.groupby(rhr['startDate'].dt.date)['value'].median()

def vo2max_trend(df: pd.DataFrame) -> pd.Series:
    vo2 = df[df["type"] == "VO2Max"]
    return vo2.groupby(vo2['startDate'].dt.date)['value'].max().sort_index()

def walking_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    whr = df[df["type"] == "WalkingHeartRateAverage"]
    wsp = df[df["type"] == "WalkingSpeed"]
    hr = whr.groupby(whr['startDate'].dt.date)['value'].mean()
    sp = wsp.groupby(wsp['startDate'].dt.date)['value'].mean()  # m/s
    eff = hr / sp
    return pd.DataFrame({'whr_avg': hr, 'walk_speed': sp, 'hr_speed_ratio': eff})

def daily_hrv(df: pd.DataFrame) -> pd.DataFrame:
    hrv = df[df["type"] == "HeartRateVariabilitySDNN"]
    daily = hrv.groupby(hrv['startDate'].dt.date)['value'].median()
    baseline = daily.rolling(7).mean()
    z = (daily - baseline) / daily.rolling(7).std()
    return pd.DataFrame({'sdnn': daily, 'baseline7': baseline, 'z_score': z})

def nightly_temp_deviation(df: pd.DataFrame) -> pd.DataFrame:
    temp = df[df["type"] == "AppleSleepingWristTemperature"]
    temp['date'] = temp['startDate'].dt.date
    nightly = temp.groupby('date')['value'].mean()
    baseline = nightly.rolling(21, min_periods=14).median()
    deviation = nightly - baseline
    return pd.DataFrame({'wrist_temp': nightly,
                         'baseline': baseline,
                         'delta': deviation})

def daily_met_minutes(df: pd.DataFrame) -> pd.Series:
    effort = df[df["type"] == "PhysicalEffort"]
    return effort.groupby(effort['startDate'].dt.date)['value'].sum()

def daily_energy(df: pd.DataFrame,
                 convert_to_kcal: bool = True) -> pd.DataFrame:
    """
    Return a daily table of basal, active and total energy in kilocalories.
    Parameters
    ----------
    df : Apple-Health record dataframe
    convert_to_kcal : perform unit normalisation (recommended)
    Returns
    -------
    pd.DataFrame indexed by date with columns:
        basal_kcal, active_kcal, total_kcal
    """
    energy_df = df[df["type"].isin({"BasalEnergyBurned",
                                    "ActiveEnergyBurned"})].copy()
    if convert_to_kcal:
        def _to_kcal(row):
            unit = str(row.get("unit", "")).lower()
            val  = row["value"]
            if unit == "cal":               
                return val / 1000.0
            if unit in {"kj", "kilojoule"}:
                return val * 0.239006
            return val                 
        energy_df["kcal_val"] = energy_df.apply(_to_kcal, axis=1)
    else:
        energy_df["kcal_val"] = energy_df["value"]
    energy_df["date"] = energy_df["startDate"].dt.date
    daily = (energy_df
             .groupby(["date", "type"])["kcal_val"]
             .sum()
             .unstack(fill_value=0)
             .rename(columns={
                 "BasalEnergyBurned": "basal_kcal",
                 "ActiveEnergyBurned": "active_kcal"
             }))
    for col in ("basal_kcal", "active_kcal"):
        if col not in daily:
            daily[col] = 0.0
    daily["total_kcal"] = daily["basal_kcal"] + daily["active_kcal"]
    return daily.sort_index()

def daily_resting_hr(data: pd.DataFrame) -> pd.Series:
    rhr = data[data['type'] == 'RestingHeartRate'].copy()
    rhr['date'] = rhr['startDate'].dt.date
    return rhr.groupby('date')['value'].median()


def observed_max_hr(data: pd.DataFrame) -> int:
    return int(data.loc[data['type'] == 'HeartRate', 'value'].max())

def trimp_score(duration_min: float,
                hr_avg: float,
                hr_rest: float,
                hr_max: float,
                gender: str = "male") -> float:
    """
    Classical Bannister TRIMP.
    """
    delta = (hr_avg - hr_rest) / (hr_max - hr_rest)
    if delta <= 0:                       
        return 0.0
    b = 1.92 if gender.lower() == "male" else 1.67
    return duration_min * delta * np.exp(b * delta)

def add_trimp_column(
        workouts : pd.DataFrame,
        data     : pd.DataFrame,
        gender   : str = "male"
) -> pd.DataFrame:
    """
    Returns a copy of `workouts` with `avg_hr` and `TRIMP` columns.

    Requires columns:
        workouts: startDate, endDate, duration     (duration in minutes)
        data    : HeartRate and RestingHeartRate rows
    """
    hr_rest_series = daily_resting_hr(data)
    hr_max_global  = observed_max_hr(data)
    hr_samples = data[data['type'] == 'HeartRate'][[
        'startDate', 'endDate', 'value'
    ]].copy()
    hr_samples['dur_min'] = (
        hr_samples['endDate'] - hr_samples['startDate']
    ).dt.total_seconds() / 60.0
    # wk_intervals = pd.IntervalIndex.from_arrays(
    #     workouts['startDate'], workouts['endDate'], closed='both'
    # )
    # # Use get_indexer_non_unique to handle overlapping intervals
    # wk_idx, hr_idx = wk_intervals.get_indexer_non_unique(hr_samples['startDate'])
    # # Both wk_idx and hr_idx are the same length, and correspond to the filtered heart rate samples
    # hr_samples_filtered = hr_samples.iloc[hr_idx].copy()
    # hr_samples_filtered = hr_samples_filtered.reset_index(drop=True)
    # hr_samples_filtered['wk_idx'] = wk_idx
    # hr_samples_filtered = hr_samples_filtered[hr_samples_filtered['wk_idx'] != -1]
    # avg_hr_by_wk = (
    #     hr_samples_filtered
    #     .groupby('wk_idx')
    #     .apply(lambda g: np.average(g['value'], weights=g['dur_min']) if g['dur_min'].sum() > 0 else np.nan)
    #     .reindex(range(len(workouts)))
    # )
    # wk = workouts.copy()
    # wk['avg_hr'] = avg_hr_by_wk.values
    # wk['date']   = wk['startDate'].dt.date
    # wk['hr_rest']= wk['date'].map(hr_rest_series).fillna(hr_rest_series.median())
    # wk['TRIMP']  = wk.apply(
    #     lambda row: trimp_score(
    #         duration_min=row['duration'],
    #         hr_avg      =row['avg_hr'],
    #         hr_rest     =row['hr_rest'],
    #         hr_max      =hr_max_global,
    #         gender      =gender),
    #     axis=1
    # )
    # return wk.drop(columns='date')
    raise NotImplementedError("TRIMP calculation not working now.")