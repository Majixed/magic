% TeXit Standard Class

\NeedsTeXFormat{LaTeX2e}
\def\texit@version{1.2-rc4}
\ProvidesClass{texit}[2025-08-05 TeXit Standard Class v\texit@version]



\DeclareKeys[texit]{
	bgcolor.tl_gset_e:N           = \texit@bgcolor,
	bggradient.tl_gset_e:N        = \texit@bggradient,
	bggradientangle.tl_gset_e:N   = \texit@bggradientangle,
	textcolor.tl_gset_e:N         = \texit@textcolor,
	textgradient.tl_gset_e:N      = \texit@textgradient,
	textgradientangle.tl_gset_e:N = \texit@textgradientangle,
	minpagewidth.tl_gset_e:N      = \texit@minpagewidth,
	border.tl_gset_e:N            = \texit@border@,
% Options for article.cls
	draft.code  = \PassOptionsToClass{\CurrentOption}{article}, draft.usage = load,
	leqno.code  = \PassOptionsToClass{\CurrentOption}{article}, leqno.usage = load,
	fleqn.code  = \PassOptionsToClass{\CurrentOption}{article}, fleqn.usage = load,
	12pt.code   = \PassOptionsToClass{\CurrentOption}{article}, 12pt.usage  = load,
	11pt.code   = \PassOptionsToClass{\CurrentOption}{article}, 11pt.usage  = load,
	10pt.code   = \PassOptionsToClass{\CurrentOption}{article}, 10pt.usage  = load
}
\ProcessKeyOptions[texit]
\protected\def\texitset{\SetKeys[texit]}

\LoadClass{article}

\RequirePackage{ifluatex}

\def\texit@engine{pdfTeX}

\ifluatex
  \RequirePackage{luatex85}
  \RequirePackage{pdftexcmds}
  \let\pdfstrcmp=\pdf@strcmp
  \def\texit@engine{LuaTeX}
  \let\texit@engineversion=\luatexversion
  \let\texit@enginerevision=\luatexrevision
\else
  \let\texit@engineversion=\pdftexversion
  \let\texit@enginerevision=\pdftexrevision
\fi

\parindent=0pt

\textwidth=345pt

\textheight=\maxdimen



% Parameters

\newif\iftexit@bggradient
\newif\iftexit@textgradient
\newdimen\texit@border

\protected\def\texit@processgradients{%
	\ifx\texit@bggradient\empty
		\texit@bggradientfalse
	\else
		\texit@bggradienttrue
		\ifx\texit@bggradientangle\empty
			\def\texit@bggradientangle{0}%
		\fi
	\fi
	\ifx\texit@textgradient\empty
		\texit@textgradientfalse
	\else
		\texit@textgradienttrue
		\ifx\texit@textgradientangle\empty
			\def\texit@textgradientangle{0}%
		\fi
	\fi
}
\protected\def\texit@processborder{%
	% Border width function
	% (default: max(5, min(15, d/24 - 5))pt where d = max(ht255+dp255, wd255))
	\ifx\texit@border@\empty
		\protected\def\texit@border@calc##1{%
			\texit@border=\dimexpr\ht##1+\dp##1\relax
			\ifdim\wd##1>\texit@border \texit@border=\wd##1\fi
			\texit@border=\dimexpr\texit@border/24-5\p@ \relax
			\ifdim\texit@border<5\p@ \texit@border=5\p@ \fi
			\ifdim\texit@border>15\p@ \texit@border=15\p@ \fi
		}%
	\else
		\protected\edef\texit@border@calc##1{\texit@border=\the\dimexpr\texit@border@\relax\relax}%
	\fi
}

\AtBeginDocument{
	% Background color given in hex or "trans" (fallback: white)
	\ifx\texit@bgcolor\empty
		\def\texit@bgcolor{ffffff}
	\fi
	% Global text color given in hex (fallback: black)
	\ifx\texit@textcolor\empty
		\def\texit@textcolor{000000}
	\fi
	\texit@processgradients
	\texit@processborder
	% Whether to fix the page width (fallback: false) and minimum width of physical page (if alwayswide is false)
	\ifx\texit@minpagewidth\empty
		\def\texit@minpagewidth{\z@}
	\fi
}
\AtEndDocument{
	\texit@processgradients
	\texit@processborder
}

