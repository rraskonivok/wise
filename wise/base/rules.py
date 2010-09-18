from wise.worksheet.rules import PublicRule

# The names given to the the public rules are all dummy variables
# (i.e. they aren't used anywhere else) they namely exist so that
# when worksheet.rules inspects this file they appear as named
# entities in __dict__ and can be extracted. You could very well
# call them Rule1, Rule2, Rule3, ....

AddSides = PublicRule('add_to_both_sides')
SubSides = PublicRule('sub_from_both_sides')
MulSides = PublicRule('mul_both_sides')
DivSides = PublicRule('div_both_sides')
AlgebraNormal = PublicRule('algebra_normal')

ComplexToRect = PublicRule('complex_polar_to_rect')
ComplexTrigExpand = PublicRule('complex_trig_expand')
ComplexSimplify = PublicRule('simplify_complex')
RectangularToPolar = PublicRule('rect_to_polar')

panel = {}
panel['Equation Manipulation'] = [('Add Equation by Expression', AddSides),
                                  ('Subtract Equation by Expression', SubSides),
                                  ('Multiply Equation by Expression', MulSides),
                                  ('Divide Equation by Expression', DivSides)
                                 ]

panel['Algebraic Simplification'] = [('Canonical Algebraic Form', AlgebraNormal),
                                     ('Simplify Complex', ComplexSimplify),
                                     ('Expand Complex Trig', ComplexTrigExpand),
                                     ('Polar Complex to Rectangular', ComplexToRect),
                                    ]
