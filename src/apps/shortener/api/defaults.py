from apps.shortener.models import URLCollection, URL


class CurrentCollectionDefault:
    requires_context = True

    def __call__(self, serializer_field):
        context = serializer_field.context
        collection_id = context['request'].path.split("/")[-3]
        return URLCollection.objects.get(id=collection_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__

class CurrentURLDefault:
    requires_context = True

    def __call__(self, serializer_field):
        context = serializer_field.context
        url_id = context['request'].path.split("/")[-3]
        return URL.objects.get(id=url_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__