from django import template
import os

register = template.Library()


@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def attendance_status(attendance_rec):
    if attendance_rec is None or attendance_rec.attendanceTime is None:
        return "결근"
    elif attendance_rec.latenessTime is not None:
        return "지각"
    

@register.filter
def attendance_css_class(value):
    if value == "결근":
        return "absence-color"
    elif value == "지각":
        return "late-color"
    elif value == False: # 퇴근 미처리
        return "not-offwork-color"
    elif value == "Business": # 출장
        return "event-type-1"
    elif value == "Holiday": # 연차
        return "event-type-2"
    elif value == "Family": # 반차
        return "event-type-3"
    else:
        return ""
