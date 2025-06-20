% LuaTeXit Standard Class

\NeedsTeXFormat{LaTeX2e}
\def\texit@version{1.1f}
\ProvidesClass{luatexit}[2025-06-11 LuaTeXit Standard Class v\texit@version]



\DeclareKeys[texit]{
	bgcolor.store   = \texit@bgcolor,
	textcolor.store = \texit@textcolor,
	alwayswide.if   = texit@alwayswide,
	border.store    = \texit@border@,
% Options for article.cls
	draft.code      = \PassOptionsToClass{\CurrentOption}{article},
	leqno.code      = \PassOptionsToClass{\CurrentOption}{article},
	fleqn.code      = \PassOptionsToClass{\CurrentOption}{article}
}

\ProcessKeyOptions[texit]
% Make the switch global
\protected\def\texit@alwayswidetrue{\global\let\iftexit@alwayswide=\iftrue}
\protected\def\texit@alwayswidefalse{\global\let\iftexit@alwayswide=\iffalse}

\LoadClass[12pt]{article}

\RequirePackage{pdftexcmds}

\parindent=0pt

\textwidth=345pt

\textheight=\maxdimen



% Parameters

% Debug
\newif\iftexit@debug
% Make the switch global
\protected\def\texit@debugtrue{\global\let\iftexit@debug=\iftrue}
\protected\def\texit@debugfalse{\global\let\iftexit@debug=\iffalse}
\font\texit@debugfont=phvr7t at 3pt
\font\texit@debugfontbold=phvb7t at 3pt

% Background colour given in hex or "trans" (fallback: white)
\ifx\texit@bgcolor\empty
	\def\texit@bgcolor{ffffff}
\fi

% Global text colour given in hex (fallback: black)
\ifx\texit@textcolor\empty
	\def\texit@textcolor{000000}
\fi

% Whether to fix the page width (fallback: false) and minimum width of physical page (if alwayswide is false)
\newdimen\texit@minpagewidth
\texit@minpagewidth=110pt

% Border width function
% (default: max(5, min(15, d/24 - 5))pt where d = max(ht255+dp255, wd255))
\newdimen\texit@border
\ifx\texit@border@\empty
	\protected\def\texit@border@calc#1{%
		\texit@border=\dimexpr\ht#1+\dp#1\relax
		\ifdim\wd#1>\texit@border \texit@border=\wd#1\fi
		\texit@border=\dimexpr\texit@border/24-5pt\relax
		\ifdim\texit@border<5pt \texit@border=5pt \fi
		\ifdim\texit@border>15pt \texit@border=15pt \fi
	}
\else
	\protected\edef\texit@border@calc#1{\texit@border=\the\dimexpr\texit@border@\relax\relax}
\fi

% Parameter that controls greediness of horizontal cropping (lower = more greedy, must be between 1 and 10000)
\mathchardef\texit@realwd@minhbadness=1000



% Output Routine

\ifcsname tex_shipout:D\endcsname
	\expandafter\let\expandafter\texit@shipout@\csname tex_shipout:D\endcsname
\else
	\let\texit@shipout@=\shipout
\fi

% Holds final output page
\newbox\texit@pagebox

\newtoks\texit@headline
\newtoks\texit@footline

\newdimen\texit@pagebox@realwd
\newdimen\texit@boxcclv@realwd
\newdimen\texit@footins@realwd

\newtoks\texit@debug@boxes

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

\AddToHook{begindocument/end}{%
	\null \vfil \penalty\texit@discardpage
	\texit@setdocumentcolor
	\topskip=0pt
	\postdisplaypenalty=\texit@realwd@postdisplaypenalty
	\null \nointerlineskip \penalty\texit@realwd@marker
	\vskip-\parskip
}
\AddToHook{enddocument}{%
	\def\clearpage{\penalty-\@MM}%
}

