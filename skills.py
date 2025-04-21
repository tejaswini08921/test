import pandas as pd

def find_jobs_by_skill(skills_input, data_path='merged_data.csv'):
    try:
        merged_data = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Could not find data file at: {data_path}")
        return []

    if 'skills' not in merged_data.columns:
        print("Error: 'skills' column not found in the data.")
        return []

    search_skills = [skill.lower().strip() for skill in skills_input.split(',')]
    
    matching_jobs = set()
    for skill in search_skills:
        jobs_with_skill = merged_data[merged_data['skills'].str.lower().str.contains(skill, na=False)]

        matching_jobs.update(jobs_with_skill['job_title'].unique())

    return sorted(list(matching_jobs))

if __name__ == '__main__':
    data_path = 'merged_data.csv'  

    while True:
        user_skills_input = input("Enter one or more skills (comma-separated) to find related jobs (or 'exit' to quit): ")
        if user_skills_input.lower() == 'exit':
            break

        related_jobs = find_jobs_by_skill(user_skills_input)

        if related_jobs:
            print(f"\nJobs mentioning any of the skills: '{user_skills_input}':")
            for job in related_jobs:
                print(f"- {job}")
        else:
            print(f"\nNo jobs found mentioning any of the skills: '{user_skills_input}'.")
        print("\n")
