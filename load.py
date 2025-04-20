import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)
stop_words = set(stopwords.words('english'))

# File paths
linkedin_path = "C:/Users/Lenovo/Desktop/CN datasets/cleaned_jobs_data.csv"
swetha_path = "C:/Users/Lenovo/Desktop/CN datasets/2025data.csv"
output_file = 'merged_data.csv'

# Load DataFrames
try:
    df_linkedin = pd.read_csv(linkedin_path)
    df_swetha = pd.read_csv(swetha_path)
except FileNotFoundError as e:
    print(f"Error loading a CSV dataset: {e}")
    exit()

# Standardize job title and skill column names
df_swetha = df_swetha.rename(columns={'Job Title': 'job_title', 'Skills': 'swetha_skills'})
df_linkedin = df_linkedin.rename(columns={'job_skills': 'linkedin_skills'})

# Select relevant columns and standardize job title case
df_swetha_cleaned = df_swetha[['job_title', 'swetha_skills']].copy()
df_linkedin_cleaned = df_linkedin[['job_title', 'linkedin_skills']].copy()

df_swetha_cleaned['job_title'] = df_swetha_cleaned['job_title'].astype(str).str.lower()
df_linkedin_cleaned['job_title'] = df_linkedin_cleaned['job_title'].astype(str).str.lower()

# Merge DataFrames
merged_df = pd.concat([df_swetha_cleaned, df_linkedin_cleaned], ignore_index=True, sort=False)
print(f"Total rows after initial merge: {len(merged_df)}")

# Remove duplicates based on job title, keeping the first occurrence
merged_df.drop_duplicates(subset=['job_title'], keep='first', inplace=True)
print(f"Total rows after deduplication (based on job title): {len(merged_df)}")

# Create a 'skills' column by combining 'swetha_skills' and 'linkedin_skills'
merged_df['skills'] = merged_df['swetha_skills'].fillna('') + ', ' + merged_df['linkedin_skills'].fillna('')
merged_df['skills'] = merged_df['skills'].str.strip(', ').replace(r', , ', ', ', regex=True)

# Drop the temporary skill columns
merged_df.drop(columns=['swetha_skills', 'linkedin_skills'], errors='ignore', inplace=True)

# Define sector inference function
def infer_sector_from_title(title):
    title = str(title).lower()
    if re.search(r'software|engineer|developer|programmer|tech|it|cloud|data science|ai|machine learning|cybersecurity|\.net', title) and not re.search(r'(?<!medical\s)nurse|(?<!home\s)health|rn|lpn|cna|medical assistant|therapist|psychologist', title):
        return 'Technology'
    elif re.search(r'nurse|doctor|health|medical|pharma|biotech|therapist|assistant|rn|lpn|cna|medical assistant|physician|surgeon|psychiatrist|mammography|care manager|hospice|patient|clinician|caregiver', title):
        return 'Healthcare'
    elif re.search(r'clinical psychologist|psychologist', title):
        return 'Healthcare' # Or consider 'Social Services' based on context
    elif re.search(r'finance|bank|investment|analyst|trading|financial|accountant|accounting|tax|teller', title):
        return 'Finance'
    elif re.search(r'market|sales|business development|advertising|pr|marketing|sales|events', title):
        return 'Marketing & Sales'
    elif re.search(r'manufactur|engineer|production|quality|supply chain|mechanical|electrical|civil|welder|fabricator|machinist|qa', title):
        return 'Manufacturing & Engineering'
    elif re.search(r'educat|teacher|professor|training|instruction|lecturer|faculty|instructor|coach|tutor', title):
        return 'Education'
    elif re.search(r'retail|customer service|sales associate|merchandis|store|cashier|clerk|grocery', title):
        return 'Retail & Customer Service'
    elif re.search(r'human resources|hr|talent|recruitment|people', title):
        return 'Human Resources'
    elif re.search(r'legal|law|compliance|attorney|paralegal|counsel', title):
        return 'Legal'
    elif re.search(r'construct|architect|civil|structural|builder', title):
        return 'Construction & Architecture'
    elif re.search(r'research|scientist|laboratory|investigator', title):
        return 'Research & Development'
    elif re.search(r'design|designer|ux|ui|graphic|creative', title):
        return 'Design'
    elif re.search(r'project manager|program manager|agile|scrum', title):
        return 'Project Management'
    elif re.search(r'support|help desk|technician|administrator|operations|office assistant|administrative assistant|secretary|clerical', title):
        return 'IT Support & Operations' # Including admin roles here for now
    elif re.search(r'operations manager|branch manager|superintendent|director', title):
        return 'Management'
    elif re.search(r'restaurant|chef|cook|food|beverage|hospitality|waiter|waitress', title):
        return 'Food & Beverage'
    elif re.search(r'veterinarian|dentist|animal care', title):
        return 'Animal Care'
    elif re.search(r'warehouse|driver|logistics|transportation|supply chain|inventory', title):
        return 'Logistics & Transportation'
    elif re.search(r'social worker|social services|case manager', title):
        return 'Social Services'
    elif re.search(r'volunteer|non-profit|charity|ngo', title):
        return 'Non-profit/Volunteer'
    return 'Other'

# Add sector column
merged_df['Sector'] = merged_df['job_title'].apply(infer_sector_from_title)
print("Sector column added to the merged DataFrame.")

# Save the merged data to 'merged_data.csv'
merged_df.to_csv(output_file, index=False)
print(f"\nMerged data with job_title, skills, and sector (from CSVs only) saved to '{output_file}'")

# --- Further Analysis (Optional) ---
print("\nFirst 5 rows of the merged data:")
print(merged_df.head())

if 'skills' in merged_df.columns:
    print("\nSample of skills from the merged data:")
    print(merged_df['skills'].head(20))
else:
    print("\n'skills' column is still empty or not created as expected. Please check the data loading and merging steps.")