from apps.shortener.models import URLCollection


class CurrentCollectionDefault:
    requires_context = True

    def __call__(self, serializer_field):
        context = serializer_field.context
        collection_id = context['request'].path.split("/")[-3]
        return URLCollection.objects.get(id=collection_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__