% Parameter that controls greediness of horizontal cropping (lower = more greedy, must be between 1 and 10000)
\mathchardef\texit@realwd@minhbadness=1000

% Debug
\newif\iftexit@debug
\font\texit@debugfont=phvr7t at 2.5pt
\font\texit@debugfontbold=phvb7t at 2.5pt



% Output Routine

\ifcsname tex_shipout:D\endcsname
	\expandafter\let\expandafter\texit@shipout@\csname tex_shipout:D\endcsname
\else
	\let\texit@shipout@=\shipout
\fi

% Holds final output page
\newbox\texit@pagebox

% Debug overlay
\newbox\texit@debug@pagebox
\newbox\texit@debug@gradientbox
\newtoks\texit@debug@boxes

\newtoks\texit@headline
\newtoks\texit@footline

\newdimen\texit@pagebox@realwd

\newdimen\texit@boxcclv@realwd
\newdimen\texit@footins@realwd

% Marker for OTR to discard the current page
\newcount\texit@discardpage \texit@discardpage=-"7FFF

% Marker for top of vlist
\mathchardef\texit@realwd@marker="7FFE

% Generic marker to force retention of full width
\mathchardef\texit@realwd@blocker="7FFD

% Marker for display equations
\mathchardef\texit@realwd@postdisplaypenalty="7FFC

% If previous box was a display equation
\newif\iftexit@realwd@isdisplay

\AddToHook{begindocument/end}{
	\null \vfil \penalty\texit@discardpage
	\texit@setdocumentcolor
	\topskip=0pt
	\postdisplaypenalty=\texit@realwd@postdisplaypenalty
	\null \nointerlineskip \penalty\texit@realwd@marker
	\vskip-\parskip
}
\AddToHook{enddocument}{
	\def\clearpage{\penalty-\@MM}
}

% Only a penalty of -20000 may trigger output
\output={%
	\ifnum\outputpenalty=-\@MM
		\let\par=\@@par
		\texit@shipout
		\global\output={\deadoutput}%
	\else
		\ifnum\outputpenalty=\texit@discardpage
			\setbox\texit@pagebox=\box\@cclv
		\else
			\unvbox\@cclv
		\fi
	\fi
}
\protected\def\deadoutput{\setbox\texit@pagebox=\box\@cclv}

\protected\def\texit@shipout{%
	\texit@shipout@setrealwd
	\setbox\texit@pagebox=\vbox{%
		\iftexit@textgradient
			\pdfliteral{1 g 1 G}%
		\else
			\texit@htmltorgb\texit@textcolor
			\pdfliteral{\texit@temp rg \texit@temp RG}%
		\fi
		\unvbox\@cclv
		\ifvoid\footins \else
			\vskip \skip\footins
			\footnoterule
			\unvbox\footins
		\fi
	}%
	\wd\texit@pagebox=\texit@pagebox@realwd
	\texit@border@calc\texit@pagebox
%
	\voffset=-1in
	\hoffset=\voffset
	\pdfpageheight=\dimexpr\ht\texit@pagebox+\dp\texit@pagebox+2\texit@border \relax
	\pdfpagewidth=\dimexpr\texit@pagebox@realwd+2\texit@border \relax
	\ifdim\pdfpagewidth<\texit@minpagewidth
		\pdfpagewidth=\texit@minpagewidth
	\fi
	\set@display@protect
	\texit@shipout@\vbox to\pdfpageheight{%
		\texit@paintbg
		\nointerlineskip \vbox to\z@{\the\texit@headline \vss}%
		\kern\texit@border 
		\nointerlineskip \moveright\texit@border \vbox to\z@{%
			\iftexit@textgradient
				\texit@gradient@parse\texit@textgradient
				\def\texit@debug@node@color{1 1 0}%
				\texit@gradientbox\texit@pagebox\texit@textgradientangle
				% On top of existing debug overlay
				\global\setbox\texit@debug@pagebox=\vbox{%
					\vbox to\z@{\box\texit@debug@pagebox \vss}%
					\unvbox\texit@debug@gradientbox
				}%
			\else
				\box\texit@pagebox
			\fi
			\vss
		}%
		\iftexit@debug
			\kern-\ht\texit@pagebox
			\kern-\dp\texit@pagebox
			\nointerlineskip \moveright\texit@border \vbox to\z@{\box\texit@debug@pagebox \vss}%
		\fi
		\vfil
		\nointerlineskip \vbox to\z@{\vss \the\texit@footline}%
		\iftexit@debug \texit@debug@footline \fi
	}%
}

