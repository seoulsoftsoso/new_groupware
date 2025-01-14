#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import threading
import time
import functools
from ast import literal_eval

import schedule

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seoulsoft_mes.settings")

import django
django.setup()

from api.models import EventMaster, UserMaster, Holiday
from datetime import date, timedelta, datetime
from django.db.models import Q


def current_staff_list():
    all_users = UserMaster.objects.filter(is_staff=True).exclude(etc="no_leave").values(
        "id", "username", "employment_date", "birthday"
    )
    create_birthday_events(all_users)
    create_annual_leave_events(all_users)


def create_birthday_events(all_users):
    today = date.today()
    birthday_users = [
        user for user in all_users
        if user['birthday'] and user['birthday'].month == today.month and user['birthday'].day == today.day
    ]

    if not birthday_users:
        print(f"{today} 생일자 없음")
        return []

    for user in birthday_users:
        title = "연차 추가"
        event_type = "plus"
        birthday_formatted = user['birthday'].strftime("%m/%d")
        etc = f"{today.year} 생일연차 ({birthday_formatted})"

        try:
            user_instance = UserMaster.objects.get(id=user['id'])
        except UserMaster.DoesNotExist:
            print(f"UserMaster 조회 실패: {user['id']}")
            continue

        # 중복 여부 확인 (특정 user_id와 생일연차 관련 내용으로 검색)
        if EventMaster.objects.filter(
                Q(create_by=user_instance) & Q(etc__contains=str(today.year)) & Q(etc__contains="생일연차")
        ).exists():
            print(f"이미 생일연차 이벤트가 생성됨: {user['username']} {user['birthday']}")
            continue

        EventMaster.objects.create(
            url='',
            title=title,
            start_date=today,
            end_date=today,
            allDay=0,
            event_type=event_type,
            create_by=user_instance,
            updated_by=user_instance,
            delete_flag="Y",
            period_count=1,
            etc=etc,
            create_at=today,
            update_at=today,
        )
        print(f"{today} 생일연차 생성됨: {user['username']} {user['birthday']}")

    return birthday_users


def create_annual_leave_events(all_users):
    today = date.today()
    check_users = [
        user for user in all_users
        if user['employment_date'] and user['employment_date'].month == today.month and user['employment_date'].day == today.day
    ]

    if not check_users:
        print(f"{today} 연차생성 해당인원 없음")
        return []

    for user in check_users:
        title = "연차 추가"
        event_type = "plus"
        working_years = today.year - user['employment_date'].year
        period_count = Holiday.objects.filter(workYear=working_years).first().law_holiday

        etc = f"{today.year} 연간연차 ({user['employment_date']}, {working_years}년차)"
        user_instance = UserMaster.objects.get(id=user['id'])

        # 중복 여부 확인 (특정 user_id와 연차생성 관련 내용으로 검색)
        if EventMaster.objects.filter(
                Q(create_by=user_instance) & Q(etc__contains=str(today.year)) & Q(etc__contains="연간연차")
        ).exists():
            print(f"이미 올해의 연차가 생성됨: {user['username']} {user['employment_date']}")
            continue

        EventMaster.objects.create(
            url='',
            title=title,
            start_date=today,
            end_date=today,
            allDay=0,
            event_type=event_type,
            create_by=user_instance,
            updated_by=user_instance,
            delete_flag="Y",
            period_count=period_count,
            etc=etc,
            create_at=today,
            update_at=today,
        )
        print(f"{today} 신규 연차 생성됨: {user['username']} {user['employment_date']}")

    return check_users


def db_polling(username):
    current_time = datetime.now()
    print(f"db_polling: {current_time}")
    qs_username = UserMaster.objects.filter(username=username)
    print(f"UserMaster QuerySet: {qs_username}")


def main():
    def db_polling_job():
        db_polling('관리자')

    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()  # (DB가 끊기는 경우 방지)

    schedule.every(20).minutes.do(run_threaded, db_polling_job)  # DB 연결 유지 (DB가 끊기는 경우 방지)
    schedule.every().day.at("00:01").do(run_threaded, current_staff_list)  # 매일 자정에 생일연차 및 연간연차 자동생성
    # schedule.every().day.at("15:06").do(run_threaded, current_staff_list)  # 테스트용
    # schedule.every(5).seconds.do(run_threaded, current_staff_list)  # 테스트용

    while True:
        schedule.run_pending()
        time.sleep(1)
    pass

if __name__ == '__main__':
    main()
