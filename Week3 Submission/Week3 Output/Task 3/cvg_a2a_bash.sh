#!/bin/bash

# Directories containing the .rsf files
child_dir=""
parent_dir=""

# Paths to the .jar files
arcade_core_A2a=""
arcade_core_Cvg=""

# Output file
output_text_file="cvg_a2a_WCA_UEMNM.txt"

# Error file
error_file="errors.txt"

# CSV file
csv_file="hashes.csv"

# CSV output file
csv_output_file="cvg_a2a_WCA_UEMNM.csv"

# Create a new CSV file and write the header
echo "Parent Hash,Child Hash,Coverage Number" > "$csv_output_file"

# Process each subdirectory in the child directory
for child_subdir in "$child_dir"/*; do

  echo "Processing child directory $child_subdir"
  # Get the name of the subdirectory (commit hash)
  commit_hash=$(basename "$child_subdir")

  # Find the corresponding parent hash
  parent_hash=$(awk -F, -v hash="$commit_hash" '$1 == hash {print $2}' "$csv_file")

  echo "Parent hash: $parent_hash"  # Debugging line

  # Find the corresponding parent subdirectory
  parent_subdir="$parent_dir/$parent_hash"

  echo "Parent subdir: $parent_subdir"  # Debugging line

  # Check if the parent subdirectory exists
  if [[ -d "$parent_subdir" ]]; then

    # Process each .rsf file in the child subdirectory
    for child_file in "$child_subdir"/*.rsf; do
      echo "Processing child file $child_file"  # Debugging line

      # Get the base name of the child file
      base_name=$(basename "$child_file")

      # Find the corresponding parent file
      parent_file="$parent_subdir/$base_name"

      # Check if the parent file exists
      if [[ -f "$parent_file" ]]; then

        # Run arcade_core_a2a.jar on the child and parent files
        echo "Running arcade_core_A2a.jar..."  # Debugging line
        output_a2a=$(java -jar "$arcade_core_A2a" "$parent_file" "$child_file" 2>> "$error_file" | tail -n 1)
        echo "Finished running arcade_core_A2a.jar"  # Debugging line

        # Run arcade_core_cvg.jar on the child and parent files
        echo "Running arcade_core_cvg.jar..."  # Debugging line
        output_cvg=$(java -jar "$arcade_core_Cvg" "$child_file" "$parent_file" 2>> "$error_file")
        echo "Finished running arcade_core_cvg.jar"  # Debugging line

        # Write the output to the CSV file
        echo "$parent_hash,$commit_hash,\"$output_a2a\",\"$output_cvg1\",\"$output_cvg2\"" >> "$csv_output_file"
        echo "Writing to CSV file: $parent_hash,$commit_hash,\"$output_a2a\",\"$output_cvg\""  # Debugging line
        echo "$parent_hash,$commit_hash,\"$output_a2a\",\"$output_cvg\"" >> "$output_text_file"

      else
        echo "Parent file $parent_file does not exist"  # Debugging line
      fi

    done

  else
    echo "Parent directory $parent_subdir does not exist"  # Debugging line
  fi

done