\protected\def\texit@shipout@setrealwd{%
	\texit@realwd\@cclv\texit@boxcclv@realwd
	\edef\@tempa{\the\texit@debug@boxes}%
	\texit@pagebox@realwd=\texit@boxcclv@realwd
	\ifvoid\footins \else
		\texit@realwd\footins\texit@footins@realwd
		\edef\@tempb{\the\texit@debug@boxes}%
		\ifdim\texit@footins@realwd>\texit@pagebox@realwd
			\texit@pagebox@realwd=\texit@footins@realwd
		\fi
		% Width of the footnoterule
		\ifdim\texit@pagebox@realwd<\footnoterulewd
			\texit@pagebox@realwd=\footnoterulewd
		\fi
	\fi
	\iftexit@debug
		\setbox\texit@debug@pagebox=\vbox{%
			\setbox\z@=\vbox{\unvcopy\@cclv}%
			\wd\z@=\texit@boxcclv@realwd
			\texit@debug@draw@page\z@\@tempa{box255}%
			\ifvoid\footins \else
				\kern\ht\z@ \kern\dp\z@
				\vskip \skip\footins
				\vskip \footnoteruleht
				\setbox\z@=\vbox{\unvcopy\footins}%
				\wd\z@=\texit@footins@realwd
				\texit@debug@draw@page\z@\@tempb{footins}%
			\fi
		}%
	\fi
}

% Compute real width of #1 and store in #2 (\global)
% A more robust algorithm is available in LuaTeX; see https://tex.stackexchange.com/q/734916/
\protected\def\texit@realwd#1#2{%
	#2=\wd#1%
	\ifdim#2>\hsize #2=\hsize \fi
	\dimen@=\z@
	\texit@debug@boxes={}%
	\setbox\z@=\vbox{%
		\hbadness=\@M
		\penalty\texit@realwd@marker
		\unvcopy#1%
		\def\next{\texit@realwd@sift#2}\next
	}%
}

