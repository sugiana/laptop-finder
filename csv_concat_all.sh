categories=`ls *.ini | grep -v "-" | awk -F"." '{print $1}'`

~/env/bin/python csv_concat.py $categories
