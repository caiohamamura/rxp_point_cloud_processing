These scripts were used for pre processing RIEGL point cloud data to binary file format that can be read by Steven Hancock LiDAR processing toolset.

# 1.	Requirements

For this task we used the [readRXP](https://bitbucket.org/StevenHancock/rxptobinary) CLI utility from StevenHancock bitbucket repository, so you need to have this compiled at a visible path in the machine. This utility will use the RXP point clouds and a 4x4 transformation matrix from another file, transforming the RXP to a binary format other tools can easily read. 
First thing we need to do is to download processing scripts from my repository:
https://github.com/caiohamamura/rxp_point_cloud_processing.git

Use:

`git clone https://github.com/caiohamamura/rxp_point_cloud_processing.git`

# 2.	Constructing the relationship between RXP files and corresponding DAT transformation matrix

Now you will use the scripts you’ve just cloned from my repository. The first one you’ll use is 01_build_transforms_scans_relationship.py. The usage is:

`python3 01_build_transforms_scans_relationship.py <RIEGL_RXP_and_DAT_matrices_path> <output_csv>`

Where `<RIEGL_RXP_and_DAT_matrices_path>` is the path where RIEGL RXP and DAT matrices are, and `<output_csv>` , is the name of the output csv which will have the information of which RXP file links to which DAT file. The RXP and DAT files can be at any depth inside the specified path and the files should have a Plot_N pattern somewhere either in folder name or the file name itself and BaseNames from DAT and RXP should match but don’t need to be in the same directory. The data as it was by 23/10/2019 was working fine.
This will output a csv file which contains data informing the relationship between RXP and DAT files.

# 3.	Processing RXP point clouds

Now, the next script will use the output csv file from the previous step to build up the BIN point cloud files. It will use multiprocessing from Python to produce the files in parallel to optimize efficiency (NOTE: as the point clouds themselves are being read from the disk, the disk read speed may also, and most likely, limit the processing speed, so it won’t be linearly faster to use many parallel processes).
The usage for this script is:

`python3 02_binarize.py <number_of_cores> <output_path> <csv_file>`

Where `<number_of_cores>` is actually the number of parallel processes will be launched for processing the files. `<output_path>` should be an existing directory where the BIN files will output (they will all output in the same directory, no further structure will be created). `<csv_file>` is the output csv file from the previous script.
