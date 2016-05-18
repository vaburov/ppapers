import csv
import re
from django.shortcuts import render
from django.utils import timezone
from django.db import models
from django.shortcuts import render, get_object_or_404
from .models import Post
from .forms import PostForm
from .forms import SearchForm
from django import forms
from django.shortcuts import redirect

inittext = 'Please, enter a name or any part of the name.'
init = True

def str_aligned(s1, s2='', tab=20):
    s = s1
    return s+' '*max(1, tab-len(s))+s2+'\n'

# Create your views here.
def post_list(request):
    global text, init
    global csv_officers, csv_intermediaries, csv_entities, csv_addresses, csv_edges
    global officers, intermediaries, entities, addresses, edges
    if init:
        init = False
        csv_officers       = open('blog/static/Officers.csv', 'rt')
        csv_intermediaries = open('blog/static/Intermediaries.csv', 'rt')
        csv_entities       = open('blog/static/Entities.csv', 'rt')
        csv_addresses      = open('blog/static/Addresses.csv', 'rt')
        csv_edges          = open('blog/static/all_edges.csv', 'rt')

        officers       = list(csv.reader(csv_officers, delimiter=','))
        intermediaries = list(csv.reader(csv_intermediaries, delimiter=','))
        entities       = list(csv.reader(csv_entities, delimiter=','))
        addresses      = list(csv.reader(csv_addresses, delimiter=','))
        edges          = list(csv.reader(csv_edges, delimiter=','))

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            text = []
            name = request.POST.get("search", "");

            for person in officers:
                if re.search(name, person[0], re.IGNORECASE):
                    item = []
                    item.append(str_aligned('NAME:', person[0]))
                    item.append(str_aligned('COUNTRY:', person[4]))

                    node_id = person[5]
                    for link in edges:
                        node0, node1 = link[0], link[2]
                        if node_id==node0:
                            found = False
                            found_name = ''

                            for asset in entities:
                                if asset[19]==node1:
                                    item.append(str_aligned(link[1].upper()+':', asset[0]))
                                    found = True
                                    found_name = asset[0]
                                    break;

                            if not found:
                                for addr in addresses:
                                    if addr[5]==node1:
                                        item.append(str_aligned(link[1].upper()+':', addr[0]))
                                        found = True
                                        found_name = addr[0]
                                        break;
                            # search for partners
                            for l in edges:
                                n0, n1 = l[0], l[2]
                                if n1 == node1 and n0 != node0:
                                    # we found a partner
                                    for partner in officers:
                                        if n0 == partner[5]:
                                            item.append(str_aligned("        "+partner[0], '('+l[1].upper()+')', 40))
                                            break;

                    text.append(item)

    else:
        text = [].append([].append(inittext))

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
