from django import template
from django.db.models import Count

from reports.models import Report

register = template.Library()


@register.simple_tag(takes_context=True)
def get_reports_count_per_type(context):
    project = context['project']
    counts = project.reports.values('type') \
        .annotate(total=Count('type')).order_by('type')
    total_count = project.reports.count()
    return [(Report.TypeChoices(row['type']).label, row['total'], round(row['total'] / total_count * 100))
            for row in counts]
