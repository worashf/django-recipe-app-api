from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeAPIViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated users."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """" return serializer class for request. """
        if self.action == "list":
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create recipe """
        serializer.save(user=self.request.user)
