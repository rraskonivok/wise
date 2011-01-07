from wise.worksheet.rules import PublicRule

push_assoc_left = PublicRule('push_assoc_left')
push_assoc_right = PublicRule('push_assoc_right')
demorgan = PublicRule('demorgan')
doubleneg = PublicRule('doubleneg')

panel = {}
panel['Logic'] = [('Push associativity right',push_assoc_right),
                  ('Push associativity left',push_assoc_left),
                  ("De Morgan's laws",demorgan),
                  ("Double negation",doubleneg)
                 ]
