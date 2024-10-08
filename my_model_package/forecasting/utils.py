import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Create a function to map the description to a category
def map_violation_category(description):   
    mapping = {
    "fugitive" : "Escape",
    "waste" : "Public Nuisance",
    "Open Storage/ Non-residential" : "Public Nuisance",
    "unlawful storage(Non-RESIDENTIAL)" : "Public Nuisance",
    "Improper placement" : "Public Nuisance",
    "Open Storage/ Residential/ Debris (R1)" : "Nuisance linked to Residential Space",
    "unlawful storage(RESIDENTIAL)" : "Nuisance linked to Residential Space",
    "placement of Courville Containers" : "Nuisance linked to Residential Space",
    "'Open Storage/ Residential" : "Nuisance linked to Residential Space",
    "failure to obtain" : "No Certificate",
    "Failed to secure" : "No Certificate",
    "failure of owner to obtain" : "No Certificate",
    "Failure to furnish a written" : "No Certificate",
    "Faillure to obtain a certificate" : "No Certificate",
    "Occupancy without certificate" : "No Certificate",
    "Violation of time limit for approved containers to remain at curbside" : "No Certificate",
    "without a Permit" : "No Certificate",
    "depositing bulk solid" : "Public Nuisance",
    "Unlawful storage" : "Public Nuisance",
    "Banner" : "Public Nuisance",
    "Business signs located" : "Public Nuisance",
    "Advertising signs located" : "Public Nuisance",
    "improperly stored" : "Public Nuisance",
    "Failure to remove unlawful signage" : "Public Nuisance",
    "Rodent harborage one-or two-family dwelling or commercial building" : "Public Nuisance",
    "Defective" : "Defective part on a building",
    "Failure to maintain a vacant building" : "Building maintenance failure",
    "Failure to abate unsafe condition for Building" : "Building maintenance failure",
    "Failure to maintain" : "Building maintenance failure",
    "Contaminated" : "Sanitary Defect",
    "unsanitary" : "Sanitary Defect",
    "grafitti" : "Vandalism",
    "Unlawful  rental of property" : "Unlawful rental",
    "Unlawful  rental" : "Unlawful rental",
    "Unlawful occupation of rental property without lead clearance" : "Unlawful rental",
    "excrement" : "Public Nuisance",
    "Other Non-Compliance with Land Use" : "Non-Compliance with Land Use",
    "weeds" : "Drugs"
    }
    for key, category in mapping.items():
        if key.lower() in description.lower():
            return category
    return "Other" 

# Convert the least represented categories into 'Other'
def convert_to_other(row):
    categories = ["No Certificate", "Public Nuisance", "Drugs"]
    
    if row['violation_category'] not in categories:
        return "Other"
    else:
        return row['violation_category']
  
# Keep the responsibles only
def keep_responsibles(df):
    responsible = ['Responsible (Fine Waived) by Admission',
               'Responsible (Fine Waived) by City Dismissal',
               'Responsible (Fine Waived) by Determination',
               'Responsible - Compl/Adj by Default',
               'Responsible - Compl/Adj by Determination',
               'Responsible by',
               'Responsible by Admission',
               'Responsible by Default',
               'Responsible by Determination',
               'Responsible by Dismissal',
               'Responsible by Responsible (Fine Waived)']
    
    df = df[df['disposition'].isin(responsible)]
    return df

# Date into datetimes format
def manage_dates(df):
    # Judgment date to datetime
    df['judgment_date'] = pd.to_datetime(df['judgment_date'],format='mixed').dt.date
    # Hearing date into datetime
    df['hearing_date'] = pd.to_datetime(df['hearing_date'],format='mixed').dt.date
    # Violation date to datetime
    df['violation_date'] = pd.to_datetime(df['violation_date'], errors='coerce')
    # Delete rows where violation_date is null or and keep the rows between 2005 and 2023
    df = df[(df['violation_date'].notnull()) & (df['violation_date'] < '2024-01-01') & (df['violation_date'] > '2004-12-31')]

