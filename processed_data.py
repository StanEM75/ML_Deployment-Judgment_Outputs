import os
import sys
import time

import pandas as pd
from utils.utils import upper_case_strip


def is_judgement_later(row):
    return 0 if (pd.isnull(row['judgment_date']) or row['judgment_date'] <= row['hearing_date']) else \
           1 if row['judgment_date'].month == row['hearing_date'].month else \
           2 if row['judgment_date'].year == row['hearing_date'].year else 3

def processed_data_for_data_science(df : pd.DataFrame, columns_to_drop : list) -> pd.DataFrame:

    '''
    This function takes in a dataframe and processes it for our data science model. 
    Our data science project is to predict whether a blight violation will be paid or not, if the the violator is responsible for its own violation.

    The function does the following:


    
    '''
     # Drop nan values in specific columns
    df = df.dropna(subset=columns_to_drop_only_NaN)

    df['judgment_date'] = pd.to_datetime(df['judgment_date'],format='mixed').dt.date
    df['hearing_date'] = pd.to_datetime(df['hearing_date'],format='mixed').dt.date
    
    # Violation date to datetime
    df['violation_date'] = pd.to_datetime(df['violation_date'], errors='coerce')

    # Delete rows where violation_date is null or superior to 2024
    df = df[(df['violation_date'].notnull()) & (df['violation_date'] < '2023-01-01') & (df['violation_date'] > '2004-12-31')]

    # Create only two categories for payment_status : NO PAYMENT & PAID
    df['payment_status'] = df['payment_status'].apply(lambda x: 'NO PAYMENT' if x not in ['PAID IN FULL'] else x)

    # Create a new column to see if the judgment date is later than the hearing date
    df['is_judgment_later'] = df.apply(is_judgement_later, axis=1)

    # Drop NEIGHBORHOOD CITY HALLS  
    df = df[df['agency_name'] != 'NEIGHBORHOOD CITY HALLS']

    # Drop all rows where counts of each disposition is less than 1000
    # We only take violators who were considered responsible because it seems to be normal to not pay if you are not guilty
    df = df.groupby('disposition').filter(lambda x: len(x) > 10000)
    
    df['disposition'] = df.loc[~df['disposition'].str.contains('NOT RESPONSIBLE', case=False)]['disposition']

    # Drop columns that are not needed to create our model. It is due to uncessary data that could lead to overfitting, data privacy or incomplete data.
    df = df.drop(columns_to_drop, axis=1)

    # For each column with object type, each value is transformed in uppercase
    df[[col for col in df.columns if df[col].dtype == 'O']] = df[[col for col in df.columns if df[col].dtype == 'O']].map(upper_case_strip)

    return df




if __name__ == '__main__':
    import os
    print(os.getcwd())

    df = pd.read_csv('data/blight_violations.csv')

    columns_to_drop = ['collection_status', 'parcelno', 'geom', 
                       'oid', 'clean_up_cost', 'non_us_str_code', 'country', 
                       'violation_zip_code','ticket_id','ticket_number',
                       'violator_id','payment_date','violation_address', 
                       'inspector_name', 'violator_name',
                       'violation_street_number','mailing_address_str_number', 'hearing_date',
                       'hearing_time', 'judgment_date','violation_date',
                       'ticket_issued_time','violation_code','violation_description',
                       'violation_code','zip_code']
    
    columns_to_drop_only_NaN = ['state', 'city','payment_status','payment_amount','judgment_date','hearing_date']

    # Add a timer to see how long it takes to run the code
    start = time.time()
    processed_data = processed_data_for_data_science(df,columns_to_drop)
    end = time.time()
    print(f'Time taken to process data: {round(end - start, 2)} seconds')


    processed_data.to_csv('processed_data.csv', index=False)