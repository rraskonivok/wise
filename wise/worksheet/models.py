from django.db import models
from django.contrib.auth.models import User

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()

    #The workspace should have a number of EXPORTABLE equations which are higlighted in yellow, these
    #can be pulled into other workspaces and inserted and quered in lookup_identities via sim hashes

    def __unicode__(self):
        return self.name

class MathematicalEquation(models.Model):
    workspace = models.ForeignKey(Workspace, primary_key=True, blank=False,null=False)
    code = models.TextField(max_length=10000,blank=False, null=False)

    followsfrom = models.OneToOneField('self',null=True,blank=True)
    followsby = models.CharField(max_length=200,null=True,blank=True)

# Arity = 1
# f : ( A ) -> Z
class UnaryTransform(models.Model):

    internal = models.CharField(max_length=200, primary_key=True, unique=True)
    module = models.CharField(max_length=200)

    domain_lower = models.FloatField()
    domain_upper = models.FloatField()

    context = models.CharField(max_length=200, null=True)
    pretty = models.CharField(max_length=200)

    def __unicode__(self):
        return self.pretty

# Arity = 2
# f : ( A ,B ) -> Z
class BinaryTransform(models.Model):

    internal = models.CharField(max_length=200, primary_key=True, unique=True)
    module = models.CharField(max_length=200)

    #First Operand
    domain1_lower = models.FloatField()
    domain1_upper = models.FloatField()

    #Second Operand
    domain2_lower = models.FloatField()
    domain2_upper = models.FloatField()

    context = models.CharField(max_length=200, null=True)
    pretty = models.CharField(max_length=200)

    def __unicode__(self):
        return self.pretty

    def __unicode__(self):
        return self.prettytext

# The code certainly supports n-ary operators, at this time I'm
# not sure how to store them in the database though
