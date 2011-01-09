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

..
Equation Manipulation
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
     \operatorname{atan2}(y, x) = \begin{cases} \arctan(\frac y x) & \qquad x > 0 \\ \pi + \arctan(\frac y x) & \qquad y \ge 0 , x < 0 \\ -\pi + \arctan(\frac y x) & \qquad y < 0 , x < 0 \\ \frac{\pi}{2} & \qquad y > 0 , x = 0 \\ -\frac{\pi}{2} & \qquad y < 0 , x = 0 \\ \frac{0}{0} & \qquad y = 0, x = 0 \end{cases} 
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
:x: Complex number
:Description: Return the real part of a complex number x.
.. math::
     \text{Re}(x+iy) = x

:Python: None (Internal)
:See Also:
------------ 

:Name: ``Im`` x
:Arguments:
:x: Complex number
:Description: Return the imaginary part of a complex number x.
.. math::
     \text{Re}(x+iy) = y

:Python: None (Internal)
:See Also:
------------ 

:Name: ``conj`` x
:Arguments:
:x: Complex number
:Description: Return the complex conjugate of a complex number x.
.. math::
     \text{Re}(x+iy) = x-iy

:Python: None (Internal)
:See Also:
------------ 

:Name: ``simplify_complex`` x
:Arguments:
:x: Complex number
:Description: Simplifies a complex expression with the following rules:
.. math::
     (u+iv) + (x+iy) = (u+x)+i(v+y)\\
     (u+iv) - (x+iy) = (u-x)+i(v-y)\\
     (a+ib) \times (c+id) = (ac-bd) + i (bc+ad)\\
     \frac{a + bi}{c + di} = \left({ac + bd \over c^2 + d^2}\right) + \left( {bc - ad \over c^2 + d^2} \right)i

:Python: None (Internal)
:See Also:
------------ 

:Name: ``rect_to_polar`` x
:Arguments:
:x: Complex number
:Description: Returns the polar form of a complex number as a complex exponential.
.. math::
     (x+iy) \mapsto \sqrt{x^2+y^2} e^{i \theta}

:Python: None (Internal)
:See Also:
------------ 

:Name: ``complex_trig_expand`` x
:Arguments:
:x: Arbitrary expression
:Description: Reduces the given expression with the following rules:
.. math::
     \sin(x+iy) = \sin(x) \cosh(y) + \cos(x) \sinh(y) i\\
     \cos(x+iy) = \cos(x) \cosh(y) - \sin(x) \sinh(y) i\\
     \tan(x+iy) = \sin(2x) + \frac{\sin(2y) i}{\cos(2x)+\cosh(2y)}\\

:Python: None (Internal)
:See Also:
------------ 

:Name: ``complex_polar_to_rect`` x
:Arguments:
:x: Multiplication expression
:Description: Converts a complex exponential into a rectangular complex number
.. math::
     r e^{i \theta} = r \cos(\theta)+i r \sin(\theta)

:Python: None (Internal)
:See Also:
------------ 

:Name: ``complex_split`` x
:Arguments:
:x: Complex expression
:Description: Converts a atomic complex value into a addition of the real part and the product of the imaginary part and the imaginary unit
:Python: None (Internal)
:See Also:
------------ 

:Name: ``simplify_multiplication`` x
:Arguments:
:x: Arbitrary expression
:Description: Reduces the given expression with the following rules
.. math::
     0x = 0\\
     a^x a^y = a^{x+y}\\
     (a b^x) b^y = a b^{x+y}\\
     x(yz) = (xy)z\\
     x(-y) = (-x)y\\

Multiplication is is associated to the left.

Multiplication of numeric quantities is reduced to a
single numeric quantitiy.

Multiplication of algebraic terms is sorted alphabetically by
variable as defined by ``cmp`` rule.

:Python: None (Internal)
:See Also:
------------ 

:Name: ``simplify_addition`` x
:Arguments:
:x: Arbitrary expression
:Description: Reduces the given expression with the following rules
.. math::
     0+x = x\\
     (qx)+(rx) = (q+r)(x)\\
     (qx)+(qy) = (q)(x+y)\\
     x+(y+z) = (x+y)+z\\
     -x+-y = -(x+y)\\

Addition is is associated to the left.

Addition of numeric quantities is reduced to a
single numeric quantitiy.

Addition of algebraic terms is sorted alphabetically by
variable as defined by ``cmp`` rule.

:Python: None (Internal)
:See Also:
------------ 

:Name: ``simplify_power`` x
:Arguments:
:x: Arbitrary expression
:Description: Reduces the given expression with the following rules
.. math::
     x^0 = 1\\
     x^1 = x\\
     0^x = 0\\
     1^x = 1\\
     (x^y)^z = x^{yz}\\
     (xy)^z = x^y x^z\\

Powers of numeric quantities is reduced to a
single numeric quantitiy.

:Python: None (Internal)
:See Also:
------------ 

:Name: ``simplify_rational`` x
:Arguments:
:x: Arbitrary expression
:Description: Reduces the given expression with the following rules
.. math::
     \frac{x}{y} = x y^{-1}\\

:Python: None (Internal)
:See Also:
------------ 

:Name: ``combine_rational`` x
:Arguments:
:x: Complex number
:Description: Combines rational expressions according to the rules:
.. math::
     -\frac{a}{b} = \frac{-a}{b}\\
     \frac{a}{b} + \frac{c}{d} = \frac{ad+bc}{bd}\\
     \frac{a}{b} \cdot \frac{c}{d} = \frac{ac}{bd}\\
     \frac{a}{b} \div \frac{c}{d} = \frac{ad}{bc}

:Python: None (Internal)
:See Also:
------------ 

:Name: ``split_rational`` x
:Arguments:
:x: Complex number
:Description: Seperates rational expressions according to the rules:
.. math::
     \frac{a+b}{c} = \frac{a}{c} + \frac{b}{c}

:Python: None (Internal)
:See Also:
------------ 

