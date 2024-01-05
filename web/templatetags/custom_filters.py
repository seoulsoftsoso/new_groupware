from django import template
import os

register = template.Library()


@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def attendance_status(attendance_rec):
    print('at_rec : ', attendance_rec)
    if attendance_rec is None or attendance_rec.attendanceTime is None:
        return "결근"
    elif attendance_rec.latenessTime is not None:
        return "지각"


@register.filter
def event_type(events):
    print('eve : ', events)
    event_types = [event.event_type for event in events]
    print('eve_t : ', event_types)
    if "Business" in event_types:
        return "출장"
    elif "Holiday" in event_types:
        return "연차"
    elif "Family" in event_types:
        return "반차"
    

@register.filter
def attendance_css_class(value):
    if value == "결근":
        return "absence-color"
    elif value == "지각":
        return "late-color"
    elif value == False: # 퇴근 미처리
        return "not-offwork-color"
    elif value == "출장": # 출장
        return "event-type-1"
    elif value == "연차": # 연차
        return "event-type-2"
    elif value == "반차": # 반차
        return "event-type-3"
    else:
        return ""
