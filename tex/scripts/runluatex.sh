uid=$1

rm -f ~group/$uid.*
rm -rf tex/staging/$uid
mkdir tex/staging/$uid
cd tex/staging/$uid

echo "\\documentclass[preview, border=10pt, 12pt]{standalone}" > $uid.tex

if [ -f "../../luapreamble/$uid.tex" ]; then
    cat ../../luapreamble/$uid.tex >> $uid.tex
else
    cat ../../luapreamble/default/default.tex >> $uid.tex
fi

echo "\\\begin{document}" >> $uid.tex
cat ../../inputs/$uid.tmp >> $uid.tex
echo "\n\\end{document}" >> $uid.tex

lualatex -no-shell-escape -interaction=nonstopmode $uid.tex > ../../log/texout.log

if [ -f $uid.pdf ]; then
    mv $uid.pdf ~group
    open "shortcuts://run-shortcut?name=pdfpng3&input=$uid.pdf"
else
    cp ../../failed.png $uid.png
    cd ../../..
    exit 1
fi

until [ -f ~group/$uid.png ]; do
    sleep 0.1
done

mv ~group/$uid.png .

convert -shave 1x1 $uid.png $uid.png

width=`identify -ping -format "%w" $uid.png`
minwidth=1000

if [ $width -lt $minwidth ]; then
    convert -background transparent -extent ${minwidth}x $uid.png $uid.png
fi

cd ../../..
