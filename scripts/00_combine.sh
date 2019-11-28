pushd ..
python3 05_combine.py --inList d1l1.txt --output d1l1.csv.gz --minGap 0.001 &
python3 05_combine.py --inList d1l2.txt --output d1l2.csv.gz --minGap 0.001 &
python3 05_combine.py --inList d2l1.txt --output d2l1.csv.gz --minGap 0.001 &
popd
