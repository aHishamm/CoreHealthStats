import zipfile
import os
import xml.etree.ElementTree as ET 
import pandas as pd 
import datetime as dt 
def extract_zip(zip_path):
    extract_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted {zip_path} to {extract_dir}")

def parse_xml(path,save_to_feather=False, save_to_csv=False): 
    tree = ET.parse('path') 
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
    
def filter_workout_data(df, workout_type):
    return df[df['workoutActivityType'] == workout_type]

def filter_by_date(df, start_date, end_date): #Need to pass a pd.to_datetime object for start_date and end_date. i.e., pd.to_datetime(dt.date(2023,12,12),utc=True)
    mask = (df['creationDate'] >= start_date) & (df['creationDate'] <= end_date)
    return df.loc[mask]

def get_heartrate_for_workout(heartrate, workout): #Getting HR information for a single workout / pass HR filtered data to heartrate i.e. heartrate[heartrate['type'] == 'HeartRate']
    def get_heartrate_for_date(hr, start, end):
        hr = hr[hr["startDate"] >= start]
        hr = hr[hr["endDate"] <= end]
        return hr
    return get_heartrate_for_date(heartrate, workout["startDate"].item(), workout["endDate"].item())
