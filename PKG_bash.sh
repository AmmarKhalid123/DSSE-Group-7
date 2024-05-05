#!/bin/bash
rsf_base="C:\Users\Saos\Desktop\Data_Science\jars\parents_rsf"
pkg_base="C:\Users\Saos\Desktop\Data_Science\jars\parents_pkg"
project_name="hadoop"
language="java"
file_level="false"

for dir in "$rsf_base"/*
do
  if [ -d "$dir" ]; then
    dir_name=$(basename "$dir")
    rsf_dir="$rsf_base/$dir_name"
    project_path="$pkg_base/$dir_name"

    for rsf_file in "$rsf_dir"/*.rsf
    do
      base_name=$(basename "$rsf_file" .rsf)
      project_version="$base_name"
      
      java -jar arcade_core-Pkg.jar depspath="$rsf_file" projectpath="$project_path" projectname="$project_name" projectversion="$project_version" language="$language" filelevel="$file_level"
    done
  fi
done