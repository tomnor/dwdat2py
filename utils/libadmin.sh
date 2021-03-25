#! /usr/bin/env bash

# usage: libadmin.sh DEWEZIP

# Unzip DEWEZIP to the working directory (root of this project)

# want to check:

# . is there any difference between the duplicates of respective .dll
#   or .so blob. If so what blobs differ?

# . is there any difference between the respective blob in given zip
#   with the blobs in this repo?

# . difference between the doc in zip to worktree (implies producing a
#   text version of the doc.)

# make a temporary directory in the working directory with
# sub-directories dll-<n>, dll64-<n>, so-<n> and so64-<n>, in which
# respective blob resides. n range from 0 to N-1 where N is the number
# of copies of each blob.

# append the output of diffing all copies against the 0-version of the
# copy into a file in tempdir called libsummary. Also append the
# result of diffing the 0-version with the versions in this worktree.

BLOBS="DWDataReaderLib64.dll DWDataReaderLib.dll DWDataReaderLib64.so DWDataReaderLib.so"
tmpdir=TMP_DEWELIBDIR
summaryfile=libsummary
docdiff=documentation.diff
headerdiff=header.diff

cnt=0
OIFS="$IFS"

unzipped=$(basename $1 .zip)
unzip -q -d $unzipped $1

# copy the blobs into a directory structure in the working directory
mkdir $tmpdir
for blob in $BLOBS; do
    cnt=0
    echo "-- $blob --" >> $tmpdir/$summaryfile
    IFS=$'\n'
    for result in $(find $unzipped -name $blob) ; do
        echo $cnt $result >> $tmpdir/$summaryfile
        subdir=$(echo $result | grep -o -P 'Lib[0-9]*\..{2,3}$')-$cnt
        mkdir $tmpdir/$subdir
        cp "$result" $tmpdir/$subdir
        cnt=$((cnt+1))
    done
    IFS="$OIFS"
done

# find and convert the documentation to text
doc=$(find $unzipped -name '*.doc')
antiword -w 90 "$doc" > $tmpdir/$(basename $doc).txt

# find and copy the py header file
doc=$(find $unzipped -name DWDataReaderHeader.py)
cp "$doc" $tmpdir

echo -e "\nDIFFS ON INTERNAL COPIES" >> $tmpdir/$summaryfile
DIRSTEMS="Lib64.dll- Lib.dll- Lib64.so- Lib.so-"
for stem in $DIRSTEMS ; do
    echo -e "\n-- $stem --" >> $tmpdir/$summaryfile
    ext=$(echo $stem | grep -o -P "(dll|so)")
    diff -u -s --from-file $tmpdir/$stem"0"/*.$ext \
         $tmpdir/$stem[1-9]/*.$ext >> $tmpdir/$summaryfile
done

treelibdir=dwdat2py/libs
echo -e "\nDIFFS TO WORKTREE" >> $tmpdir/$summaryfile
DIRSTEMS="Lib64.dll- Lib.dll- Lib64.so- Lib.so-"
for stem in $DIRSTEMS ; do
    echo -e "\n-- $stem --" >> $tmpdir/$summaryfile
    predot=$(echo $stem | grep -o -P "Lib(64)?")
    ext=$(echo $stem | grep -o -P "(dll|so)")
    diff -u -s $treelibdir/*$predot.$ext \
         $tmpdir/$stem"0"/*$predot.$ext >> $tmpdir/$summaryfile
done

echo -e "\nDIFF FROM WORKTREE DOC\n" >> $tmpdir/$summaryfile
echo -e "See $docdiff" >> $tmpdir/$summaryfile
diff -us $treelibdir/*doc.txt $tmpdir/*doc.txt > $tmpdir/$docdiff

echo -e "\nDIFF FROM WORKTREE PY HEADER\n" >> $tmpdir/$summaryfile
echo -e "See $headerdiff" >> $tmpdir/$summaryfile
diff -us dwdat2py/DWDataReaderHeader.py $tmpdir/DWDataReaderHeader.py > $tmpdir/$headerdiff

echo "See $tmpdir/$summaryfile for diffs"
