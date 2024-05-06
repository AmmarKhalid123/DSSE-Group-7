# This code is written in Python and uses the PyDriller library to analyze Git repositories. 
# It downloads an Excel file from a URL, reads the file into a pandas DataFrame, 
# gets the list of issue IDs from the DataFrame, and gets the commits for each issue from a local Git repository. 
# The commits are then written to a CSV file.


# Importing necessary libraries
from pydriller import Repository
import pandas as pd
import os
import subprocess
import re
import csv
from tqdm import tqdm
import json
from pydriller.domain.commit import ModificationType

# Defining variables
excel_file_path = r'Issues_assignment1.xlsx'

source_code_url = r'D:\Studies++\hadoop'


######                                     STEP: 01

# Function to get commits for issues
def get_commits_for_issues(issues, repo_url):
  pattern = r'[A-Z]+-\d+'

  issue_commits = {} # Dictionary to store commits for each issue
  for issue in issues: # Loop through each issue
    issue_commits[issue] = []

  # Traverse through each commit in the repository
  for commit in tqdm(Repository(repo_url).traverse_commits()):
    if commit.msg: # If the commit message is not empty
        issue_id = re.search(pattern, commit.msg) # Search for the issue ID in the commit message
        
        if issue_id: # If the issue ID is found
            issue_id = issue_id.group() # Get the issue ID
        else:
            continue

        if issue_id in issues:
            issue_commits[issue_id].append(commit)
  
  return issue_commits # Return the dictionary of commits for each issue

# Function to get a commit from its hash
def get_commit_from_hash(hash, repo_url):
  # Get the commit from the repository and return it
  commit = list(Repository(repo_url, single=hash).traverse_commits())
  return commit[0]

# Read the excel file into a pandas DataFrame
df = pd.read_excel(excel_file_path, 'Group2')

# Get the list of issue IDs from the DataFrame
issue_ids = df['Key'].tolist()

# # Get the commits for each issue
issue_commits = get_commits_for_issues(issue_ids, source_code_url)

# # Writing to json and csv
json_to_write = {}
with open('step1_result.csv', 'w', newline='') as csvfile:
  spamwriter = csv.writer(csvfile, delimiter=',')
  
  # Write the header row to the CSV file
  spamwriter.writerow(['issue_id','commit_hash','commit_msg','parent_hashes'])
  for issue_id, commits in issue_commits.items():
    if (len(commits) > 0):
      json_to_write[issue_id] = []
      for commit in commits:
        json_to_write[issue_id].append({'hash': commit.hash, 'msg': str(commit.msg.encode('utf-8')), 'parents': commit.parents})
        spamwriter.writerow([issue_id, commit.hash, str(commit.msg.encode('utf-8')), '-'.join(commit.parents)])
        
# Serializing json
json_object = json.dumps(json_to_write, indent=4)
 
# Writing to step1_result.json
with open("step1_result.json", "w") as outfile:
    outfile.write(json_object)



#####                             STEP: 02

# json_commits_file = pd.read_json('step1_result.json')
with open("step1_result.json",'r') as f:
    data = json.loads(f.read())
json_commits_file = pd.json_normalize(data)
# Function to compile the Yarn project
def compile_project(hash):
    os.chdir(source_code_url)  # Change directory to the repository path

    try:
        subprocess.run(["git", "checkout", f"{hash}"], shell=True, check=True, cwd=source_code_url)
        print(f"Checked out commit: {hash}")
    except subprocess.CalledProcessError as e:
        print("Error checking out commit:", e)
        return 

    compilation_command = "mvn clean install"  # Example Maven compilation command

    # Execute the compilation command
    try:
        subprocess.run(compilation_command, shell=True, check=True)
        print("JAR file created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error: Failed to create JAR file with exit code", e.returncode)


# Loop through issue-commits dictionary
# for index,row in json_commits_file.iterrows():
# # Compile the Yarn project for each identified commit
#   compile_project(row['commit_hash'])  # Replace repo_path with the actual path to your repository
#   for parent_commit in row['parents']:
#     compile_project(parent_commit)  # Replace repo_path with the actual path to your repository 



#####                        STEP: 03

# Initialize an empty dictionary to store the final results
final_obj = {}

