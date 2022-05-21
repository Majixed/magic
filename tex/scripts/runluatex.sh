uid=$1

rm -f ~group/$uid.*
rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo "\\documentclass[preview, border=20pt, 12pt]{standalone}" > $uid.tex
echo "\\IfFileExists{eggs.sty}{\\usepackage{eggs}}{}" >> $uid.tex

if [ -f "../../luapreamble/$uid.tex" ]; then
    cat ../../luapreamble/$uid.tex >> $uid.tex
else
    cat ../../luapreamble/default/default.tex >> $uid.tex
fi

echo "\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo "\n\\end{document}" >> $uid.tex

lualatex -no-shell-escape -interaction=nonstopmode $uid.tex > ../../log/texout.log

mv $uid.pdf ~group
open "shortcuts://run-shortcut?name=pdfpng3&input=$uid.pdf"
sleep 1.5
mv ~group/$uid.png .
cd ../../..