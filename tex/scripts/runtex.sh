uid=$1

rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo "\\documentclass[preview, border=10pt, 12pt]{standalone}" > $uid.tex

if [ -f "../../preamble/$uid.tex" ]; then
    cat ../../preamble/$uid.tex >> $uid.tex
else
    cat ../../preamble/default/default.tex >> $uid.tex
fi

echo -e "\n\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo -e "\n\\\end{document}" >> $uid.tex

timeout 15 pdflatex -no-shell-escape -interaction=nonstopmode $uid.tex > ../../log/texout.log

if [ $? -eq 124 ]; then
    echo "Compilation timed out!"
    cp ../../failed.png $uid.png
    cd ../../..
    exit 1
fi

if [ -f $uid.pdf ]; then
    timeout 15 pdftoppm $uid.pdf tmp -r 600 -png && mv tmp-1.png $uid.png

    if [ $? -eq 124 ]; then
        echo "Image conversion timed out!"
        cp ../../failed.png $uid.png
        cd ../../..
        exit 1
    fi
else
    cp ../../failed.png $uid.png
    cd ../../..
    exit 1
fi

width=`identify -ping -format "%w" $uid.png`
minwidth=1000

if [ $width -lt $minwidth ]; then
    convert -background transparent -extent ${minwidth}x $uid.png $uid.png
fi

cd ../../..
