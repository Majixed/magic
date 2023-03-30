uid=$1

rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo -e "\\documentclass[preview, border=10pt, 12pt]{standalone}\n\\\IfFileExists{eggs.sty}{\\usepackage{eggs}}{}" > $uid.tex

if [ -f "../../luapreamble/$uid.tex" ]; then
    cat ../../luapreamble/$uid.tex >> $uid.tex
else
    cat ../../luapreamble/default/default.tex >> $uid.tex
fi

echo -e "\n\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo -e "\n\\\end{document}" >> $uid.tex

timeout 60 lualatex -no-shell-escape -interaction=nonstopmode -cnf-line 'openin_any=r' $uid.tex > ../../log/texout.log

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

if [ $width -lt $minwidth ]; then
    convert -background transparent -extent ${minwidth}x $uid.png $uid.png
fi

cd ../../..
