from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from archive_manager.models import Location
from archive_manager.serializers import LocationSerializer

from .models import Location, Photo

# Create your views here.
from .forms import PostPhoto


def home(request):
    locations = Location.objects.all()
    return render(request, 'archive_manager/index.html',
                  {'locations': locations})


@csrf_exempt
def location_list(request):
    """
    List all code locations, or create a new location.
    """
    if request.method == 'GET':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def location_detail(request, pk):
    """
    Retrieve, update or delete a location.
    """
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(location, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        location.delete()
        return HttpResponse(status=204)


def post_new(request):
    if request.method == 'GET':
        form = PostPhoto(request.GET, request.FILES)
        return render(request, 'archive_manager/post_edit.html', {'form': form})
    elif request.method == 'POST':
        form = PostPhoto(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
        # if request.user.is_authenticated:
        #     post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse('archive_gallery', args=[post.location.id]))
        else:
            return render(request, 'archive_manager/post_edit.html', {'form': form})


def archive_gallery(request, id):
    location = get_object_or_404(Location, id=id)
    # photos =
    # all_photos = Photo.objects.filter(location=location)
    # archive_photos = [photo for photo in all_photos if photo.photo_location.id == id]
    return render(request, "archive_manager/archive_gallery.html", {
        'location': location,
        'archive_photos': location.photos.all(),
        })
