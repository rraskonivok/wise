import parser

#Used for hashing trees
from hashlib import sha1

from mathobjects import *

from wise.worksheet.utils import *
import wise.worksheet.exceptions as exception

from pure_wrap import p2i, i2p

#-------------------------------------------------------------
# Parse Tree
#-------------------------------------------------------------

# Create our parse tree structure, the Branch object simply holds
# the arguments before they are evaluated into internal Math
# objects


class Branch(object):
    #                                                             
    #         O            The hash of a non-terminal node is 
    #        / \           hash of its children's hashes.
    #       /   \                
    #      O     O         Terminal nodes have carry a unicode   
    #     /|\    |         string which is hashed yield the hash
    #    / | \   |         of the node.                         
    #   #  #  #  O                                               
    #           / \        All nodes have carry a unicode      
    #          /   \       string 'type' which is hashed
    #         #     #      into the node.

    # We use the SHA1 algorithm, since it likely to have
    # collisions than CRC32. But it's much slower.

    atomic = False

    def __init__(self,typ,args,parent):
        self.type = typ
        self.id = None

        self.valid = False
        self.hash = False
        self.commutative = False

        if self.type == 'Addition':
            self.commutative = True

        def descend(ob):
            if type(ob) is str or type(ob) is unicode:
                return ob
            else:
                #Yah, there is a serious functional slant to this
                return reduce(lambda a,b: Branch(a,b,self), ob)

        #Allow for the possibility of argument-less/terminal Branches
        if args:
            self.args = map(descend,args)
        else:
            self.args = []

        self.parent = parent

    def __repr__(self):
        return 'Branch: %s(%r)' % (self.type,self.args)

    def __getitem__(self,n):
        return self.args[n]

    def __hash__(self):
        return self.gethash()

    def gethash(self):

        #      Eq. 1     =      Eq. 2          
        #       / \              / \          
        #      /   \            /   \         
        #    LHS   RHS         LHS   RHS          
        #    /|\    |           |    /|\  
        #   / | \   |           |   / | \ 
        #  x  y  z add         add x  y  z
        #          / \         / \    
        #         /   \       /   \   
        #        1     2     2     1      
        #
        # The point of this hash function is so that equivalent
        # mathobjects "bubble" up through the tree. Since
        # addition is commutative: 
        #
        # hash ( 1 + 0 ) = hash( 1 ) + hash ( 0 ) 
        #                = hash( 0 ) + hash ( 1 )
        #
        # Mathematical structures are in general much too
        # complex for this to always work, but it is very useful
        # for substitutions on toplevel nodes like Equation.

        #HASH_ALGORITHM = sha1
        HASH_ALGORITHM = crcdigest

        if self.valid:
            return self.hash

        def f(x):
            if isinstance(x,unicode) or isinstance(x,str):
                digester = HASH_ALGORITHM()
                digester.update(x)
                return digester.hexdigest()
            else:
                return x.gethash()

        ls = map(f,self.args)
        digester = HASH_ALGORITHM()

        # Hashing the type assures that
        # Addition( x y ) and Multiplication( x y )
        # yield different hashes 
        digester.update(self.type)

        if self.commutative:
            sm = sum([int(hsh,16) for hsh in ls])
            digester.update(str(sm))
            self.hash = digester.hexdigest()
        else:
            for arg in ls:
                digester.update(arg)
            self.hash = digester.hexdigest()

        self.valid = True
        return self.hash

    def gen_uids(self,uid_generator):
        '''Take a uid generator and walk the tree assigning each
        node a unique id'''

        self.id = uid_generator.next()
        self.idgen = uid_generator

        for node in self.walk():
            node.id = uid_generator.next()
            # Give the element the uid generator so it can spawn
            # new elements that don't conflict in the HTML
            # id/namespace
            node.idgen = uid_generator


    def is_toplevel(self):
        return self.parent == None

    def walk(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
                yield i

    def walk_all(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
                yield i
            else:
                yield i

    def walk_args(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
            else:
                yield i

    def json(self):
        def f(x):
            if isinstance(x,Branch):

                i = x.json()
                return i
            else:
                return x
        obj = map(f,self.args)
        return {'name': self.id, 'type': self.type , 'args': obj }

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        def f(x):
            if isinstance(x,Branch):
                i = x.json_flat(lst)
                return i
            else:
                return x

        lst.append({"id": self.id,
                    "type": self.type,
                    "children": [child.id for child in self.args if isinstance(child,Branch)]})

        map(f,self.args)
        return lst

    def eval_args(self):
        '''Create an instance of the node's type ( self.type )
        and pass the node's arguments ( self.args ) to the new
        instance'''

        # We call the evil eval a couple of times but it's OK
        # because any arguments are previously run through the
        # sexp parser and if the user tries to inject
        # anything other than (Equation ...)  it will throw an
        # error and not reach this point anyways.

        # Recursive descent
        def f(x):
            if isinstance(x,unicode) or isinstance(x,str):
                # The two special cases where a string in the
                # parse tree is not a string
                if x == 'Placeholder':
                    return Placeholder()
                elif x == 'None':
                    return Empty()
                else:
                    return x
            elif isinstance(x,int):
                return x
            elif isinstance(x,Branch):
                #create a new class from the Branch type
                try:
                    return x.eval_args()
                except KeyError:
                    raise exception.InternalMathObjectNotFound(x)
            else:
                print 'something strange is being passed'

        #Ugly hack to pass database indices
        #if '__' in self.type:
        #    ref,id = self.type.split('__')
        #    self.args.insert(0,id)
        #    obj = apply(eval(ref),(map(f,self.args)))
        #    obj.hash = self.gethash()
        #    obj.idgen = self.idgen
        #else:

        if self.atomic:
            print self.type
            obj = typ(*self.args)
        else:
            obj = apply(eval(self.type),(map(f,self.args)))

        obj.hash = self.gethash()
        obj.id = self.id
        obj.idgen = self.idgen

        if hasattr(obj,'side') and (obj.side is not None):
            obj.set_side(obj.side)

        return obj

    def eval_pure(self):
        '''Like pure_eval but instead of mapping into internal
        python objects it maps into Pure Objects. This is used
        for when we run an expression through pure and want to
        map the result into something to use in Python.'''

        #Evalute by descent
        def f(x):
            #Ugly Hack
            if isinstance(x,str):
                if x.isdigit():
                    obj = Numeric(x)
                elif x in translation_table:
                    obj = translate_pure(x)()
                else:
                    obj = Variable(x)
                obj.idgen = self.idgen
                obj.id = self.idgen.next()
                return obj
            elif isinstance(x,Branch):
                '''create a new class from the Branch type'''
                try:
                    return x.eval_pure()
                except KeyError:
                    raise exception.InternalMathObjectNotFound(x)
            else:
                print 'something strange is being passed'

        print 'HERE IT IS',self,type(self.args[0])
        typ = translate_pure(self.type)

        #try:
        if self.atomic:
            obj = typ(*self.args)
        else:
            obj = apply(typ,(map(f,self.args)))
        #except TypeError:
        #    raise exception.ParseError("Invalid function arguments: %s, %s" % (self.args, typ))

        obj.id = self.id
        obj.idgen = self.idgen

        return obj

def ParseTree(str,ignore_atomic=True):
    atomic = False
    parsed = parser.eq_parse(str)

    # Our sexp is atomic ( only occurs in Pure -> Python translation)
    if not ignore_atomic:
        if not parsed[1]:
            atomic = True
            tag, args = parsed
            if tag.isdigit():
                parsed = ('num',[tag])
            else:
                parsed = ('var',[tag])

    branch = reduce(lambda type, args: Branch(type,args,None), parsed)
    branch.atomic = atomic

    return branch

def pretty(t):
    '''Prints out a tree diagram of the parse tree with the
    hashes for each objects'''
    from funcparserlib.util import pretty_tree

    def kids(x):
        if isinstance(x,Branch):
            return x.args
        else:
            return []

    def show(x):
        if isinstance(x,Branch):
            return str(x.type) + '  ::  ' +  hash(x)
        else:
            return repr(x)

    return pretty_tree(t,kids,show)

def parse_pure_exp(expr, uidgen=None):
    #Get the string representation of the pure expression
    parsed = ParseTree(str(expr),ignore_atomic=False)
    if uidgen:
        parsed.gen_uids(uidgen)
    else:
        print "You better be manually assigning or craaazy shit is going to go down."
    #Map into the Python wrapper classes
    return parsed.eval_pure()

#Convenience wrappers with more obvious names...
def pure_to_python(obj,uidgen=None,wrap_infix=True):
    '''Maps a set of Pure objects (as translated by the Cython
    wrapper into internal Python objects'''

    if wrap_infix:
        return parse_pure_exp(i2p(obj),uidgen)
    else:
        return parse_pure_exp(obj,uidgen)

def python_to_pure(obj,wrap_infix=True):
    '''Maps internal Python objects into their pure equivelents'''

    if wrap_infix:
        return p2i(obj._pure_())
    else:
        return obj._pure_()

def parse_sexp(code, uid):
    parsed = ParseTree(code)
    parsed.gen_uids(uid)
    evaled = parsed.eval_args()
    return evaled

