from django import template

register = template.Library()

@register.filter
def divided_by(value, divisor):
    """
    将值除以指定的除数
    用法: {{ value|divided_by:60 }}
    """
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def percentage_of_max(value, queryset):
    """
    计算值在查询集中的百分比
    用法: {{ analytics.total_study_time.total_seconds|percentage_of_max:topic_analytics }}
    """
    try:
        max_value = max([item.total_study_time.total_seconds() for item in queryset], default=0)
        if max_value <= 0:
            return 0
        return (float(value) / max_value) * 100
    except (ValueError, ZeroDivisionError, TypeError, AttributeError):
        return 0