FAQ
================================

What browsers can I use the Notebook in?
-----------------------------------------
At this time, only Firefox 3.5+ . Unfortunatly Internet Explorer, Chromium, Safari, 
and Opera do not support enough MathML to be functional. Hopefully this will
change as MathML is now part of the HTML5 spec. For best results use Firefox 4.

Why does the math not render properly?
--------------------------------------
Wise tries to load the STIX webfonts in your browser but web
fonts are only supported in fairly recent version of Firefox. To get best
results you may need install the `STIX fonts <http://stixfonts.org/>`_ locally.

How is this different from Sage (or Mathematica / Maple)?
---------------------------------------------------------
At the moment Wise is in its infancy and is little more than a toy that can do
some basic algebraic manipulations. Hopefully it become more in
time but the goal of the project is not to create another computer
algebra system, Sage already satifies this need quite well.

If you are using Mathematica or Maple then definetley give the Sage project a look.


Will it run on Windows?
-----------------------
Maybe, all the libraries Wise is based on can be run on Windows but I have not tested this. 
The primary hurdle would be getting Pure compiled and getting the Python virtualenv set 
up. My target operating systems are Linux/BSD and Mac OSX to a lesser degree.

Is the Notebook secure enough to run in the wild?
-----------------------------------------------------
No.
