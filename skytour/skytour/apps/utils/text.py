def replace_greek_letters(text, translate='title'):
    """
    Replaces common Greek letters in a string with their English names.
    """
    greek_to_english = {
        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'epsilon',
        'ζ': 'zeta', 'η': 'eta', 'θ': 'theta', 'ι': 'iota', 'κ': 'kappa',
        'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron',
        'π': 'pi', 'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
        'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
        'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta', 'Ε': 'Epsilon',
        'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta', 'Ι': 'Iota', 'Κ': 'Kappa',
        'Λ': 'Lambda', 'Μ': 'Mu', 'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron',
        'Π': 'Pi', 'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
        'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega'
    }

    for greek_char, english_name in greek_to_english.items():
        if translate == 'title':
            english_name = english_name.title()
        elif translate == 'lower':
            english_name = english_name.lower()
        elif translate == 'upper':
            english_name = english_name.upper()
        text = text.replace(greek_char, english_name)
    return text