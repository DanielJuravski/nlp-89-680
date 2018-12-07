#! /bin/bash
feature_vecs_file=$PWD/$1
model_file=$PWD/$2

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"

java -cp liblinear*.jar de.bwaldvogel.liblinear.Train -s 0 -c 0.25 $feature_vecs_file $model_file
