from django.shortcuts import render
from datetime import datetime

def index(request):
    is_new_year = datetime.now().day == 1 and datetime.now().month == 1
    context = {'is_new_year': is_new_year}
    return render(request, 'new_year/index.html', context)