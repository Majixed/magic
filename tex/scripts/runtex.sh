rm -f ~group/$1.*
rm -rf tex/staging/$1
mkdir tex/staging/$1
cd tex/staging/$1

echo "\\documentclass[preview, border=20pt, 12pt]{standalone}" > $1.tex
echo "\\IfFileExists{eggs.sty}{\\usepackage{eggs}}{}" >> $1.tex

if [ -f "../../preamble/$1.tex" ]; then
    cat ../../preamble/$1.tex >> $1.tex
else
    cat ../../preamble/default/default.tex >> $1.tex
fi

echo "\\\begin{document}" >> $1.tex
cat ../../inputs/$1.tmp >> $1.tex
echo "\n\\end{document}" >> $1.tex

pdflatex -jobname=$1 -no-shell-escape -interaction=nonstopmode $1.tex > ../../log/texout.log

mv $1.pdf ~group
open "shortcuts://run-shortcut?name=pdfpng3&input=$1.pdf"
sleep 1.5
mv ~group/$1.png .
cd ../../..
