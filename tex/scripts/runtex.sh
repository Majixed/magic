#! /bin/sh

uid=$1

rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo "\\documentclass[preview, border=10pt, 12pt]{standalone}\n\\\IfFileExists{eggs.sty}{\\usepackage{eggs}}{}" > $uid.tex

if [ -f "../../preamble/$uid.tex" ]; then
    cat ../../preamble/$uid.tex >> $uid.tex
else
    cat ../../preamble/default/default.tex >> $uid.tex
fi

echo "\n\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo "\n\\\end{document}" >> $uid.tex

timeout 60 pdflatex -no-shell-escape -interaction=nonstopmode -cnf-line 'openin_any=r' $uid.tex > ../../log/texout.log

if [ $? -eq 124 ]; then
    echo "Compilation timed out!" > $uid.error
    cp ../../failed.png $uid.png
    cd ../../..
    exit 1
fi

if [ -f $uid.pdf ]; then
    timeout 60 pdftoppm $uid.pdf $uid -r 600 -png -singlefile

    if [ $? -eq 124 ]; then
        echo "Image conversion timed out!" > $uid.error
        cp ../../failed.png $uid.png
        cd ../../..
        exit 1
    elif [ `stat -c%s $uid.png` -gt 8000000 ]; then
        echo "Output image too large!" > $uid.error
        cp ../../failed.png $uid.png
        cd ../../..
        exit 1
    fi
else
    grep -A 10 "^!" -m 1 $uid.log > $uid.error
    cp ../../failed.png $uid.png
    cd ../../..
    exit 1
fi

if grep -q "^!" $uid.log; then
    grep -A 10 "^!" -m 1 $uid.log > $uid.error
fi

width=`identify -ping -format "%w" $uid.png`
minwidth=1000

convert -shave 1x1 $uid.png $uid.png
# convert -flop $uid.png $uid.png

if [ $width -lt $minwidth ]; then
    timeout 60 convert -background transparent -extent ${minwidth}x $uid.png $uid.png
fi

cd ../../..
