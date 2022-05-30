uid=$1

rm -f ~group/$uid.*
rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo "\\documentclass[preview, border=20pt, 12pt]{standalone}" > $uid.tex

if [ -f "../../preamble/$uid.tex" ]; then
    cat ../../preamble/$uid.tex >> $uid.tex
else
    cat ../../preamble/default/default.tex >> $uid.tex
fi

echo "\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo "\n\\end{document}" >> $uid.tex

pdflatex -no-shell-escape -interaction=nonstopmode $uid.tex > ../../log/texout.log

if [ -f $uid.pdf ]; then
    mv $uid.pdf ~group
    open "shortcuts://run-shortcut?name=pdfpng3&input=$uid.pdf"
    sleep 1.5
    if [ -f ~group/$uid.png ]; then
        mv ~group/$uid.png .
    else
        cp ../../failed.png $uid.png
    fi
else
    cp ../../failed.png $uid.png
fi

cd ../../..