\def\texit@realwd@sift#1{%
	\texit@realwd@isdisplayfalse
	\texit@realwd@sift@superunskip
	\setbox\z@=\lastbox
	\ifvoid\z@
		\ifnum\lastpenalty=\texit@realwd@marker
			\ifnum\dimen@<#1%
				\texit@realwd@sift@end{#1}%
			\fi
		\fi
		\let\next\relax
	\else
		\iftexit@realwd@isdisplay
			\let\next=\relax
			\iftexit@debug \texit@debug@draw@box{1 0 0}{1 0 0 1 \strip@pt\dimexpr(#1-\wd\z@)/2\relax\space 0 cm}\z@ \fi
		\else
			\ifhbox\z@
				\setbox\tw@\hbox to\wd\z@{\unhcopy\z@}%
				\count@=\badness
				\setbox\tw@\hbox to\wd\z@{\unhcopy\z@ \texit@superunskip}%
				\ifnum\numexpr\badness-\count@>\texit@realwd@minhbadness
					\setbox\tw@\hbox{\unhbox\z@ \texit@superunskip}%
					\ifdim\wd\tw@>\dimen@
						\dimen@=\wd\tw@
					\fi
					\iftexit@debug \texit@debug@draw@box{0 1 0}{}\tw@ \fi
				\else
					\ifdim\dimexpr\wd\z@+1sp>#1%
						\let\next=\relax
					\else
						\ifdim\wd\z@>\dimen@
							\dimen@=\wd\z@
						\fi
					\fi
					\iftexit@debug \texit@debug@draw@box{0 1 0}{}\z@ \fi
				\fi
			\else
				\ifdim\dimexpr\wd\z@+1sp>#1%
					\let\next=\relax
				\else
					\ifdim\wd\z@>\dimen@
						\dimen@=\wd\z@
					\fi
				\fi
				\iftexit@debug \texit@debug@draw@box{0 0 1}{}\z@ \fi
			\fi
		\fi
	\fi
	\next
}

% Remove all trailing skips, kerns, and penalties
\protected\def\texit@superunskip{%
	\ifcase\lastnodetype
	    % 0: char node
	\or % 1: hlist node
	\or % 2: vlist node
	\or % 3: rule node
	\or % 4: ins node
	\or % 5: mark node
	\or % 6: adjust node
	\or % 7: ligature node
	\or % 8: disc node
	\or % 9: whatsit node
	\or % 10: math node
	\or % 11: glue node
		\unskip
		\expandafter\texit@superunskip
	\or % 12: kern node
		\unkern
		\expandafter\texit@superunskip
	\or % 13: penalty node
		\unpenalty
		\expandafter\texit@superunskip
	\or % 14: unset node
	\or % 15: math mode nodes
	\fi
}
% Version of \texit@superunskip with special message handling and saves total distance in \dimen@i
\protected\def\texit@realwd@sift@superunskip{\dimen@i=\z@ \texit@realwd@sift@dosuperunskip}
\def\texit@realwd@sift@dosuperunskip{%
	\let\next@=\relax
	\ifcase\lastnodetype
	    % 0: char node
	\or % 1: hlist node
	\or % 2: vlist node
	\or % 3: rule node
	\or % 4: ins node
	\or % 5: mark node
	\or % 6: adjust node
	\or % 7: ligature node
	\or % 8: disc node
	\or % 9: whatsit node
	\or % 10: math node
	\or % 11: glue node
		\advance\dimen@i \lastskip
		\unskip
		\let\next@=\texit@realwd@sift@dosuperunskip
	\or % 12: kern node
		\advance\dimen@i \lastkern
		\unkern
		\let\next@=\texit@realwd@sift@dosuperunskip
	\or % 13: penalty node
		\ifnum\lastpenalty=\texit@realwd@marker \else
			\ifnum\lastpenalty=\texit@realwd@blocker \else
				\ifnum\lastpenalty=\texit@realwd@postdisplaypenalty
					\unpenalty \unskip \unpenalty
					\texit@realwd@isdisplaytrue
				\else
					\unpenalty
					\let\next@=\texit@realwd@sift@dosuperunskip
				\fi
			\fi
		\fi
	\or % 14: unset node
	\or % 15: math mode nodes
	\fi
	\next@
}
\def\texit@realwd@sift@end#1{%
	\ifdim\dimen@<#1%
		\global#1\dimen@
	\fi
}



% Colors

% Convert HTML color #1 to rgb and save results in \texit@temp
\protected\def\texit@htmltorgb#1{%
	\uppercase\expanded{{\edef\noexpand\texit@temp{\noexpand\texit@htmltorgbA#1}}}%
}
\def\texit@htmltorgbA#1#2#3#4#5#6{%
	\strip@pt\dimexpr"#1#2\p@/"FF\relax\space
	\strip@pt\dimexpr"#3#4\p@/"FF\relax\space
	\strip@pt\dimexpr"#5#6\p@/"FF\relax\space
}

\protected\def\texit@setdocumentcolor{%
	\@ifpackageloaded{xcolor}{%
		\definecolor{texittextcolor}{HTML}{\texit@textcolor}%
		\global\expandafter\let\expandafter\default@color
			\csname \string\color @\iftexit@textgradient white\else texittextcolor\fi\endcsname
		\ifnum\pdfstrcmp{trans}{\texit@bgcolor}=\z@ \else
			\definecolor{texitbgcolor}{HTML}{\texit@bgcolor}%
			\@ifpackageloaded{tikz-cd}{%
				\tikzcdset{background color=texitbgcolor}%
			}{}%
		\fi
	}{}%
}

\protected\def\texit@paintbg{%
	\iftexit@bggradient
		\vbox to\z@{%
			\setbox\z@=\vbox{%
				\pdfliteral{1 g 1 G}%
				\hrule height\pdfpageheight width\dimexpr\texit@pagebox@realwd+2\texit@border \relax
				\vss
			}%
			\texit@gradient@parse\texit@bggradient
			\texit@gradientbox@overshoot=\z@
			\def\texit@debug@node@color{1 .5 0}%
			\texit@gradientbox\z@\texit@bggradientangle
			% Below existing debug overlay
			\global\setbox\texit@debug@pagebox=\vbox{%
				\vbox to\z@{\kern-\texit@border \moveleft\texit@border \box\texit@debug@gradientbox \vss}%
				\unvbox\texit@debug@pagebox
			}%
			\vss
		}%
	\else
		\ifnum\pdfstrcmp{trans}{\texit@bgcolor}=\z@ \else
			\pdfsave
				\texit@htmltorgb\texit@bgcolor
				\pdfliteral{\texit@temp rg \texit@temp RG}%
				\vbox to\z@{%
					\hrule height\pdfpageheight width\dimexpr\texit@pagebox@realwd+2\texit@border \relax
					\vss
				}%
			\pdfrestore
		\fi
	\fi
}

\protected\def\texit@gradientbox#1#2{%
	\if\relax \ifdim\wd#1=\z@.\fi \ifdim\dimexpr\ht#1+\dp#1=\z@.\fi \relax
	\begingroup
	\expanded{\noexpand\texit@gradientbox@setends{#1}{\the\numexpr#2-(#2/360)*360}}%
	\iftexit@debug
		\global\setbox\texit@debug@gradientbox=\vbox{%
			\texit@debug@draw@end\texit@debug@node@color{0\%}{\texit@gradientbox@startx}{\texit@gradientbox@starty}%
			\texit@debug@draw@end\texit@debug@node@color{100\%}{\texit@gradientbox@endx}{\texit@gradientbox@endy}%
			\pdfliteral{%
				q
					.996264 0 0 .996264 0 0 cm
					\texit@debug@node@color\space RG
					.3 w
					[1.25] 0 d
					\expandafter\rem@pt \texit@gradientbox@startx\space
					\expandafter\rem@pt \texit@gradientbox@starty\space
					m
					\expandafter\rem@pt \texit@gradientbox@endx\space
					\expandafter\rem@pt \texit@gradientbox@endy\space
					l S
				Q
			}%
		}%
	\fi
	\setbox2=\hbox to\dimexpr\wd#1+2\texit@gradientbox@overshoot{%
		\kern\texit@gradientbox@overshoot
		\vbox to\dimexpr\ht#1+\dp#1+2\texit@gradientbox@overshoot{%
			\kern\texit@gradientbox@overshoot
			\pdfliteral{q .996264 0 0 .996264 0 0 cm /Sh sh Q}%
			\vfil
		}%
		\hfil
	}%
	\setbox#1=\hbox to\dimexpr\wd#1+2\texit@gradientbox@overshoot{%
		\kern\texit@gradientbox@overshoot
		\vbox to\dimexpr\ht#1+\dp#1+2\texit@gradientbox@overshoot{%
			\kern\texit@gradientbox@overshoot
			\box#1
			\vfil
		}%
		\hfil
	}%
	\immediate\pdfxform#1
	\setbox4=\hbox{\pdfrefxform\pdflastxform}%
	\immediate\pdfxform attr{/Group << /S /Transparency /CS /DeviceGray >>}4
	\count@=\pdflastxform
	\def\do##1##2{%
		\texit@htmltorgb{##2}%
		\ifnum##1=1
			\edef\next{<< /FunctionType 2 /Domain [0 1] /C0 [\texit@temp] /C1 }%
		\else
			\ifnum##1=\texit@gradient@count
				\edef\next{\next [\texit@temp] /N 1 >> }%
			\else
				\edef\next{\next [\texit@temp] /N 1 >> << /FunctionType 2 /Domain [0 1] /C0 [\texit@temp] /C1 }%
			\fi
		\fi
	}%
	\texit@gradient@colors
	\immediate\pdfxform resources{\texit@gradient@shader}2
	\setbox6=\hbox{\pdfliteral{/smask gs}\pdfrefxform\pdflastxform}%
	\pdfobj reserveobjnum\relax
	\immediate\pdfobj useobjnum\pdflastobj{\texit@gradient@egsresource}%
	\immediate\pdfxform resources{/ExtGState \the\pdflastobj\space 0 R}6
	\kern-\texit@gradientbox@overshoot
	\nointerlineskip \hbox{\kern-\texit@gradientbox@overshoot \pdfrefxform\pdflastxform}%
	\endgroup
	\else \box#1
	\fi
}

