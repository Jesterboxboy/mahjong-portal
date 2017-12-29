from django.shortcuts import render, get_object_or_404
from django.utils.translation import get_language
from haystack.forms import ModelSearchForm

from player.models import Player
from rating.models import Rating, RatingResult
from settings.models import City
from tournament.models import Tournament


def home(request):
    rating = Rating.objects.get(type=Rating.INNER)
    rating_results = RatingResult.objects.filter(rating=rating).order_by('place')[:25]

    return render(request, 'website/home.html', {
        'page': 'home',
        'rating_results': rating_results,
        'rating': rating
    })


def about(request):
    template = 'about_en.html'
    if get_language() == 'ru':
        template = 'about_ru.html'

    return render(request, 'website/{}'.format(template), {
        'page': 'about'
    })


def search(request):
    query = request.GET.get('q', '')

    search_form = ModelSearchForm(request.GET, load_all=True)
    results = search_form.search()

    query_list = [x.object for x in results]
    players = [x for x in query_list if x.__class__ == Player]

    rating_results = RatingResult.objects.filter(player__id__in=[x.id for x in players]).order_by('place')

    return render(request, 'website/search.html', {
        'rating_results': rating_results,
        'search_query': query
    })


def city_page(request, slug):
    city = get_object_or_404(City, slug=slug)
    tournaments = Tournament.objects.filter(city=city).order_by('-end_date')
    rating_results = RatingResult.objects.filter(player__city=city).order_by('place')
    return render(request, 'website/city.html', {
        'city': city,
        'rating_results': rating_results,
        'tournaments': tournaments
    })
