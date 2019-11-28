inPath = $1
outPath = $2

for i in $(find inPath -maxDepth 1 -name '*day1_loc1*');
do
    voxDecimate    
done
