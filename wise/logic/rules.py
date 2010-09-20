from wise.worksheet.rules import PublicRule

push_assoc_left = PublicRule('push_assoc_left')
push_assoc_right = PublicRule('push_assoc_right')

panel = {}
panel['Logic'] = [('Push associativity right',push_assoc_right),
                  ('Push associativity left',push_assoc_left)
                 ]
