import reversion
from django.db import models
from django.contrib.auth.models import User

class Workspace(models.Model):
    name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    public = models.BooleanField()

    def __unicode__(self):
        return self.name

class Cell(models.Model):
    workspace = models.ForeignKey(Workspace, blank=False,null=False)
    index = models.IntegerField(blank=False,null=False)

    def __unicode__(self):
        return self.workspace.name + ('[%s]' % (self.index))

class Expression(models.Model):
    cell = models.ForeignKey(Cell,blank=False,null=False)
    #cell = models.ManyToManyField(Cell)

    sexp = models.TextField(max_length=10000,blank=False, null=False)
    annotation = models.TextField(max_length=100)
    index = models.IntegerField(blank=False,null=False)

    def __unicode__(self):
        return self.cell.workspace.name + ('[%s] -- %s' %
                (self.cell.index, self.sexp[0:25]))
