from django.utils import timezone


def post_filter(posts):
    return posts.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')
