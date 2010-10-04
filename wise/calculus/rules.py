from wise.worksheet.rules import PublicRule

panel = {}

EvalDiff = PublicRule('diff_normal')
DiffSides = PublicRule('diff_both_sides')

panel['Differentiation'] = [('Evaluate Derivatives',EvalDiff),
                            ('Differentiate Both Sides',DiffSides)
                           ]