\newdimen\texit@gradientbox@overshoot
\texit@gradientbox@overshoot=10\p@

\def\texit@gradient@shader{%
	/Shading <<
		/Sh <<
			/ShadingType 2
			/ColorSpace /DeviceRGB
			/Domain [0 \the\numexpr\texit@gradient@count-1\relax]
			/Coords [
				\expandafter\rem@pt\texit@gradientbox@startx\space
				\expandafter\rem@pt\texit@gradientbox@starty\space
				\expandafter\rem@pt\texit@gradientbox@endx\space
				\expandafter\rem@pt\texit@gradientbox@endy\space
			]
			/Function <<
				/FunctionType 3
				/Domain [0 \the\numexpr\texit@gradient@count-1\relax]
				/Functions [ \next ]
				/Bounds [\texit@gradient@bounds 1\texit@gradient@count]
				/Encode [\texit@gradient@encode 1\texit@gradient@count]
			>>
			/Extend [true true]
		>>
	>>
}
\def\texit@gradient@bounds#1#2{%
	\ifnum#1<\numexpr#2-1\relax
		#1 %
		\expandafter\texit@gradient@bounds\expandafter{\the\numexpr #1+1\relax}{#2}%
	\fi
}
\def\texit@gradient@encode#1#2{%
	\ifnum#1<#2
		0 1 %
		\expandafter\texit@gradient@encode\expandafter{\the\numexpr #1+1\relax}{#2}%
	\fi%
}
\def\texit@gradient@egsresource{%
	<< /smask << /SMask <<
		/S /Luminosity /G \the\count@\space 0 R
	>> >> >>
}

