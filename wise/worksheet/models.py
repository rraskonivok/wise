from django.db import models
from django.contrib.auth.models import User

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()

    #The workspace should have a number of EXPORTABLE equations which are higlighted in yellow, these
    #can be pulled into other workspaces and inserted and quered in lookup_identities via sim hashes

#    def __unicode__(self):
#        return self.name

class Equation(models.Model):
    workspace = models.ForeignKey(Workspace,blank=False,null=False)
    name = models.CharField(max_length=10000)
    followsfrom = models.OneToOneField('self',null=True,blank=True)
    followsby = models.CharField(max_length=200,null=True,blank=True)

#    def __unicode__(self):
#        return self.name

#Statements of the form {n is integer} , x >0 ...
#Charactersitics of the workspace... physical quanities... sig figures

class Assumption(models.Model):
    workspace = models.ForeignKey(Workspace,blank=False,null=False)

#Ad-hoc statements created to simplify equations ... k = (a^2+b^2+7)
class References(models.Model):
    workspace = models.ForeignKey(Workspace,blank=False,null=False)

class MathematicalObject(models.Model):
    internalname = models.CharField(max_length=200)
    prettyname = models.CharField(max_length=200)
    arguments = models.IntegerField(max_length=3)

#    def __unicode__(self):
#        return self.prettyname

class MathematicalTransform(models.Model):
    first = models.CharField(max_length=200)
    second = models.CharField(max_length=200)
    context = models.CharField(max_length=200)
    prettytext = models.CharField(max_length=200)
    internal = models.CharField(max_length=200,primary_key=True)

#    def __unicode__(self):
#        return self.prettytext

class MathematicalIdentity(models.Model):
    first = models.CharField(max_length=200)
    prettytext = models.CharField(max_length=200)
    internal = models.CharField(max_length=200,primary_key=True)

#    def __unicode__(self):
#        return self.prettytext

#Identites are for SINGLE elements

#Identites are for SINGLE elements

#class MathematicalDefinition
#class MathematicalTheorem

#There should exisit context free transforms such as substituting one expression in another and context-sensitive transforms such as factoring inside an addition statement or combining exponents

#Theorems should provide either new expressions or new assumptions, references

#Definitions should be one-to-one mappings between high-level objects and low-level objects


