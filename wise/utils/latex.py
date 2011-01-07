# -*- coding: utf-8 -*-

greek_unicode = {
         'alpha'  :          'α',
         'beta'   :          'β',
         'gamma'  :          'γ',
         'delta'  :          'δ',
         'epsilon':          'ε',
         'zeta'   :          'ζ',
         'eta'    :          'η',
         'theta'  :          'ϑ',
         'iota'   :          'θ',
         'kappa'  :          'ι',
         'kappa'  :          'κ',
         'lambda' :          'λ',
         'mu'     :          'μ',
         'nu'     :          'ν',
         'xi'     :          'ξ',
         'omicron':          'ο',
         'pi'     :          'π',
         'rho'    :          'ρ',
         'sigma'  :          'σ',
         'tau'    :          'τ',
         'upsilon':          'υ',
         'phi'    :          'ϕ',
         'chi'    :          'χ',
         'psi'    :          'ψ',
         'omega'  :          'ω',
         'Gamma'  :          'Γ',
         'Delta'  :          'Δ',
         'Theta'  :          'Θ',
         'Lambda' :          'Λ',
         'Xi'     :          'Ξ',
         'Pi'     :          'Π',
         'Sigma'  :          'Σ',
         'Upsilon':          'Υ',
         'Phi'    :          'Φ',
         'Psi'    :          'Ψ',
         'Omega'  :          'Ω',
         }

#TODO: change this to zip(iterkeys, itervalues)
greek_unicode_list = [
         ('alpha'  ,          'α'),
         ('beta'   ,          'β'),
         ('gamma'  ,          'γ'),
         ('delta'  ,          'δ'),
         ('epsilon',          'ε'),
         ('zeta'   ,          'ζ'),
         ('eta'    ,          'η'),
         ('theta'  ,          'ϑ'),
         ('iota'   ,          'θ'),
         ('kappa'  ,          'ι'),
         ('kappa'  ,          'κ'),
         ('lambda' ,          'λ'),
         ('mu'     ,          'μ'),
         ('nu'     ,          'ν'),
         ('xi'     ,          'ξ'),
         ('omicron',          'ο'),
         ('pi'     ,          'π'),
         ('rho'    ,          'ρ'),
         ('sigma'  ,          'σ'),
         ('tau'    ,          'τ'),
         ('upsilon',          'υ'),
         ('phi'    ,          'ϕ'),
         ('chi'    ,          'χ'),
         ('psi'    ,          'ψ'),
         ('omega'  ,          'ω'),
         ('Gamma'  ,          'Γ'),
         ('Delta'  ,          'Δ'),
         ('Theta'  ,          'Θ'),
         ('Lambda' ,          'Λ'),
         ('Xi'     ,          'Ξ'),
         ('Pi'     ,          'Π'),
         ('Sigma'  ,          'Σ'),
         ('Upsilon',          'Υ'),
         ('Phi'    ,          'Φ'),
         ('Psi'    ,          'Ψ'),
         ('Omega'  ,          'Ω'),
         ]

greek_alphabet_latex = {
        'alpha'  :  '\\alpha',
        'beta'   :  '\\beta',
        'gamma'  :  '\\gamma',
        'delta'  :  '\\delta',
        'epsilon' :  '\\epsilon',
        'varepsilon' :  '\\varepsilon',
        'zeta'   :  '\\zeta',
        'eta'    :  '\\eta',
        'theta'  :  '\\theta',
        'vartheta' :'\\vartheta',
        'gamma'  :  '\\gamma',
        'kappa'  :  '\\kappa',
        'lambda' :  '\\lambda',
        'mu'     :  '\\mu',
        'nu'     :  '\\nu',
        'xi'     :  '\\xi',
        'pi'     :  '\\pi',
        'varpi'  :  '\\varpi',
        'rho'    :  '\\rho',
        'varrho' :  '\\varrho',
        'sigma'  :  '\\sigma',
        'varsigma' :'\\varsigma',
        'tau'    :  '\\tau',
        'upsilon':  '\\upsilon',
        'phi'    :  '\\phi',
        'varphi' :  '\\varphi',
        'chi'    :  '\\chi',
        'psi'    :  '\\psi',
        'omega'  :  '\\omega',
        'Gamma'  :  '\\Gamma' ,
        'Delta'  :  '\\Delta' ,
        'Theta'  :  '\\Theta' ,
        'Lambda' :  '\\Lambda',
        'Xi'     :  '\\Xi'    ,
        'Pi'     :  '\\Pi'    ,
        'Sigma'  :  '\\Sigma' ,
        'Upsilon':  '\\Upsilon',
        'Phi'    :  '\\Phi'   ,
        'Psi'    :  '\\Psi'   ,
        'Omega'  :  '\\Omega' ,
        }

def greek_lookup(s):
    try:
        return greek_unicode[s]
    except KeyError:
        return s
