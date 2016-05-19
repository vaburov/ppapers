from django.db import models
from django.db.models.base import ModelBase
import datetime
import csv

class MyGlobals(ModelBase):
    officers        = tuple(csv.reader(open('/home/vaburov/panamapapers/static/Officers.csv', 'rt'), delimiter=','))
    #intermediaries = tuple(csv.reader(open('/home/vaburov/panamapapers/static/Intermediaries.csv', 'rt'), delimiter=','))
    entities        = tuple(csv.reader(open('/home/vaburov/panamapapers/static/Entities.csv', 'rt'), delimiter=','))
    addresses       = tuple(csv.reader(open('/home/vaburov/panamapapers/static/Addresses.csv', 'rt'), delimiter=','))

    edg             = list(csv.reader(open('/home/vaburov/panamapapers/static/all_edges.csv', 'rt'), delimiter=','))
    edges           = tuple(sorted([(int(a),b,int(c)) for [a,b,c] in edg[1:]]))
    back_edges      = tuple(sorted([(int(c),b,int(a)) for [a,b,c] in edg[1:]]))

    inittext = 'Please, enter a name or any part of the name.'

class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=datetime.datetime.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = datetime.datetime.now() 
        self.save()

    def __str__(self):
        return self.title

class Edge(models.Model):
    node1 = models.DecimalField(max_digits=8, decimal_places=0, blank=False, null=True)
    node2 = models.DecimalField(max_digits=8, decimal_places=0, blank=False, null=True)
    edge  = models.TextField()

    #def __unicode__(self):
    #    return "%d %s %d" % (self.node1, self.edge, self.node2)

    #def __str__(self):
    #    return "%d %s %d" % (self.node1, self.edge, self.node2)

    class Meta:
        ordering = ['node2']

class Entity(models.Model):
    name = models.TextField()
    #jurisdiction_description = models.TextField()
    #address = models.TextField()
    node_id = models.DecimalField(max_digits=8, decimal_places=0, blank=False, null=True)

    class Meta:
        ordering = ['node_id']
