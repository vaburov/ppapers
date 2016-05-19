import re
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
import bisect

def get_index(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a):
        return i
    raise ValueError

def str_aligned(s1, s2='', tab=20):
    s = s1
    return s+' '*max(1, tab-len(s))+s2+'\n'

# Create your views here.
def post_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            text = []
            name = request.POST.get("search", "");

            for person in MyGlobals.officers:
                if re.search(name, person[0], re.IGNORECASE):
                    item = []
                    item.append(str_aligned('NAME:', person[0]))
                    item.append(str_aligned('COUNTRY:', person[4]))

                    node_id = int(person[5])
                    try: 
                        i = get_index(MyGlobals.edges, (node_id, "", None))
                    except: 
                        i = len(MyGlobals.edges)

                    while (i < len(MyGlobals.edges) and MyGlobals.edges[i][0] == node_id):
                        node0, edge, node1 = MyGlobals.edges[i]
                        found = False
                        found_name = ''

                        for asset in MyGlobals.entities:
                            if asset[19]==str(node1):
                                item.append(str_aligned(MyGlobals.edges[i][1].upper()+':', asset[0]))
                                found = True
                                found_name = asset[0]
                                break;

                        if not found:
                            for addr in MyGlobals.addresses:
                                if addr[5]==str(node1):
                                    item.append(str_aligned(MyGlobals.edges[i][1].upper()+':', addr[0]))
                                    found = True
                                    found_name = addr[0]
                                    break;

                        be = MyGlobals.back_edges
                        try: 
                            j = get_index(be, (node1, "", None))
                        except: 
                            j = len(be)
                        # search for partners
                        while (j < len(be) and be[j][0] == node1):
                            n0, ed, n1 = be[j]
                            if n1 != node0:
                                # we found a partner
                                for partner in MyGlobals.officers:
                                    if str(n1) == partner[5]:
                                        item.append(str_aligned("        "+partner[0], '('+ed.upper()+')', 40))
                                        break;
                            j += 1
                        i += 1

                    text.append(item)

    else:
        text = [].append([].append(MyGlobals.inittext))

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
