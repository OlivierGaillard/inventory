from django.shortcuts import render
from clothes.models import Clothes
from django.views.generic import ListView
from django.shortcuts import render


class ClothesLabelsView(ListView):
    model = Clothes
    template_name = 'labels/clothes_labels.html'
    context_object_name = 'label_clothes'


def clothes_labels(request):
    label_clothes = Clothes.objects.all()
    return render(request, "labels/clothes_labels.html", {'label_clothes': label_clothes})



