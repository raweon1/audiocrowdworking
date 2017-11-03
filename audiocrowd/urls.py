from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^register', views.register, name="register"),
    url(r'^qualification/$', views.qualification_job_view, name="qualification"),
    url(r'^training/$', views.training_job_view, name="training"),
    url(r'^acr/$', views.acr_job_view, name="acr")
]