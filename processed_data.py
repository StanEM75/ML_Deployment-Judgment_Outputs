import os
import time
import pandas as pd

from my_model_package.forecasting.utils import pre_processing

if __name__ == '__main__':
    print(os.getcwd())

    df = pd.read_csv('data/blight_violations.csv')
    
    # Add a timer to see how long it takes to run the code
    start = time.time()
    processed_data = pre_processing(df)
    processed_data.to_csv('processed_data.csv', index=False)
    end = time.time()
    print(f'Time taken to process data: {round(end - start, 2)} seconds')
    