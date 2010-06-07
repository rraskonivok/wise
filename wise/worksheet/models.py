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

class Cell(models.Model):
    workspace = models.ForeignKey(Workspace, primary_key=True, blank=False,null=False)
    index = models.IntegerField(blank=False,null=False)

    def __unicode__(self):
        return self.workspace.name + ('[%s]' % (self.index))

class MathematicalEquation(models.Model):
    cell = models.ForeignKey(Cell,blank=False,null=False)
    code = models.TextField(max_length=10000,blank=False, null=False)
    followsfrom = models.OneToOneField('self',null=True,blank=True)
    followsby = models.CharField(max_length=200,null=True,blank=True)

    def __unicode__(self):
        return self.cell.workspace.name + ('[%s] -- %s' %
                (self.cell.index, self.code[0:25]))
