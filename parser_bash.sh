#!/bin/bash
jar_base="C:\Users\Saos\Desktop\Data_Science\jars\common-jars\parent_jars"
rsf_base="C:/Users/Saos/Desktop/Data_Science/jars/parents_rsf"
fv_base="C:/Users/Saos/Desktop/Data_Science/jars/parents_rsf"
package_prefix="org.apache.hadoop"

for dir in "$jar_base"/*
do
  if [ -d "$dir" ]; then
    dir_name=$(basename "$dir")
    jar_dir="$jar_base/$dir_name"
    rsf_dir="$rsf_base/$dir_name"
    fv_dir="$fv_base/$dir_name"

    for jar_file in "$jar_dir"/*.jar
    do
      base_name=$(basename "$jar_file" .jar)
      rsf_file="$rsf_dir/$base_name.rsf"
      fv_file="$fv_dir/$base_name.fv"
      
      java -jar arcade_core_JavaParser.jar "$jar_file" "$rsf_file" "$fv_file" "$package_prefix"
    done
  fi
done
