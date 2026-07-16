#!/bin/bash

# This script allows you to download a set of Climate DT surface variables
# that can be used to force ocean models.
#
# This is done by creating a batch job for each year that then calls a python
# routine that downloads the data into monthly files
#
for year in {2040..2049}
do
((i++))
echo $year
cat <<EOF > job_$i.sh
#!/bin/bash
#SBATCH --account=project_2010748
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=20G
#SBATCH --partition=small
#SBATCH --cpus-per-task=1
#SBATCH --gres=nvme:100
#SBATCH --job-name=ClimateDT

export PATH="/projappl/project_2010748/DTO4OWE/earthkit/bin:$PATH"
cd /projappl/project_2010748/DTO4OWE/extract_forcing/

python extract_forcing.py $year
EOF
sbatch job_$i.sh
done
