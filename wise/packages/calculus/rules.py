from wise.translators.pure_wrap import PublicRule

panel = {}

class diff_normal(PublicRule):
    """
    Evaluate elementary derivatives to normal form.
    """
    pure = 'diff_normal'

panel['Calculus'] = (

        ('Evaluate  Derivatives'    , diff_normal),

)