# Check the timedelta between the hearing and judgment date
def is_judgement_later(row):
    row['judgment_date'] = pd.to_datetime(row['judgment_date'], format='mixed', errors='coerce')
    row['hearing_date'] = pd.to_datetime(row['hearing_date'], format='mixed', errors='coerce')
    
    if pd.isnull(row['judgment_date']) or pd.isnull(row['hearing_date']):
        return 0
    
    if row['judgment_date'] <= row['hearing_date']:
        return 0
    elif row['judgment_date'].month == row['hearing_date'].month:
        return 1
    elif row['judgment_date'].year == row['hearing_date'].year:
        return 2
    else:
        return 3

# Pre-Processing Function
def pre_processing(df):
    # Keep only the columns useful for the analysis and prediction
    columns_to_keep= ['agency_name','state','violation_date','hearing_date','hearing_time',
         'judgment_date','violation_description','disposition',
         'fine_amount','late_fee','discount_amount',
          'judgment_amount','balance_due','payment_status','city']
      
    df = df[columns_to_keep]

    # Apply the mapping to the dataframe
    df['violation_category'] = df['violation_description'].astype(str).apply(lambda x: map_violation_category(x))

    df['violation_category'] = df.apply(convert_to_other, axis=1)

    # Keep the responsibles only
    df = keep_responsibles(df)

    # Remove Useless Spaces from Street Names
    #df['violation_street_name'] = df['violation_street_name'].str.strip()

    # Capitalize Locations Names
    #df['violation_street_name'] = df['violation_street_name'].str.capitalize()
    df['state'] = df['state'].str.capitalize()
    df['city'] = df['city'].map(lambda x: str(x).strip().capitalize())

    # Remove violation_description column
    df.drop(columns=['violation_description'], inplace=True)

    # Create only two categories for payment_status : NO PAYMENT & PAID
    df['payment_status'] = df['payment_status'].apply(lambda x: 'NO PAYMENT' if x not in ['PAID IN FULL'] else x)

    # Create a new column to see if the judgment date is later than the hearing date
    df['is_judgment_later'] = df.apply(is_judgement_later, axis=1)

    # Drop NEIGHBORHOOD CITY HALLS  
    df = df[df['agency_name'] != 'NEIGHBORHOOD CITY HALLS']

    # Drop rows with judgment_amount = 0. Other amounts are not realistic or difficult to interpret.
    df = df.query("judgment_amount>0")

    return df

# Feature Engineering 1 : Encode non-Numerical Variables
def label_encode(df,list_columns):
    label_encoder = LabelEncoder()
    for col in list_columns:
        df[col] = label_encoder.fit_transform(df[col])
    return df

# Feature Enginnering 2 : Transform the State and City informations into a more general information : Is the violator living in Detroit, Michigan or elsewhere
def state_violator_origin(row):
    conditions = {
        ('MI', 'Detroit'): 'Violator living in Detroit',
        ('MI',): 'Violator living in Michigan but not in Detroit'
    }
    return conditions.get((row['state'], row['city']), 'Violator living outside Michigan')

# Feature Engineering 3 : Transform the Amount of Discount into a Promotion/No Promotion information
def amount_to_discount(row):
    if row['discount_amount']==0:
        return "No Discount"
    else:
        return "Discount" 

# Apply the discount status to check if there is a discount or not 
def feature_engineering(df):
    columns_to_drop_only_NaN = ['state', 'discount_amount','fine_amount','late_fee']

    columns_to_drop_after_transformation = ['violation_date','hearing_date', 'hearing_time', 'judgment_date','discount_amount','city','state']

    columns_to_encode = ['agency_name', 'disposition', 'payment_status','violation_category','violator_origin','discount_status']
    
    df['discount_status'] = df.apply(amount_to_discount, axis=1)

    # Definite the violator's origin
    df['violator_origin'] = df.apply(state_violator_origin, axis=1)

    # Drop NaN values
    df.dropna(subset=columns_to_drop_only_NaN, inplace=True)

    # Drop dates columns
    df.drop(columns=columns_to_drop_after_transformation, inplace=True)

    #Encode the categorical columns
    df = label_encode(df,columns_to_encode)

    # Reset the index
    df.reset_index(inplace=True,drop=True)