# Loop through each issue and its associated commits
for issue_id, commits in tqdm(issue_commits.items()):
      
  # If there are commits associated with the issue    
  if (len(commits) > 0):
    
    # Initialize an empty list for the issue in the final results dictionary
    final_obj[issue_id] = []
    
    # Loop through each commit
    for commit in tqdm(commits):
      
      # Initialize counters for the types of file changes
      added_files = 0
      modified_files = 0
      deleted_files = 0
      
      # Initialize a dictionary to store the commit's information
      commit_obj = {
        'commit_hash': commit.hash, # The commit's hash
        'dmm_metrics': {            # The commit's DMM metrics
          'dmm_unit_size': commit.dmm_unit_size, # DMM size metrics for the commit
          'dmm_unit_complexity': commit.dmm_unit_complexity, # DMM complexity metrics for the commit
          'dmm_unit_interfacing': commit.dmm_unit_interfacing # DMM interfacing metrics for the commit
        },
        'date': commit.committer_date.isoformat(),
        'parents': [],
        'files': [] # An empty list to store the commit's modified files
      }

      # Loop through each file modified in the commit
      for modified_file in commit.modified_files:
            
        # Initialize a dictionary to store the file's information
        file_obj = {
          'added_lines':modified_file.added_lines, # The number of lines added to the file
          'deleted_lines':modified_file.deleted_lines, # The number of lines deleted from the file
          'added_methods': max(0, len(modified_file.methods) - len(modified_file.methods_before)), # The number of methods added to the file
          'deleted_method': max(0, len(modified_file.methods_before) - len(modified_file.methods)), # The number of methods deleted from the file
          'modified_methods': len(modified_file.changed_methods), # The number of methods modified in the file
          'complexity': modified_file.complexity # The file's complexity
        }
        
        
        # Get the file's new path
        filename = modified_file.new_path
        
        # Check the type of change made to the file and increment the appropriate counter
        if modified_file.change_type == ModificationType.ADD:
          added_files += 1
        elif modified_file.change_type == ModificationType.MODIFY:
          modified_files += 1
        elif modified_file.change_type == ModificationType.DELETE:
          deleted_files += 1
          # If the file was deleted, get the file's old path
          filename = modified_file.old_path
          
        # Add the file's path to the file's information
        file_obj['filename'] = filename
        
        # Add the file's information to the commit's list of modified files
        commit_obj['files'].append(file_obj)

      # Add the counters to the commit's information
      commit_obj['added_files'] = added_files
      commit_obj['modified_files'] = modified_files
      commit_obj['deleted_files'] = deleted_files
      for parent_commit_hash in commit.parents:
        # Initialize counters for the types of file changes
        added_files_parent = 0
        modified_files_parent = 0
        deleted_files_parent = 0
        parent_commit = get_commit_from_hash(parent_commit_hash, source_code_url)
        # Initialize a dictionary to store the commit's information
        commit_obj_parent = {
          'commit_hash': parent_commit.hash, # The commit's hash
          'dmm_metrics': {            # The commit's DMM metrics
            'dmm_unit_size': parent_commit.dmm_unit_size, # DMM size metrics for the commit
            'dmm_unit_complexity': parent_commit.dmm_unit_complexity, # DMM complexity metrics for the commit
            'dmm_unit_interfacing': parent_commit.dmm_unit_interfacing # DMM interfacing metrics for the commit
          },
          'date': parent_commit.committer_date.isoformat(),
          'files': [] # An empty list to store the commit's modified files
        }

        # Loop through each file modified in the commit
        for modified_file_parent in parent_commit.modified_files:
              
          # Initialize a dictionary to store the file's information
          file_obj_parent = {
            'added_lines':modified_file_parent.added_lines, # The number of lines added to the file
            'deleted_lines':modified_file_parent.deleted_lines, # The number of lines deleted from the file
            'added_methods': max(0, len(modified_file_parent.methods) - len(modified_file_parent.methods_before)), # The number of methods added to the file
            'deleted_method': max(0, len(modified_file_parent.methods_before) - len(modified_file_parent.methods)), # The number of methods deleted from the file
            'modified_methods': len(modified_file_parent.changed_methods), # The number of methods modified in the file
            'complexity': modified_file_parent.complexity # The file's complexity
          }
          
          
          # Get the file's new path
          filename_parent = modified_file_parent.new_path
          
          # Check the type of change made to the file and increment the appropriate counter
          if modified_file_parent.change_type == ModificationType.ADD:
            added_files_parent += 1
          elif modified_file_parent.change_type == ModificationType.MODIFY:
            modified_files_parent += 1
          elif modified_file_parent.change_type == ModificationType.DELETE:
            deleted_files_parent += 1
            # If the file was deleted, get the file's old path
            filename_parent = modified_file_parent.old_path
            
          # Add the file's path to the file's information
          file_obj['filename'] = filename_parent
          
          # Add the file's information to the commit's list of modified files
          commit_obj_parent['files'].append(file_obj_parent)

        # Add the counters to the commit's information
        commit_obj_parent['added_files'] = added_files_parent
        commit_obj_parent['modified_files'] = modified_files_parent
        commit_obj_parent['deleted_files'] = deleted_files_parent
        commit_obj['parents'].append(commit_obj_parent)
      # Add the commit's information to the issue's list of commits in the final results
      final_obj[issue_id].append(commit_obj)
      
# Convert the final results to a JSON string with indentation      
json_object = json.dumps(final_obj, indent=4)

# Write the JSON string to a file
with open("step3_result.json", "w") as outfile:
    outfile.write(json_object)