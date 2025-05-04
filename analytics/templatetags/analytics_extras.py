from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def divided_by(value, arg):
    """将值除以参数"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def percentage_of_max(value, queryset):
    """计算值相对于查询集中最大值的百分比"""
    if not queryset:
        return 0
    
    try:
        # 找出最大值
        max_value = max([item.total_study_time.total_seconds() for item in queryset])
        if max_value <= 0:
            return 0
        return (float(value) / max_value) * 100
    except (ValueError, ZeroDivisionError):
        return 0