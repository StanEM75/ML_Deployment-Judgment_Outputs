import os
import sys
import time
import pandas as pd

from my_model_package.forecasting.utils import pre_processing

if __name__ == '__main__':
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
    processed_data = pre_processing(df)
    end = time.time()
    print(f'Time taken to process data: {round(end - start, 2)} seconds')


    processed_data.to_csv('processed_data.csv', index=False)