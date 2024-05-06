import os
import subprocess

#Settings the required file paths for input folder path of files,output folder path and path of the jar file of ACDC
acdc_jar_path = 'F:\\Final\\same\\arcade_core-ACDC.jar'   #Path of ACDC  jar file
root_direc = 'F:\\Final\\same\\INPUT\\parents_rsf'                        #Root directory for RSF files
output_root = 'D:\\parents ACDC'             #Output root directory where you want to store the files post processing

def lst_folders(root_dir):
    folder_lst = []
    for root, dirs, _ in os.walk(root_dir):
        for dir in dirs:
            folder_lst.append(os.path.join(root, dir))
    return folder_lst

# Get all subfolders within the root directory
folders = lst_folders(root_direc)

#Loop through each folder one by one and get only the .rsf files required for ACDC clustering
for folder in folders:
    print(f"Processing files in folder: {folder}")
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".rsf"):
                inpt_file = os.path.join(root, file)
                
                # Create the corresponding output folder structure in the output directory
                otput_folder = root.replace(root_direc, output_root)  
                os.makedirs(otput_folder, exist_ok=True)
                
                # Set the naming convention of  adding "_ACDC" to the input filename
                final_filename = file.replace(".rsf", "_ACDC.rsf")
                otpt_file = os.path.join(otput_folder,final_filename)
                
                # Check if the output file already exists, if not, proceed with processing
                if not os.path.exists(otpt_file):
                    # Main code for ACDC implementation including acdc jar path, input file path, and output file path
                    subprocess.run(["java", "-jar", acdc_jar_path, inpt_file, otpt_file])

print("Processing of ACDC algorithm finished")
