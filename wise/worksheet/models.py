from django.db import models
from django.contrib.auth.models import User

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()

    def __unicode__(self):
        return self.name

class RuleSet(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

#Be able to specify order of rules
class Rule(models.Model):
    pure = models.TextField(max_length=10000,blank=False, null=False)
    sexp = models.TextField(max_length=10000,blank=False, null=False)
    set = models.ForeignKey(RuleSet, primary_key=True, blank=False,null=False)

    def __unicode__(self):
        return str(self.set) + ' ' + self.sexp[0:25]

class Cell(models.Model):
    workspace = models.ForeignKey(Workspace, primary_key=True, blank=False,null=False)
    index = models.IntegerField(blank=False,null=False)

    def __unicode__(self):
        return self.workspace.name + ('[%s]' % (self.index))

class Function(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()
    desc = models.CharField(max_length=200)
    notation = models.CharField(max_length=200)
    arity = models.IntegerField()
    symbol1 = models.CharField(max_length=200)
    symbol2 = models.CharField(max_length=200)
    symbol3 = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Symbol(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()
    desc = models.CharField(max_length=200)

    tex = models.TextField(max_length=100,blank=False, null=False)

    numeric = models.BooleanField()
    zero = models.BooleanField()
    positive = models.BooleanField()
    negative = models.BooleanField()
    integer = models.BooleanField()
    even = models.BooleanField()
    odd = models.BooleanField()
    prime = models.BooleanField()
    rational = models.BooleanField()
    real = models.BooleanField()
    complex = models.BooleanField()

    def __unicode__(self):
        return self.name

class MathematicalEquation(models.Model):
    cell = models.ForeignKey(Cell,blank=False,null=False)
    code = models.TextField(max_length=10000,blank=False, null=False)
    followsfrom = models.OneToOneField('self',null=True,blank=True)
    followsby = models.CharField(max_length=200,null=True,blank=True)

    def __unicode__(self):
        return self.cell.workspace.name + ('[%s] -- %s' %
                (self.cell.index, self.code[0:25]))
