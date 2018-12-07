# This script recives input file in the format 'word context-word'
# a number of minimal couple appearence
# an output file path
# outputs a file to the given path in the format 'word context-word amount-of-times'
INPUT_FILE=$1
MIN_COUPLE_C=$2
OUTPUT_FILE=$3
export LC_ALL=C
cat $INPUT_FILE | sort | uniq -c | awk -v a=$MIN_COUPLE_C '{if ($1 > a) {print $2 " " $3 " " $1}}'  |sort  > $OUTPUT_FILE
