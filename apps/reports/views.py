from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reports to be viewed or edited.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """
        Return only reports created by the current user,
        or all reports if user is admin.
        """
        if self.request.user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(created_by=self.request.user)
