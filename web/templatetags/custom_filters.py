from django import template
import datetime
import os

register = template.Library()


@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def attendance_status(attendance_rec):
    # print('at_rec : ', attendance_rec)
    if attendance_rec is None or attendance_rec.attendanceTime is None:
        return "결근"
    elif attendance_rec.latenessTime is not None:
        return "지각"


@register.filter
def event_type(events, search_to):
    # print('events : ', events)
    search_to = search_to.strftime('%Y-%m-%d') if isinstance(search_to, datetime.date) else search_to
    search_to = datetime.datetime.strptime(search_to, "%Y-%m-%d").date()
    event_types = [(event.event_type, event.start_date, event.end_date) for event in events]
    for event_type, start_date, end_date in event_types:
        start_date = start_date.date()
        end_date = end_date.date()
        # print('start_date', start_date)
        # print('end_date', end_date)
        # print('search_to', search_to)
        if start_date <= search_to <= end_date:
            # print(f'Event: {event_type}, Start date: {start_date}, End date: {end_date}')
            if event_type == "Business":
                return "출장"
            elif event_type == "Holiday":
                return "연차"
            elif event_type == "Family":
                return "반차"
    return None

@register.filter
def attendance_css_class(value):
    if value == "연차":
        return "event-type-holiday"
    elif value == "반차":
        return "event-type-half-refresh"
    elif value == "출장":
        return "event-type-business"
    elif value == "False":
        return "not-offwork-color"
    elif value == "지각":
        return "late-color"
    elif value == "결근":
        return "absence-color"
    else:
        return ""
