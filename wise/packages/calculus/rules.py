from wise.translators.pure_wrap import PublicRule

panel = {}

# -------------------
# Derivatives
# -------------------

#class diff_normal(PublicRule):
    #"""
    #Evaluate elementary derivatives to normal form.
    #"""
    #pure = 'diff_normal'

#panel['Calculus'] = (
        #('Derivatives'    , diff_normal),
#)

# -------------------
# Series
# -------------------

#class truncate_series(PublicRule):
    #"""
    #"""
    #pure = 'truncate_series'

class prettyseries(PublicRule):
    """
    """
    pure = 'prettyseries'

class rmzeroterms(PublicRule):
    """
    """
    pure = 'rmzeroterms'

class truncateseries(PublicRule):
    """
    """
    pure = 'truncateseries'

class taylor1(PublicRule):
    """
    """
    pure = 'taylor1'

class taylor2(PublicRule):
    """
    """
    pure = 'taylor2'

class taylor3(PublicRule):
    """
    """
    pure = 'taylor3'

panel['Series'] = (
        ('Remove Zero Terms'    , rmzeroterms),
        ('Pretty Series'        , prettyseries),
        ('Truncate Series'      , truncateseries),
        ('First Order Taylor'      , taylor1),
        ('Second Order Taylor'     , taylor2),
        ('Third Order Taylor'      , taylor3),
)