% Only a penalty of -20000 may trigger output
\output={%
	\ifnum\outputpenalty=-\@MM
		\let\par=\@@par
		\texit@shipout\@cclv
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

\protected\def\texit@shipout#1{%
	\setbox\texit@pagebox=\vbox{%
		\texit@htmltorgb\texit@textcolor
		\pdfextension literal\relax{\texit@temp rg \texit@temp RG}%
		\texit@realwd#1\texit@boxcclv@realwd
		\global\texit@pagebox@realwd=\texit@boxcclv@realwd
		\iftexit@debug
			\setbox\z@=\vbox{\unvcopy#1}%
			\wd\z@=\texit@boxcclv@realwd
			\texit@debug@draw@page\z@{}{box255}%
		\fi
		\unvbox#1%
		\ifvoid\footins \else
			\vskip \skip\footins
			\footnoterule
			\texit@realwd\footins\texit@footins@realwd
			\ifdim\texit@footins@realwd>\texit@pagebox@realwd
				\global\texit@pagebox@realwd=\texit@footins@realwd
			\fi
			% This is needed to account for the width of the footnoterule
			\ifdim\texit@pagebox@realwd<.4\columnwidth
				\global\texit@pagebox@realwd=.4\columnwidth
			\fi
			\iftexit@debug
				\setbox\z@=\vbox{\unvcopy\footins}%
				\wd\z@=\texit@footins@realwd
				\texit@debug@draw@page\z@{}{footins}%
			\fi
			\unvbox\footins
		\fi
	}%
	\wd\texit@pagebox=\texit@pagebox@realwd
	\texit@border@calc\texit@pagebox
	\voffset=-1in
	\hoffset=\voffset
	\pageheight=\dimexpr\ht\texit@pagebox+\dp\texit@pagebox+2\texit@border \relax
	\pagewidth=\dimexpr\texit@pagebox@realwd+2\texit@border \relax
	\iftexit@alwayswide \else
		\ifdim\pagewidth<\texit@minpagewidth
			\pagewidth=\texit@minpagewidth
		\fi
	\fi
	\set@display@protect
	\texit@shipout@\vbox{%
		\texit@paintbg
		\vbox to\z@{\the\texit@headline \vss}%
		\nointerlineskip \kern\texit@border \moveright\texit@border \box\texit@pagebox
		\kern\texit@border
		\nointerlineskip \vbox to\z@{\vss \the\texit@footline}%
		\iftexit@debug \texit@debug@footline \fi
	}%
}

\protected\def\texit@debug@draw@page#1#2#3{%
	\pdfextension save\relax
	\pdfextension literal\relax{%
		.996264 0 0 .996264 0 0 cm
		q
			1 0 0 1 0 -\strip@pt\dimexpr\ht#1+\dp#1\relax\space cm
			.25 w
			\the\texit@debug@boxes
		Q
		.3 w 1 0 1 rg 1 0 1 RG #2
		0 0 m
		\strip@pt\wd#1\space 0 l
		\strip@pt\wd#1\space -\strip@pt\dimexpr\ht#1+\dp#1\relax\space l
		0 -\strip@pt\dimexpr\ht#1+\dp#1\relax\space l
		0 0 l s
	}%
	\vbox to\z@{\vss\hbox{\texit@debugfont {\texit@debugfontbold#3}\enspace(\the\ht#1 + \the\dp#1) x \the\wd#1}\kern2pt}
	\pdfextension restore\relax
}

\protected\def\texit@debug@draw@box#1#2#3{%
	\global\texit@debug@boxes=\expanded{{%
		\the\texit@debug@boxes
		1 0 0 1 0 \strip@pt\dimen@i\space cm
		q
			#1 rg #1 RG #2
			0 0 m
			\strip@pt\wd#3\space 0 l
			\strip@pt\wd#3\space \strip@pt\dimexpr\ht#3+\dp#3\relax\space l
			0 \strip@pt\dimexpr\ht#3+\dp#3\relax\space l
			0 0 l s
			q
				[1 1] 0 d
				0 \strip@pt\dp#3\space m
				\strip@pt\wd#3\space \strip@pt\dp#3\space l S
			Q
		Q
		1 0 0 1 0 \strip@pt\dimexpr\ht#3+\dp#3\relax\space cm
	}}%
}

\protected\def\texit@debug@footline{%
	\nointerlineskip
	\pdfextension save\relax
	\pdfextension literal\relax{1 0 1 rg}%
	\moveright\jot \vbox to\z@{%
		\vss
		\hbox{\texit@debugfont
			LuaTeX {\texit@debugfontbold v\the\luatexversion:\luatexrevision}\qquad
			luatexit.cls {\texit@debugfontbold v\texit@version}\qquad
			id: {\texit@debugfontbold \jobname}\qquad
			colours: {\texit@debugfontbold \texit@bgcolor/\texit@textcolor}\qquad
			alwayswide: {\texit@debugfontbold \iftexit@alwayswide true\else false (\the\texit@minpagewidth)\fi}\qquad
			border: {\texit@debugfontbold \the\texit@border}%
		}%
		\kern\jot
	}%
	\pdfextension restore\relax
}

% Compute real width of #1 and store in #2 (\global)
% A more robust algorithm is available in LuaTeX; see https://tex.stackexchange.com/q/734916/
\protected\def\texit@realwd#1#2{%
	#2=\wd#1%
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
					\ifdim\wd\z@=#1%
						\let\next=\relax
					\else
						\ifdim\wd\z@>\dimen@
							\dimen@=\wd\z@
						\fi
					\fi
					\iftexit@debug \texit@debug@draw@box{0 1 0}{}\z@ \fi
				\fi
			\else
				\ifdim\wd\z@>\dimen@
					\dimen@=\wd\z@
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

\renewcommand\marginpar[2][]{\ClassError{texit}{Not supported}{}}



% Colors

% Convert HTML color #1 to rgb and save results in \texit@temp
\protected\def\texit@htmltorgb#1{%
	\uppercase\expanded{{\edef\noexpand\texit@temp{\noexpand\texit@htmltorgb@#1}}}%
}
\def\texit@htmltorgb@#1#2#3#4#5#6{%
	\strip@pt\dimexpr"#1#2pt/255\relax\space
	\strip@pt\dimexpr"#3#4pt/255\relax\space
	\strip@pt\dimexpr"#5#6pt/255\relax\space
}

\protected\def\texit@setdocumentcolor{%
	\@ifpackageloaded{xcolor}{%
		\definecolor{texittextcolor}{HTML}{\texit@textcolor}%
		\global\expandafter\let\expandafter\default@color
			\csname \string\color @texittextcolor\endcsname
		\ifnum\pdf@strcmp{trans}{\texit@bgcolor}=\z@ \else
			\definecolor{texitbgcolor}{HTML}{\texit@bgcolor}%
			\@ifpackageloaded{tikz-cd}{%
				\tikzcdset{background color=texitbgcolor}%
			}{}%
		\fi
	}{}%
}

\protected\def\texit@paintbg{%
	\ifnum\pdf@strcmp{trans}{\texit@bgcolor}=\z@ \else
	\pdfextension save\relax
		\texit@htmltorgb\texit@bgcolor
		\pdfextension literal\relax{\texit@temp rg \texit@temp RG}%
		\vbox to\z@{%
			\hrule height\pageheight width\dimexpr\texit@pagebox@realwd+2\texit@border \relax
			\vss
		}%
	\pdfextension restore\relax
	\nointerlineskip
	\fi
}
