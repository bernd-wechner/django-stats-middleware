# Django Stats Middleware

[Django](https://www.djangoproject.com/) is one of the most popular Python web frameworks today.

When a Django site seems slow, it's nice to put some real number to to that. The [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/) is the go-to middleware solution for diagnosing Django performance among other things, but it is rather large, and slow itself, adding significantly to the load time of your pages. So it's in a bit of catch 22 bind for simple performance overviews.

For that reason I wrote this tiny little lightweight piece of middleware that reports at the bottom of every page a single line reporting some basic timing stats. 

- **Total Time**: The time from the request arriving to the response being delivered.
- **Python Time**: Time spent running Python code
- **DB Time**: Time spent waiting on database queries
- **Number of Queries**: The number of database queries run

Where:

​	Python Time + DB Time = Total Time

Here's an example:

![image-20220212213923280](/home/bernd/.var/app/io.typora.Typora/config/Typora/typora-user-images/image-20220212213923280.png)

To use it just put it at the top of your Django Middleware stack:

```python
MIDDLEWARE = (
    'django_stats_middleware.StatsMiddleware',
	...
```

That way Total Time will include the time spent in all other middleware as well as your site code.
