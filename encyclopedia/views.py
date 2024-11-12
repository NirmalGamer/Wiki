import os
from random import randint
from django.urls import reverse
from markdown2 import Markdown
from django.shortcuts import render, HttpResponse, redirect
from django import forms

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(label="Content", widget=forms.Textarea)

class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "pages": util.list_entries()
    })

def page(request, name):
    markdowner = Markdown()
    if util.get_entry(name) != None:
        return render(request, "encyclopedia/pages.html", {
            "body" : markdowner.convert(util.get_entry(name)).splitlines(),
            "title" : name.upper()
        })
    else:
        return HttpResponse("Error File Not Found")

def search(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        if query in util.list_entries():
            return redirect('page', name=query)
        else:
            sub = []
            for i in util.list_entries():
                if query in i:
                    sub.append(i)
            return render(request, "encyclopedia/results.html", {
                "entries": sub,
                "pages": sub,
            })


def create(request):
    if request.method == 'POST':
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            if form.cleaned_data['title'] not in util.list_entries():

                # Save the new page (assuming you're using a simple file system storage)
                with open(f"entries/{title}.md", "w") as file:
                    file.write(content)

                return redirect('page', name=title)
            
            else:
                return render(request, 'encyclopedia/create.html', {
                    'form': form,
                    "status": "ERROR: Name already Exists"
                })

                
    else:
        form = NewPageForm()

    return render(request, 'encyclopedia/create.html', {'form': form})


def edit(request, name):
    filepath = f"entries/{name}.md"

    if request.method == 'POST':
        form = EditPageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']

            # Save the updated content
            with open(filepath, "w") as file:
                file.write(content)

            return redirect('page', name=name)
    else:
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                initial_content = file.read()
            form = EditPageForm(initial={'content': initial_content})
        else:
            form = EditPageForm()

    return render(request, 'encyclopedia/edit.html', {'form': form, 'name': name})

def random(request):
    content = []
    len = 0
    for i in util.list_entries():
        content.append(i)
        len += 1
    choose = randint(0,len - 1)
    return redirect("page", name=content[choose])