from wise.worksheet.rules import PublicRule

# The names given to the the public rules are all dummy variables
# (i.e. they aren't used anywhere else) they namely exist so that
# when worksheet.rules inspects this file they appear as named
# entities in __dict__ and can be extracted. You could very well
# call them Rule1, Rule2, Rule3, ....

panel = {}
panel['Relational'] = [

        ('Add To Both Sides'        , PublicRule('add_to_both_sides')),
        ('Subtract From Both Sides' , PublicRule('sub_from_both_sides')),
        ('Multiply To Both Sides'   , PublicRule('mul_both_sides')),
        ('Divide Both Sides'        , PublicRule('div_both_sides')),
        ('Algebraic Normal Form'    , PublicRule('algebra_normal')),
        ('Commute Left'             , PublicRule('commute_left')),

    ]

panel['Commutative Algebra'] = [

        ('Commute Elementary'        , PublicRule('commute_elementary')),
        ('Expand Multiplication'     , PublicRule('algebra_expand')),
        ('Pull Left'                 , PublicRule('pull_left')),
        ('Pull Right'                , PublicRule('pull_right')),
        ('Pull Constants Left'       , PublicRule('pull_numeric_left')),
        ('Pull Constants Right'      , PublicRule('pull_numeric_right')),
        ('Iterate Left'      , PublicRule('iter_left')),

    ]

panel['Rational'] = [

        ('Split Rational'            , PublicRule('split_rational')),
        ('Combine Ratiional'         , PublicRule('combine_rational')),
        ('Seperate Ratiional'        , PublicRule('seperate_rational')),

    ]
