from django.shortcuts import render
from clothes.models import Clothes
from django.http import HttpResponse
from django.views.generic import ListView
from django.shortcuts import render
from django.template.loader import get_template
from subprocess import PIPE, Popen
import tempfile
import os
from shoes.models import Shoe
from accessories.models import Accessory
from products.models import Employee, Enterprise

def make_pdf(latex_source):
    with tempfile.TemporaryDirectory() as tempdir:
        process = Popen(
            ['pdflatex', '-output-directory', tempdir],
            stdin=PIPE,
            stdout=PIPE,
        )
        process.communicate(latex_source)
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')
    r.write(pdf)
    return r


    #return HttpResponse(content_type='text/plain', content=rendered_template)

def labels_tex(request, article_type):
    enterprise_of_current_user = Employee.get_enterprise_of_current_user(request.user)
    if article_type == 'Clothes':
        articles = Clothes.objects.filter(product_owner=enterprise_of_current_user)
    elif article_type == 'Shoes':
        articles = Shoe.objects.filter(product_owner=enterprise_of_current_user)
    elif article_type == 'Accessories':
        articles = Accessory.objects.filter(product_owner=enterprise_of_current_user)
    else:
        return HttpResponse("article_type %s inconnu." % article_type)
    total_articles = len(articles)
    template = get_template('labels/labels.tex')
    latex_source = template.render({'articles': articles, 'total_articles':total_articles}).encode('utf-8')
    return make_pdf(latex_source)






