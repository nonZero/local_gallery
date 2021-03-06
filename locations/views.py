import operator
from functools import reduce

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import html
from django.utils.html import linebreaks
from django.views.generic import CreateView, DetailView
from rest_framework import generics

from locations.forms import PostPhoto, LocationForm
from locations.serializers import LocationSerializer, \
    LocationPhotoSerializer, PhotoSerializer
from locations.models import Photo, Location
from projects.models import Project


def post_new(request):
    if request.method == 'POST':
        # if request.user.is_authenticated:
        #     post.author = request.user
        form = PostPhoto(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            if request.is_ajax():
                return JsonResponse({})
            return redirect('archive_gallery', post.location.id)
        if request.is_ajax():
            return JsonResponse({'errors': form.errors.get_json_data()},
                                status=400)
    else:
        form = PostPhoto()

    return render(request, 'general/post_edit.html', {
        'form': form,
    })


class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    form_class = PostPhoto

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['location'].queryset = self.project.locations.all()
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect(form.instance.location)


class LocationDetailView(DetailView):
    model = Location

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.project = get_object_or_404(Project, slug=kwargs['slug'],
                                         pk=self.object.project.pk)
        return super().dispatch(request, *args, **kwargs)


def create_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            # TODO: check if is in Israel
            point = Point([form.cleaned_data['lng'], form.cleaned_data['lat']])
            form.instance.point = point
            location = form.save()
            if request.is_ajax():
                return JsonResponse({
                    'name': html.escape(location.name),
                    'info': linebreaks(location.information),
                    'lat': format(location.point.coords[1], ".5f"),
                    'lng': format(location.point.coords[0], ".5f"),
                })
            return redirect("home")
    else:
        form = LocationForm()

    return render(request,
                  'general/templates/locations/location_form.html', {
        'form': form,
    })


class LocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        project = self.kwargs.get('pj_id')
        queryset = self.queryset.filter(project=project)
        return queryset

    def perform_create(self, serializer):
        project = Project.objects.all().filter(id=self.kwargs.get('pj_id'))[0]
        serializer.save(project=project)


class LocationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        project = self.kwargs.get('pj_id')
        id = self.kwargs.get('pk')
        queryset = self.queryset.filter(id=id, project=project)
        return queryset


class LocationPhotoList(generics.ListCreateAPIView):
    queryset = Photo.objects.all()
    serializer_class = LocationPhotoSerializer

    def get_related_project_id(self, location_id):
        return Location.objects.filter(id=location_id).values_list('project',
                                                                   flat=True)

    def get_queryset(self):
        location_id = self.kwargs.get('pk')
        project_id = self.kwargs.get('pj_id')
        if project_id in self.get_related_project_id(location_id):
            queryset = self.queryset.filter(location_id=location_id)
        else:
            queryset = Photo.objects.none()
        return queryset

    def perform_create(self, serializer):
        location = Location.objects.all().filter(id=self.kwargs.get('pk'))[0]
        serializer.save(location=location)


class PhotoList(generics.ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_locations(self, project_id):
        return Location.objects.filter(project=project_id).values_list('id',
                                                                       flat=True)

    def get_queryset(self):
        project_id = self.kwargs.get('pj_id')
        queryset = self.queryset.filter(reduce(operator.or_,
                                               (Q(location_id=id) for id in
                                                self.get_locations(
                                                    project_id))))
        return queryset


class PhotoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_related_project_id(self, location_id):
        return Location.objects.filter(id=location_id).values_list('project',
                                                                   flat=True)

    def get_related_location_id(self, photo_id):
        return Photo.objects.filter(id=photo_id).values_list('location',
                                                             flat=True)

    def get_queryset(self):
        photo_id = self.kwargs.get('pk')
        project_id = self.kwargs.get('pj_id')
        if project_id in self.get_related_project_id(
                self.get_related_location_id(photo_id)[0]):
            queryset = self.queryset.filter(id=photo_id)
        else:
            queryset = Photo.objects.none()
        return queryset
