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
CombineRational = PublicRule('combine_rational')
SplitRational = PublicRule('split_rational')
DivisionThm = PublicRule('division_theorem')
Expand = PublicRule('algebra_expand')

panel = {}
panel['Relational'] = [('Add Equation by Expression', AddSides),
                                  ('Subtract Equation by Expression', SubSides),
                                  ('Multiply Equation by Expression', MulSides),
                                  ('Divide Equation by Expression', DivSides)
                                 ]

panel['Algebraic'] = [('Canonical Algebraic Form', AlgebraNormal),
                      ('Simplify Complex', ComplexSimplify),
                      ('Expand Complex Trig', ComplexTrigExpand),
                      ('ComplexToRect', ComplexToRect),
                      ('Division Theorem', DivisionThm),
                      ('Expand', Expand),
                     ]

panel['Rational'] = [('Combine Rational', CombineRational),
                     ('Split Rational', SplitRational),
                    ]
