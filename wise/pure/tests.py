from pure import PureEnv, PureSymbol

env = PureEnv()

assert env != None
assert env.eval('1') != None
assert str(PureSymbol('x')) == 'x'

env.eval('using prelude')

assert str(env.eval('i2p $ x + y')) == 'add x y'
assert str(env.eval('3+1+4')) == '8'

print 'Passed all tests!'
