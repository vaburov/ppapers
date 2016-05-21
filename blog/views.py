import re
import datetime
import bisect
from django.shortcuts import render
from django.utils import timezone
from django.db import models
from django.shortcuts import render, get_object_or_404
from .models import MyGlobals
from .models import Post
from .forms import PostForm
from .forms import SearchForm
from django import forms
from django.shortcuts import redirect

class Address:
    def __init__(self, address, addr_id):
        self.address = address
        self.addr_id = addr_id
        self.owners = []

class Person:
    def __init__(self, name, country, p_id):
        self.name = name
        self.country = country
        self.p_id = p_id
        self.assets = []
        self.address = Address('',0)

class Asset:
    def __init__(self, asset, a_id):
        self.asset = asset
        self.a_id = a_id
        self.owners = []

# Create your views here.
def post_list(request):
    text = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            text.append([].append(MyGlobals.inittext))
            query = request.POST.get("search", "")
            time = datetime.datetime.now()
            name_list = []

            # search for the candidates
            """
            for lastname, name, country, p_id in MyGlobals.lastnames[ bisect.bisect_left(MyGlobals.lastnames, (query.upper(), '', '', None)): ] :
                if re.search(query.upper(), lastname, re.IGNORECASE):
                    name_list.append( Person(name +' ' + lastname + ' FAST!', country, p_id))
                else:
                    break
                if len(name_list) >= 50:
                    break
            """

            for item in MyGlobals.officers:
                if re.search(query, item[0], re.IGNORECASE):
                    name_list.append( Person(item[0], item[4], int(item[5])) )
                if len(name_list) >= 50:
                    break

            for name in name_list:
                for person_id, edge, rel_id in MyGlobals.edges[bisect.bisect_left(MyGlobals.edges, (name.p_id, '', None)):]:
                    if person_id != name.p_id: break

                    asset_found = False
                    for asset_id, asset_name in MyGlobals.entities[bisect.bisect_left(MyGlobals.entities, (rel_id, '') ):]:
                        if asset_id != rel_id:
                            break;
                        ast = Asset( asset_name, rel_id )

                        for asst_id, ed, partner_id in MyGlobals.back_edges[bisect.bisect_left(MyGlobals.back_edges, (ast.a_id, '', None)):]:
                            if asst_id != ast.a_id: break
                            if partner_id == person_id: continue
                            p_id, partner_name = MyGlobals.nameid[bisect.bisect_left(MyGlobals.nameid, (partner_id,''))]
                            if (p_id == partner_id):
                                ast.owners.append((partner_name, ed))
                        name.assets.append(ast)
                        asset_found = True
                        break

                    if not asset_found:
                        for addr_id, addr_text in MyGlobals.addresses[bisect.bisect_left(MyGlobals.addresses, (rel_id, '')):]:
                            if addr_id==rel_id:
                               name.address = Address( addr_text, addr_id )
                               for addr_id, ed, partner_id in MyGlobals.back_edges[bisect.bisect_left(MyGlobals.back_edges, (name.address.addr_id, '', None)):]:
                                   if addr_id != name.address.addr_id: break
                                   if partner_id == person_id: continue
                                   p_id, partner_name = MyGlobals.nameid[bisect.bisect_left(MyGlobals.nameid, (partner_id,''))]
                                   if (p_id == partner_id):
                                        name.address.owners.append((partner_name, ed))
                               break

            for name in name_list:
                item = []
                item.append('<b>name:</b> ' + name.name + '<br>')
                item.append('<b>country:</b> ' + name.country + '<br>')

                li = ''
                for owner, ed in name.address.owners:
                    li += '<li>' + owner + ' (' + ed + ')</li>'
                if li != '':
                    li = ' <b>in company with:</b> <ul>' + li + '</ul>'
                else:
                    li = '<br>'
                item.append('<b>address:</b> ' + name.address.address + li)

                for asset in name.assets:
                    li = ''
                    for owner, ed in asset.owners:
                        li += '<li>' + owner + ' (' + ed + ')</li>'
                    if li != '':
                        li = ' <b>in company with:</b> <ul>' + li + '</ul>'
                    else:
                        li = '<br>'
                    item.append('<b>asset:</b> ' + asset.asset + li)

                item.append('<hr>')
                text.append(item)
            #endfor
            delta = datetime.datetime.now()-time
            item.append(str(len(name_list)) + " entries found in " + str(delta.seconds) + '.' + str(delta.microseconds/1000) + ' seconds')
        else: #form is not valid
            item = []
            item.append(MyGlobals.inittext)
            text.append(item)
    else: # request.method is not "POST"
        item = []
        item.append(MyGlobals.inittext)
        text.append(item)

    form = SearchForm(auto_id=False)
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'form': form, 'text': text, 'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('blog.views.post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})
