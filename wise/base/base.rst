..
Base Mathematics
==============

..
Algebraic Ordering
--------------

:Name: ``cmp`` x y - Lexicographical ordering on algebraic terms
:Arguments:
:x: Arbitrary expression
:y: Arbitrary expression
:Description: Returns 1 if ``x`` > ``y``
:Python: None (Internal)
:See Also:
 ------------ 

..
Deconstructors
--------------

:Name: ``sump`` x
:Arguments:
:x: Arbitrary expression
:Description: Returns 1 if ``x`` is an addition expression, 0 otherwise
:Python: None (Internal)
:See Also:
------------ 

:Name: ``base`` x
:Arguments:
:x: Arbitrary expression
:Description: Returns the base of a exponential expression.  For all other expression returns the given expression.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``exponent`` x
:Arguments:
:x: Arbitrary expression
:Description: Returns the exponent of a exponential expression. For all other expression returns the given expression.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``term`` x
:Arguments:
:x: Arbitrary expression
:Description: Returns the a non-numeric element of a multiplication expression, otherwise returns the expression.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``constant`` x
:Arguments:
:x: Arbitrary expression
:Description: Returns numeric element of a multiplication expression, otherwise returns the expression.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``add_to_both_sides`` x y
:Arguments:
:x: Equation
:y: Arbitrary expression
:Description: Adds y to both sides of x.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``sub_from_both_sides`` x y
:Arguments:
:x: Equation
:y: Arbitrary expression
:Description: Subtracts y from both sides of x.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``mul_both_sides`` x y
:Arguments:
:x: Equation
:y: Arbitrary expression
:Description: Multiplites y to both sides of x.
:Python: None (Internal)
:See Also:
------------ 

:Name: ``div_both_sides`` x y
:Arguments:
:x: Equation
:y: Arbitrary expression
:Description: Divides both sides of x by y.
:Python: None (Internal)
:See Also:
------------ 

..
Trigonometric Manipulation
------------ 

..
Trigonometric Simplification
------------ 

:Name: ``atan2`` y x
:Arguments:
:x: Arbitrary expression
:y: Arbitrary expression
:Description: Return atan(y / x), in radians. The result is between -pi and pi. 
.. math::
     \operatorname{atan2}(y, x) = \begin{cases} \arctan(\frac y x) & \qquad x > 0 \\ \pi + \arctan(\frac y x) & \qquad y \ge 0 , x < 0 \\ -\pi + \arctan(\frac y x) & \qquad y < 0 , x < 0 \\ \frac{\pi}{2} & \qquad y > 0 , x = 0 \\ -\frac{\pi}{2} & \qquad y < 0 , x = 0 \\ \text{undefined} & \qquad y = 0, x = 0 \end{cases}

:Python: None (Internal)
:See Also:
------------ 

..
Absolute Value Manipulation
------------ 

..
Complex Manipulation
------------ 

:Name: ``Re`` x
:Arguments:
:x: Equation
:Description: Return the real part of a complex number x.
.. math::
     \text{Re}(x+iy) = x

:Python: None (Internal)
:See Also:
------------ 

