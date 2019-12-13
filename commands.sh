for i in $(ls d1l*.txt);
    do 
    filename=$(basename -- "$i");
    filename="${filename%.*}";
    echo "python3 05_combine.py --inList \"$i\" --output \"multivoxel/$filename.tar.gz\" --minGap 0.0001" >> commands;
done


ls d1l*.txt | parallel 'filename=$(basename -- "{}");filename="${filename%.*}";python3 05_combine.py --inList "{}" --output "multivoxel/$filename.tar.gz" --minGap 0.0001;'


ls multi_voxel/d1l1* | parallel 'filename="{}";filename2="${filename/d1l1/d1l2}";python3 06_diff_combines.py "{}" "$filename2"'

ssh burn
pushd myspace/python
ls multi_voxel/diff* | parallel 'filename=$(basename -- "{}");filename="${filename%.*}";regex="([0-9\.]*)$";if [[ $filename =~ $regex ]] ; then res=${BASH_REMATCH[1]}; fi;python3 09_analysis_mean_bias_rmse.py {} -m "plots/${filename}.mean.png" -r "plots/${filename}.rmse.png" -v $res'


ls multi_voxel/diff* | parallel 'filename=$(basename -- "{}");filename="${filename%.*}";regex="([0-9\.]*)\.tar$";if [[ $filename =~ $regex ]] ; then res=${BASH_REMATCH[1]}; fi;python3 10_analysis_histogram.py {} -H "plots/${filename}.hist.png" -v $res'