from wise.worksheet.rules import PublicRule

AddSides = PublicRule('add_to_both_sides')
SubSides = PublicRule('sub_from_both_sides')
MulSides = PublicRule('mul_both_sides')
DivSides = PublicRule('div_both_sides')
AlgebraNormal = PublicRule('algebra_normal')

panel = {}
panel['Equation Manipulation'] = [('Add Equation by Expression', AddSides),
                                  ('Subtract Equation by Expression', SubSides),
                                  ('Multiply Equation by Expression', MulSides),
                                  ('Divide Equation by Expression', DivSides)
                                 ]

panel['Algebraic Simplification'] = [('Canonical Algebraic Form', AlgebraNormal),
                                    ]