% Parse a comma-separated list of hex values to store in \texit@gradient@colors, and set \texit@gradient@count
\protected\def\texit@gradient@parse#1{%
	\begingroup
		\count@=\z@
		\let\do\relax
		\let\texit@gradient@colors\empty
		\expanded{\noexpand\@for\noexpand\next:=#1}\do{%
			\if\relax\detokenize\expanded{{\expandafter\@gobble\next.}}\relax \else
				\advance\count@ 1
				\xdef\texit@gradient@colors{\texit@gradient@colors \do{\the\count@}{\romannumeral-`\0\next}}%
			\fi
		}%
		\ifnum\count@=1
			\count@=2
			\def\do##1##2{\noexpand\do1{##2}\noexpand\do2{##2}}%
			\xdef\texit@gradient@colors{\texit@gradient@colors}%
		\fi
		\ifnum\count@<2 \ClassError{texit}{Malformed gradient}{}\fi
		\xdef\texit@gradient@count{\the\count@}%
	\endgroup
}

% Compute endpoints of the gradient
\protected\def\texit@gradientbox@setends#1#2{%
	\dimen@i=.5\wd#1
	\dimen@ii=\dimexpr.5\ht#1+.5\dp#1\relax
	\ifnum#2<-90
		\texit@gradientbox@setendsA{#2}++%
	\else\ifnum#2<0
		\texit@gradientbox@setendsA{#2}-+%
	\else\ifnum#2<90
		\texit@gradientbox@setendsA{#2}--%
	\else
		\texit@gradientbox@setendsA{#2}+-%
	\fi \fi \fi
}
\def\texit@gradientbox@setendsA#1#2#3{%
	\texit@gradientbox@setendsB
		{ cos(#1*deg)*(#2\dimen@i*cos(#1*deg)+#3\dimen@ii*sin(#1*deg))+\dimen@i}%
		{ sin(#1*deg)*(#2\dimen@i*cos(#1*deg)+#3\dimen@ii*sin(#1*deg))-\dimen@ii}%
		{-cos(#1*deg)*(#2\dimen@i*cos(#1*deg)+#3\dimen@ii*sin(#1*deg))+\dimen@i}%
		{-sin(#1*deg)*(#2\dimen@i*cos(#1*deg)+#3\dimen@ii*sin(#1*deg))-\dimen@ii}%
}
\begingroup \lccode`!=`p \lccode`?=`t
\lowercase{\endgroup
	\def\texit@gradientbox@setendsB#1#2#3#4{%
		\edef\texit@gradientbox@startx{\csname fp_format:nn\endcsname{#1}{.5f}!?}%
		\edef\texit@gradientbox@starty{\csname fp_format:nn\endcsname{#2}{.5f}!?}%
		\edef\texit@gradientbox@endx  {\csname fp_format:nn\endcsname{#3}{.5f}!?}%
		\edef\texit@gradientbox@endy  {\csname fp_format:nn\endcsname{#4}{.5f}!?}%
	}
}



% Debug visuals

\protected\def\texit@debug@draw@page#1#2#3{%
	\pdfsave
	\pdfliteral{%
		.996264 0 0 .996264 0 0 cm
		q
			1 0 0 1 0 -\strip@pt\dimexpr\ht#1+\dp#1\relax\space cm
			.25 w
			#2
		Q
		.3 w 1 0 1 rg 1 0 1 RG
		0 0 \strip@pt\wd#1\space -\strip@pt\dimexpr\ht#1+\dp#1\relax\space re S
	}%
	\nointerlineskip \vbox to\z@{\vss\hbox{\texit@debugfont {\texit@debugfontbold#3}\enspace(\the\ht#1 + \the\dp#1) x \the\wd#1}\kern\p@}
	\pdfrestore
}

\protected\def\texit@debug@draw@box#1#2#3{%
	\global\texit@debug@boxes=\expanded{{%
		\the\texit@debug@boxes
		1 0 0 1 0 \strip@pt\dimen@i\space cm
		q
			#1 rg #1 RG #2
			0 0 \strip@pt\wd#3\space \strip@pt\dimexpr\ht#3+\dp#3\relax\space re S
			q
				[1.25] 0 d
				0 \strip@pt\dp#3\space m
				\strip@pt\wd#3\space \strip@pt\dp#3\space l S
			Q
		Q
		1 0 0 1 0 \strip@pt\dimexpr\ht#3+\dp#3\relax\space cm
	}}%
}

\protected\def\texit@debug@draw@end#1#2#3#4{%
	\pdfsave
	\pdfliteral{#1 rg #1 RG}%
	\nointerlineskip \moveright\dimexpr#3\relax \vbox to\z@{%
		\dimen@=\dimexpr#4\relax
		\kern-\dimen@
		\kern-4\p@
		\vbox to4\p@{\hbox to\z@{\hss \texit@debugfont #2\hss}\vss}
		\pdfliteral{%
			.996264 0 0 .996264 0 0 cm
			1.25 w 1 j
			0 0 m 0 0.01 l s
		}%
		\vss
	}%
	\pdfrestore
}

\protected\def\texit@debug@footline{%
	\nointerlineskip
	\pdfsave
	\pdfliteral{1 0 1 rg}%
	\nointerlineskip \moveright\p@ \vbox to\z@{%
		\vss
		\hbox{\texit@debugfont
			\texit@engine\ {\texit@debugfontbold v\the\texit@engineversion:\texit@enginerevision}\quad
			texit.cls {\texit@debugfontbold v\texit@version}\quad
			id: {\texit@debugfontbold \jobname}\quad
			\iftexit@textgradient
				textgradient: {\texit@debugfontbold
					\texit@textgradient\space (\texit@textgradientangle)}%
			\else
				textcolor: {\texit@debugfontbold \texit@bgcolor}%
			\fi \quad
			\iftexit@bggradient
				bggradient: {\texit@debugfontbold
					\texit@bggradient\space (\texit@bggradientangle)}%
			\else
				bgcolor: {\texit@debugfontbold \texit@bgcolor}%
			\fi \quad
			minpagewidth: {\texit@debugfontbold \ifdim\dimexpr\texit@minpagewidth<1sp None\else \the\dimexpr\texit@minpagewidth\relax \fi}\quad
			border: {\texit@debugfontbold \the\texit@border}%
		}%
		\kern\p@
	}%
	\pdfrestore
}



% Patches to LaTeX2e for better OTR compatibility

% Lists force full width
\edef\endtrivlist{\unexpanded\expandafter{\endtrivlist}\penalty\texit@realwd@blocker}

% Floats are fixed in place
\def\@xfloat#1[#2]{%
	\@nodocument
	\def\@captype{#1}%
	\ifinner \@parmoderr \fi
	\vskip\floatsep
	\color@vbox
		\normalcolor
		\vbox\bgroup
			\hsize\columnwidth
			\@parboxrestore
			\@floatboxreset
}%
\def\end@float{\@endfloatbox}
\def\@endfloatbox{%
			\par\vskip\z@skip
			\@minipagefalse
			\outer@nobreak
		\egroup
	\color@endbox
	\vskip\floatsep
}

% 5pt-high footnoterule
\protected\def\footnoterule{%
	\kern-\p@
	\hrule\@width\footnoterulewd \@height.4\p@
	\kern5.6\p@
}
\def\footnoteruleht{5\p@}
\def\footnoterulewd{.4\columnwidth}

\renewcommand\marginpar[2][]{\ClassError{texit}{Not supported}{}}
