'''
Created on 7 May.,2018

Django Stats Middleware

@author: Bernd Wechner, based on an old snippet here: https://code.djangoproject.com/wiki/PageStatsMiddleware
@status: Beta - works and is in use on a dedicated project.

Inserts some basic performance stats just prior to the </body> tag in the response of every page served.

To use, add it to the MIDDLEWARE list in settings.py as follows:

MIDDLEWARE = (
    'django_stats_middleware.StatsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware'    
)

Can be easily tweaked below to deliver whatever stats you like.

This information cannot be delivered to pages through the template context because timing information isn't 
collected until the whole template is already rendered. To wit, it is patched into the content just above 
the </body> tag. If your page has no such tag, stats won't appear on it of course.

This of course, is primarily a debugging tool. And hence does nothing if settings.DEBUG is False.
It's a very very lightweight reporter and you'll get all this info and more from the Django Debug Toolbar:

    https://django-debug-toolbar.readthedocs.io/en/latest/
'''

# Python Imports
import re

from time import time
from operator import add
from functools import reduce

# Django Imports
from django.db import connection
from django.conf import settings

class StatsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)

        # get number of db queries before we do anything
        n = len(connection.queries)

        # time the view
        start = time()
        response = self.get_response(request)
        total_time = time() - start

        # compute the db time for the queries just run
        db_queries = len(connection.queries) - n
        if db_queries:
            db_time = reduce(add, [float(q['time'])
                                   for q in connection.queries[n:]])
        else:
            db_time = 0.0

        # and backout python time
        python_time = total_time - db_time
        
        stats = br''.join((br'<div id="stats" style="margin-top:1ex"><table><tr>'
                           br'<td><b>STATS:</b></td>',
                           br'<td style="padding-left: 5ch;">Total Time:</td><td>', "{:.1f} ms".format(total_time*1000).encode(), br'</td>',
                           br'<td style="padding-left: 5ch;">Python Time:</td><td>', "{:.1f} ms".format(python_time).encode(), br'</td>',
                           br'<td style="padding-left: 5ch;">DB Time:</td><td>', "{:.1f} ms".format(db_time).encode(), br'</td>',
                           br'<td style="padding-left: 5ch;">Number of Queries:</td><td>', "{:,}".format(db_queries).encode(), br'</td>', 
                           br'</tr></table></div>\1'))

        # Insert the stats just prior to the body close tag (we need to update the Content-Length header or browser won't render it all.
        if response and getattr(response, 'content', False):
            response.content = re.sub(br"(</body>)", stats, response.content, flags=ref.RegexFlag.IGNORECASE)
            response['Content-Length'] = str(len(response.content))

        return response
    