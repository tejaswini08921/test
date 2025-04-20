import pandas as pd
from collections import Counter

def get_demanding_data_by_sector(sector, data_path='merged_data.csv', top_n=10):
    """
    Analyzes job data to find the most demanding jobs and skills within a specific sector.

    Args:
        sector (str): The sector to filter by (case-insensitive).
        data_path (str): Path to the CSV file containing job data.
        top_n (int): The number of top demanding jobs and skills to return.

    Returns:
        tuple: A tuple containing two dictionaries:
            - top_demanding_jobs: Dictionary of top N job titles and their frequencies.
            - top_demanding_skills: Dictionary of top N skills and their frequencies.
    """
    try:
        merged_data = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Could not find data file at: {data_path}")
        return {}, {}

    sector_data = merged_data[merged_data['Sector'].str.lower() == sector.lower()]

    if sector_data.empty:
        print(f"No job postings found for the sector: {sector}")
        return {}, {}

    job_title_counts = sector_data['job_title'].value_counts().head(top_n).to_dict()

    all_skills = []
    for skills_list in sector_data['skills'].dropna():
        if isinstance(skills_list, str):
            all_skills.extend([skill.strip().lower() for skill in skills_list.split(',')])
        elif isinstance(skills_list, list):
            all_skills.extend([skill.strip().lower() for skill in skills_list])

    skill_counts = Counter(all_skills).most_common(top_n)
    top_demanding_skills = dict(skill_counts)

    return job_title_counts, top_demanding_skills

if __name__ == '__main__':
    data_path = 'merged_data.csv'  # Assuming merged_data.csv is in the same directory
    try:
        merged_df = pd.read_csv(data_path)
        unique_sectors = sorted(merged_df['Sector'].unique())
        print("Available Sectors:")
        for sector in unique_sectors:
            print(f"- {sector}")
        print("\n")

        while True:
            user_sector = input("Enter the sector to analyze (or 'exit' to quit): ")
            if user_sector.lower() == 'exit':
                break

            top_jobs_in_sector, top_skills_in_sector = get_demanding_data_by_sector(user_sector)

            print(f"\nTop Demanding Jobs in {user_sector}:")
            if top_jobs_in_sector:
                for job, count in top_jobs_in_sector.items():
                    print(f"- {job}: {count}")
            else:
                print(f"No demanding jobs found in the sector: {user_sector}")

            print(f"\nTop Demanding Skills in {user_sector}:")
            if top_skills_in_sector:
                for skill, count in top_skills_in_sector.items():
                    print(f"- {skill}: {count}")
            else:
                print(f"No demanding skills found in the sector: {user_sector}")
            print("\n")

    except FileNotFoundError:
        print(f"Error: Could not find data file at: {data_path}. Please ensure 'merged_data.csv' is in the correct location.")