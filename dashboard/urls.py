from django.urls import path

from dashboard.views import DashboardSummaryView, DashboardAdditionsPrintView


urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path(
        "dashboard/print-additions/",
        DashboardAdditionsPrintView.as_view(),
        name="dashboard-print-additions",
    ),
]
