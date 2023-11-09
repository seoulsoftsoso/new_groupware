import pandas as pd

from datetime import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



def excel_basic_customer_parser(path):
    """CustomerMaster 위한 엑셀 파서. 필드만 파싱하여 a list of dictionary 반환. 이후 FK에 대한 매핑 해줘야 함."""
    df = pd.read_excel(path)

    # Retrieve data
    items = []
    for i, row in df.iloc[:].iterrows():
        fields = ('code', 'name', 'owner_name', 'business_conditions', 'business_event', 'office_phone', 'office_fax', 'email', )
        item = {}
        for idx, field in enumerate(fields):
            item[field] = row.iloc[idx]

        items.append(item)

    return items

