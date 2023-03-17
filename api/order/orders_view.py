from django.db import transaction
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import re

from KPI.kpi_views import kpi_log
from api.models import Orders, OrdersItems, ItemIn, OrdersInItems, ItemMaster
from api.permission import MesPermission
from api.serializers import OrdersSerializer, OrdersItemsSerializer, generate_code, OrdersInItemsSerializer
from api.temp_volt_monitoring.send_mail import send_gmail, send_gmail_pdf
from api.pagination import PostPageNumberPagination5


class OrdersViewSet(viewsets.ModelViewSet):
    class OrdersFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Orders
            fields = ['id', 'code_id']

    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "get_queryset", False)
        qs = Orders.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        if 'last' in self.request.query_params:
            last = self.request.query_params['last']
            if last == 'true':
                last_id = qs.first()  # -id 로 order 를 했기 때문에 last > first

                if last_id == None:
                    qs = qs.none()
                else:
                    qs = qs.filter(id=last_id.id)

                return qs

        if 'in_status' in self.request.query_params:
            in_status = self.request.query_params['in_status']
            if in_status != '':
                if in_status == '미입고':
                    in_status = ''

                qs = qs.filter(in_status=in_status)

        if 'make_from' in self.request.query_params:
            fr_date = self.request.query_params['make_from']
            if fr_date != '':
                qs = qs.filter(created_at__gte=fr_date)

        if 'make_to' in self.request.query_params:
            to_date = self.request.query_params['make_to']
            if to_date != '':
                qs = qs.filter(created_at__lte=to_date)

        if 'mail_from' in self.request.query_params:
            mail_from = self.request.query_params['mail_from']
            if mail_from != '':
                qs = qs.filter(send_date__gte=mail_from)

        if 'mail_to' in self.request.query_params:
            mail_to = self.request.query_params['mail_to']
            if mail_to != '':
                qs = qs.filter(send_date__lte=mail_to)

        return qs

    @transaction.atomic
    def sendmail_to_company(self, request, *args, **kwargs):

        mail_info = dict(gmail_user='greenbi5693@gmail.com', gmail_password='grqsbumhzdmrjeav',
                         sent_from='greenbi5693@gmail.com', send_to='greenbi5693@naver.com',
                         subject="발주서", body="발주서 입니다.")

        send_gmail(mail_info, None)

        return Response({}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def sendmail_to_company_pdf(self, request, *args, **kwargs):
        email_form = re.compile('[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        phone_form = re.compile('\d{2,3}-\d{3,4}-\d{4}')
        customer_email = email_form.search(request.data['customer_email'])
        enter_email = email_form.search(request.data['enter_email'])
        enter_fax = ""
        if phone_form.search(request.data['enter_fax']):
            enter_fax = phone_form.search(request.data['enter_fax']).group()
        enter_call = ""
        if phone_form.search(request.data["enter_call"]):
            enter_call = phone_form.search(request.data['enter_call']).group()
        logo_img = request.data['logo_img']

        if enter_email and customer_email:
            enter_email = enter_email.group()
        else:
            enter_email = ""
            customer_email = ""

        if customer_email:
            customer_email = customer_email.group()
            print(customer_email)
            mail_info = dict(gmail_user='seoulsoftinfo@gmail.com', gmail_password='zwsixkqojsisiqpc',
                             sent_from=enter_email, send_to=customer_email,
                             Cc='yubin.shin@seoul-soft.com', Bcc=enter_email,
                             subject=request.data['enterprise_name'] + " - 발행한 발주서입니다.", enterprise=request.data['enterprise_name'],
                             enter_email=enter_email, enter_fax=enter_fax, enter_call=enter_call, logo_img=logo_img, type="발주서")

            # 'hjlim@seoul-soft.com, greenbi5693@naver.com, ubin1101@gmail.com, ubin1101@naver.com'

            file = request.FILES['file']
            try:
                send_gmail_pdf(mail_info, file)
                return Response('success', status=status.HTTP_201_CREATED)

            except:
                raise ValidationError('관리자에게 문의하세요.')
        else:
            raise ValidationError('거래처 이메일을 확인해 주시기 바랍니다.')


    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)
        if 'itemCnt' in request.data:
            cnt = int(request.data['itemCnt'])
            user = request.user

            item_id = []
            item_detail = []

            item_quantity = []
            item_price = []
            supply_price = []
            surtax = []
            item_supply_total = []

            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)

                item_quantity.append(None)
                item_price.append(None)
                supply_price.append(None)
                surtax.append(None)
                item_supply_total.append(None)

                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.data['item_id[' + str(i) + ']']  # 품번 ID
                item_detail[i] = request.data['item_detail[' + str(i) + ']']  # 품명상세

                item_quantity[i] = request.data['item_quantity[' + str(i) + ']']  # 수량
                item_price[i] = request.data['item_price[' + str(i) + ']']  # 단가
                supply_price[i] = request.data['supply_price[' + str(i) + ']']  # 공급가
                surtax[i] = request.data['surtax[' + str(i) + ']']  # 부가세
                item_supply_total[i] = request.data['item_supply_total[' + str(i) + ']']  # 합계

                item_remarks[i] = request.data['item_remarks[' + str(i) + ']']  # 비고
                item_file[i] = request.data['file[' + str(i) + ']']

                # 발주항목 등록
                row = OrdersItems.objects.create(orders_id=res.data['id'],
                                                 item_id=item_id[i],
                                                 item_detail=item_detail[i],

                                                 quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                                 item_price=(0 if (item_price[i] == '') else item_price[i]),

                                                 supply_price=(0 if (supply_price[i] == '') else supply_price[i]),
                                                 surtax=(0 if (surtax[i] == '') else surtax[i]),
                                                 item_supply_total=(0 if (item_supply_total[i] == '') else item_supply_total[i]),

                                                 remarks=item_remarks[i],
                                                 file=item_file[i],

                                                 created_by=user,
                                                 updated_by=user,
                                                 created_at=user,
                                                 updated_at=user,
                                                 enterprise=request.user.enterprise
                                                 )

                # 미입고 등록
                num = generate_code('I', ItemIn, 'num', user)
                OrdersInItems.objects.create(ins=False,  # 미입고
                                             orders_id=res.data['id'],
                                             orders_item_id=row.id,
                                             num=num,
                                             item_id=item_id[i],
                                             item_detail=item_detail[i],

                                             quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                             item_price=(0 if (item_price[i] == '') else item_price[i]),
                                             supply_price=(0 if (supply_price[i] == '') else supply_price[i]),

                                             surtax=(0 if (surtax[i] == '') else surtax[i]),
                                             item_supply_total=(0 if (item_supply_total[i] == '') else item_supply_total[i]),

                                             in_quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),  # 입고수량
                                             in_date=None,  # 입고일자

                                             created_by=user,
                                             updated_by=user,
                                             created_at=user,
                                             updated_at=user,
                                             enterprise=request.user.enterprise
                                             )


        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)

        if 'send_try' in self.request.data:
            row = Orders.objects.get(pk=kwargs.get('pk'))

            if row:
                from datetime import datetime
                row.send_date = datetime.today().strftime("%Y-%m-%d")
                row.save()

                res.data['send_date'] = datetime.today().strftime("%Y-%m-%d")

        return res

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrdersItemsViewSet(viewsets.ModelViewSet):
    class OrdersItemsFilter(FilterSet):
        class Meta:
            model = OrdersItems
            fields = ['id', 'orders', 'orders_id']

    queryset = OrdersItems.objects.all()
    serializer_class = OrdersItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersItemsFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "get_queryset", False)
        qs = OrdersItems.objects.filter(enterprise=self.request.user.enterprise).order_by('item_id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "create", False)

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrdersInItemsViewSet(viewsets.ModelViewSet):
    class OrdersInItemsFilter(FilterSet):
        class Meta:
            model = OrdersInItems
            fields = ['id', 'orders_id']

    queryset = OrdersInItems.objects.all()
    serializer_class = OrdersInItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersInItemsFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "get_queryset", False)
        qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise).order_by('item_id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "create", False)
        dataLength = int(request.data['dataLength'])

        for nm in range(0, dataLength):
            orders_id = request.data['itemData[' + str(nm) + '][orders]']  # 발주서 ID
            orders_item_id = request.data['itemData[' + str(nm) + '][orders_item]']  # 주문항목 ID
            item_id = request.data['itemData[' + str(nm) + '][item]']  # 품번 ID
            item_detail = request.data['itemData[' + str(nm) + '][item_detail]']  # 품명상세
            item_price = request.data['itemData[' + str(nm) + '][item_price]']  # 단가
            location = request.data['itemData[' + str(nm) + '][location]']  # 단가
            if item_price == '': item_price = 0

            quantity = request.data['itemData[' + str(nm) + '][quantity]']  # 발주수량
            if quantity == '': quantity = 0

            # supply_price = request.data['itemData[' + str(nm) + '][supply_price]']  # 공급가
            # if supply_price == '': supply_price = 0
            #
            # surtax = request.data['itemData[' + str(nm) + '][surtax]']  # 부가세
            # if surtax == '': surtax = 0
            #
            # item_supply_total = request.data['itemData[' + str(nm) + '][item_supply_total]']  # 합계
            # if item_supply_total == '': item_supply_total = 0

            in_will_quantity = request.data['itemData[' + str(nm) + '][in_will_quantity]']  # 입고수량
            if in_will_quantity == '': in_will_quantity = 0

            in_will_faulty = request.data['itemData[' + str(nm) + '][in_will_faulty]']  # 입고할 불량수량
            if in_will_faulty == '': in_will_faulty = 0

            from datetime import datetime
            in_date = request.data['itemData[' + str(nm) + '][in_date]']  # 입고일자
            if in_date == '':
                in_date = datetime.today().strftime("%Y-%m-%d")

            item_created_at = request.data['itemData[' + str(nm) + '][item_created_at]']  # 자재 생산일자
            if item_created_at == '':
                item_created_at = None

            etc = request.data['itemData[' + str(nm) + '][etc]']  # 비고

            user = request.user
            num = generate_code('I', ItemIn, 'num', user)

            # 미입고 모두 삭제
            qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise).all()
            qs = qs.filter(orders_item_id=orders_item_id, ins=False)
            for row in qs:
                row.delete()

            orders = Orders.objects.get(id=orders_id)
            customer = orders.code

            # 재고입고 진행
            current_amount = ItemMaster.objects.get(pk=item_id).stock

            item_in = ItemIn.objects.create(
                num=num,  # 입고번호
                item_id=item_id,  # 품번
                in_at=in_date,  # 입고일자
                item_created_at=item_created_at,  # 자재생산일자
                current_amount=float(current_amount),  # 현재재고
                receive_amount=float(in_will_quantity) + float(in_will_faulty),  # 입고할 수량
                package_amount=float(in_will_quantity),  # 입고할 수량
                in_faulty_amount=float(in_will_faulty),  # 입고할 불량수량
                in_price=float(item_price),  # 입고단가
                customer=customer,  # 거래처
                location_id=location,
                created_by=user,
                updated_by=user,
                created_at=user,
                updated_at=user,
                enterprise=request.user.enterprise
            )

            """
            QR 입고 처리
            키로 사용할 dict를 생성하여 카테고리와 함께 넘김 
            """

            try:
                dict_qr = {'id': item_in.id, 'item_id': item_id}

                from api.QRCode.QRCodeManager import QRCodeGen
                # qrcodePath = QRCodeGen(dict_qr, 'ItemIn')
                filename = QRCodeGen(dict_qr, 'ItemIn')

                print(filename)

                # instance['qr_path'] = filename
                item_in.qr_path = filename
                item_in.save()

            except:
                raise ValidationError('QR Code 생성에러. 관리자에게 문의하세요.')

            # 아이템에 QR코드 이미지 경로 업데이트
            # ex : previous.item.qrpath = qrcodePath
            # ex : previous.item.save()


            # 품목마스터 현재고 재계산
            item = ItemMaster.objects.get(pk=item_id)
            item.stock = item.stock + float(in_will_quantity)
            item.save()

            # 입고내용 등록
            OrdersInItems.objects.create(ins=True,  # 입고
                                         orders_id=orders_id,
                                         orders_item_id=orders_item_id,
                                         num=num,
                                         item_id=item_id,
                                         item_detail=item_detail,
                                         item_price=float(item_price),

                                         quantity=float(quantity),  # 발주수량
                                         # supply_price=supply_price,
                                         # surtax=surtax,
                                         # item_supply_total=item_supply_total,

                                         in_quantity=float(in_will_quantity),
                                         in_faulty=float(in_will_faulty),

                                         in_date=in_date,
                                         item_created_at=item_created_at,
                                         location_id=location,
                                         etc=etc,

                                         item_in_id=item_in.id,

                                         created_by=user,
                                         updated_by=user,
                                         created_at=user,
                                         updated_at=user,
                                         enterprise=request.user.enterprise
                                         )

            orders_item = OrdersItems.objects.get(id=orders_item_id)

            # 입고한 수량 / 입고할 수량 변경
            in_ed_quantity = orders_item.in_ed_quantity
            to_in_quantity = in_ed_quantity + float(in_will_quantity)
            orders_item.in_ed_quantity = to_in_quantity
            orders_item.in_will_quantity = 0

            # 불량 입고한 수량 / 불량 입고할 수량 변경
            in_ed_faulty = orders_item.in_ed_faulty
            to_in_faulty = in_ed_faulty + float(in_will_faulty)
            orders_item.in_ed_faulty = to_in_faulty
            orders_item.in_will_faulty = 0

            orders_item.in_date = None  # 입고일자
            orders_item.item_created_at = None  # 자재생산일자
            orders_item.location = orders_item.location  # 자재위치
            orders_item.etc = ''  # 비고

            # 미입고 계산
            a = orders_item.quantity  # 발주수량
            b = orders_item.in_ed_quantity  # 출하된 수량
            remain = (a - b) if ((a - b) >= 0) else 0  # 미입고 수량 (남은 수량)

            # if remain == 0:
            #     orders_item.in_status = True  # 입고완료
            # else:
            #     orders_item.in_status = False  # 미입고

            # 미입고 : 입고한 수량 = 0
            # 입고완료 : 발주 수량 <= 입고한 수량
            # 일부입고 : 그 이외는 일부입고

            if orders_item.in_ed_quantity == 0:
                orders_item.in_status = ''

            elif orders_item.quantity <= orders_item.in_ed_quantity:
                orders_item.in_status = '입고완료'

            else:
                orders_item.in_status = '일부입고'

            orders_item.save()

            if remain > 0:  # 미입고 내용등록
                OrdersInItems.objects.create(ins=False,  # 미입고
                                             orders_id=orders_id,
                                             orders_item_id=orders_item_id,
                                             num=num,
                                             item_id=item_id,
                                             item_detail=item_detail,
                                             item_price=float(item_price),

                                             quantity=float(quantity),  # 발주수량
                                             # supply_price=supply_price,  # 공급가
                                             # surtax=surtax,  # 부가세
                                             # item_supply_total=item_supply_total,  # 합계

                                             in_quantity=float(remain),  # 입고수량 ? 미입고수량
                                             in_date=None,  # 입고일자
                                             item_created_at=None,  # 자재생산일자

                                             created_by=user,
                                             updated_by=user,
                                             created_at=user,
                                             updated_at=user,
                                             enterprise=request.user.enterprise
                                             )

        orders_status_check(self, orders_id)  # 입고현황 체크

        queryset = self.filter_queryset(self.get_queryset()).filter(enterprise=self.request.user.enterprise,
                                                                    orders_id=orders_id).order_by('item_id')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "destroy", False)

        dataLength = int(request.data['dataLength'])
        if kwargs['pk'] == '0':  # 출하등록 취소인 경우
            for nm in range(0, dataLength):
                orders_id = request.data['itemData[' + str(nm) + '][orders]']  # 발주서 ID
                orders_item_id = request.data['itemData[' + str(nm) + '][orders_item]']  # 발주항목 ID
                item_id = request.data['itemData[' + str(nm) + '][item]']  # 품번 ID
                item_detail = request.data['itemData[' + str(nm) + '][item_detail]']  # 품명상세
                item_price = request.data['itemData[' + str(nm) + '][item_price]']  # 단가
                if item_price == '': item_price = 0

                quantity = request.data['itemData[' + str(nm) + '][quantity]']  # 발주수량
                if quantity == '': quantity = 0

                # supply_price = request.data['itemData[' + str(nm) + '][supply_price]']  # 공급가
                # if supply_price == '': supply_price = 0
                #
                # surtax = request.data['itemData[' + str(nm) + '][surtax]']  # 부가세
                # if surtax == '': surtax = 0
                #
                # item_supply_total = request.data['itemData[' + str(nm) + '][item_supply_total]']  # 합계
                # if item_supply_total == '': item_supply_total = 0

                in_quantity = request.data['itemData[' + str(nm) + '][in_quantity]']  # 입고수량
                if in_quantity == '': in_quantity = 0

                in_faulty = request.data['itemData[' + str(nm) + '][in_faulty]']  # 불량수량
                if in_faulty == '': in_faulty = 0

                orders_in_item_id = request.data['itemData[' + str(nm) + '][orders_in_item]']  # 입고항목 ID
                item_num = request.data['itemData[' + str(nm) + '][item_num]']  # 입고번호

                user = request.user
                num = generate_code('O', ItemIn, 'num', user)

                # 입고등록 취소
                ins = OrdersInItems.objects.get(id=orders_in_item_id)
                if ins:
                    ins.delete()

                # 재고입고 취소
                qs = ItemIn.objects.filter(id=ins.item_in_id)
                if qs:
                    item_in_row = qs.get(id=ins.item_in_id)
                    if item_in_row:
                        item_in_row.delete()

                # 발주항목 남은 재고량 재계산
                orders_item = OrdersItems.objects.get(id=float(orders_item_id))

                in_ed_quantity = orders_item.in_ed_quantity
                to_in_quantity = in_ed_quantity - float(in_quantity)
                orders_item.in_ed_quantity = to_in_quantity

                in_ed_faulty = orders_item.in_ed_faulty
                to_in_ed_faulty = in_ed_faulty - float(in_faulty)
                orders_item.in_ed_faulty = to_in_ed_faulty

                # 품목마스터 현재고 재계산
                item = ItemMaster.objects.get(pk=item_id)
                item.stock = item.stock - float(in_quantity)
                item.save()

                # 미입고 모두 삭제
                qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise).all()
                qs = qs.filter(orders_item_id=orders_item_id, ins=False)
                for row in qs:
                    row.delete()

                # 미입고 계산
                a = orders_item.quantity  # 발주수량
                b = orders_item.in_ed_quantity  # 입고된 수량
                remain = (a - b) if ((a - b) >= 0) else 0  # 미입고 수량 (남은 수량)


                # if remain == 0:
                #     orders_item.in_status = True  # 입고완료
                # else:
                #     orders_item.in_status = False  # 미입고


                # 미입고 : 입고한 수량 = 0
                # 입고완료 : 발주 수량 <= 입고한 수량
                # 일부입고 : 그 이외는 일부입고

                if orders_item.in_ed_quantity == 0:
                    orders_item.in_status = ''

                elif orders_item.quantity <= orders_item.in_ed_quantity:
                    orders_item.in_status = '입고완료'

                else:
                    orders_item.in_status = '일부입고'

                orders_item.save()

                if remain > 0:  # 미입고 내용등록
                    OrdersInItems.objects.create(ins=False,  # 미입고
                                                 orders_id=orders_id,
                                                 orders_item_id=orders_item_id,
                                                 num=num,
                                                 item_id=item_id,
                                                 item_detail=item_detail,
                                                 item_price=float(item_price),

                                                 quantity=float(quantity),  # 발주수량
                                                 # supply_price=supply_price,  # 공급가
                                                 # surtax=surtax,  # 부가세
                                                 # item_supply_total=item_supply_total,  # 합계

                                                 in_quantity=float(remain),  # 입고수량 ? 미입고수량
                                                 in_date=None,  # 입고일자
                                                 item_created_at=None,  # 자재생산일자

                                                 created_by=user,
                                                 updated_by=user,
                                                 created_at=user,
                                                 updated_at=user,
                                                 enterprise=request.user.enterprise
                                                 )

            orders_status_check(self, orders_id)  # 입고현황 체크

            queryset = self.filter_queryset(self.get_queryset()).filter(enterprise=self.request.user.enterprise,
                                                                        orders_id=orders_id).order_by('item_id')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().destroy(request, request, *args, **kwargs)



def orders_status_check(self, _id):
    OrdersItems_qs = OrdersItems.objects.filter(orders_id=_id)

    cnt = OrdersItems_qs.count()
    ok_in = 0  # 각 항목의 '입고완료' 된 수
    no_in = 0  # 각 항목의 '미입고' 된 수

    for row in OrdersItems_qs:

        # 방어 코드 : '미입고', '일부입고', '입고완료' 가 아닌 경우는 모두 미입고로 처리
        if row.in_status == '' or row.in_status == '입고완료' or row.in_status == '일부입고':
            pass
        else:
            row.in_status = ''
            row.save()


        if row.in_status == '입고완료':
            ok_in = ok_in + 1

        if row.in_status == '':
            no_in = no_in + 1

    orders = Orders.objects.get(id=_id)
    if orders:
        if ok_in == cnt:
            orders.in_status = '입고완료'

        elif no_in == cnt:
            orders.in_status = ''  # 미입고

        else:
            orders.in_status = '일부입고'

        orders.save()




































