import graphene
from graphene_django.types import DjangoObjectType
import requests
import json
import environ
from datetime import datetime, date
from requests.structures import CaseInsensitiveDict
from .models import Zahialga, ZahialgaNom, QpayToken, ZahialgaDeepLink, ZahialgaHural
from apps.nom.models import Nom
from graphql_jwt.decorators import login_required

env = environ.Env()
environ.Env.read_env()

class QpayEnv(object):
    username = ""
    password = ""
    invoice_code = ""
    url = ""
    token = ""

def resolve_qpay_env_data():
            
    qpayEnv = QpayEnv()
    
    # Load environment variables
    qpayEnv.username = env('QPAY_USERNAME')
    qpayEnv.password = env('QPAY_PASSWORD')
    qpayEnv.invoice_code = env('QPAY_INVOICE_CODE')
    qpayEnv.url = env('QPAY_URL')
    
    def fetch_and_save_token():
        """Fetch and save a new token from QPay API."""
        auth_url = f"{qpayEnv.url}/auth/token"
        try:
            auth_resp = requests.post(auth_url, auth=(qpayEnv.username, qpayEnv.password))
            auth_resp.raise_for_status()
            json_data = auth_resp.json()

            token = QpayToken(
                token_type=json_data.get('token_type'),
                refresh_expires_in=json_data.get('refresh_expires_in'),
                access_token=json_data.get('access_token'),
                expires_in=json_data.get('expires_in'),
                refresh_token=json_data.get('refresh_token'),
            )
            token.save()
            return token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching token: {e}")
    
    # Retrieve the latest token
    token = QpayToken.objects.last()

    if not token:
        token = fetch_and_save_token()

    # Check token validity
    refresh_expires_at = datetime.fromtimestamp(token.refresh_expires_in)
    if (refresh_expires_at - datetime.now()).total_seconds() < 10800:  # Less than 3 hours
        token = fetch_and_save_token()

    # Set the valid token
    qpayEnv.token = token.access_token
    
    return qpayEnv

class ZahialgaType(DjangoObjectType):
    class Meta:
        model = Zahialga

class ZahialgaDeepLinkType(DjangoObjectType):
    class Meta:
        model = ZahialgaDeepLink
        fields = ["id", "zahialga", "name", "logo", "link"]

class ZahialgaNomType(DjangoObjectType):
    class Meta:
        model = ZahialgaNom
        fields = ["id", "zahialga", "nom", "une"]
        
class ZahialgaHuralType(DjangoObjectType):
    class Meta:
        model = ZahialgaHural
        fields = ["id", "zahialga", "mute_all"]        

class ZahialgaNomInputType(graphene.InputObjectType):
    nom = graphene.ID(required=True)
    une = graphene.Int()
    
class TotalPaidUniinDunType(graphene.ObjectType):
    zahialga = graphene.List(ZahialgaType)
    total = graphene.Int()

class Query(graphene.ObjectType):
    all_zahialga = graphene.List(ZahialgaType)
    niit_orlogo = graphene.Field(
        TotalPaidUniinDunType,
        start_date=graphene.Date(required=True),
        end_date=graphene.Date(required=True),
    )
    
    @login_required
    def resolve_niit_orlogo(self, info, start_date, end_date):
        
        za = Zahialga.calculate_total_paid_uniin_dun(start_date, end_date)
        
        return TotalPaidUniinDunType(zahialga=za[0], total=za[1])
    
    def resolve_all_zahialga(self, info):
        return Zahialga.objects.all()
    
class CreateZahialga(graphene.Mutation):
    class Arguments:
        utas = graphene.Int(required=False)
        ner = graphene.String(required=False)
        hend = graphene.String(required=False)
        jil = graphene.String(required=True)
        huis = graphene.String(required=True)
        torson_ognoo = graphene.Date(required=True)
        is_online = graphene.Boolean(required=True)
        nom = graphene.List(ZahialgaNomInputType, required=True)
        
    success = graphene.Boolean(default_value=False)
    qpay_invoice_code = graphene.String(default_value=None)
    
    @staticmethod
    def mutate(self, info, jil, huis, torson_ognoo, nom, is_online, utas = "", ner = "", hend = ""):
        
        qpay_env_data = resolve_qpay_env_data()    
        
        qpay_call_back_url = "https://bd5492c3ee85.ngrok.io/payments?payment_id=1234567"
        
        total_price = 0  
        
        zahialga = Zahialga(
            utas=utas,
            ner=ner,
            hend=hend,
            jil=jil,
            huis=huis,
            torson_ognoo=torson_ognoo,
            qpay_invoice_id="qpay_invoice_id",
            qpay_qr_text="qpay_qr_text",
            qpay_qr_image="qpay_qr_image",
            qpay_shortUrl="qpay_shortUrl",
            uniin_dun=total_price
        )
        zahialga.save()
        
        for nom_data in nom:
            try:
                nom_o = Nom.objects.get(id=nom_data.nom)  # Retrieve the Nom instance by ID
                if nom_o.une == 0:
                    nom_une = nom_data.une
                else:
                    nom_une = nom_o.une
                # if is_online == True:
                #     nom_une = nom_une * 2
                #     total_price = total_price + nom_une
                # else: 
                #     total_price += nom_une
                total_price += nom_une
                ZahialgaNom.objects.create(zahialga=zahialga, nom=nom_o, une=nom_une)
            except Nom.DoesNotExist:
                None
                
        zahialga.uniin_dun = total_price
        zahialga.save()
        
        invoice_data = {
            "invoice_code": qpay_env_data.invoice_code,
            "sender_invoice_no": zahialga.uuid4,
            "invoice_receiver_code": zahialga.uuid4,
            "sender_branch_code": "test",
            "amount": zahialga.uniin_dun,
            "invoice_description": zahialga.uuid4,
            "callback_url": qpay_call_back_url
        }
        
        json_invoice_data = json.dumps(invoice_data)
        
        invoice_headers = CaseInsensitiveDict()
        invoice_headers["Content-Type"] = "application/json"
        invoice_headers["charset"] = "utf-8"
        invoice_headers["Authorization"] = 'Bearer {}'.format(qpay_env_data.token)

        qpay_url = qpay_env_data.url+'/invoice'
        
        invoice_resp = requests.post(
            qpay_url,
            headers=invoice_headers,
            data=json_invoice_data
        )
        
        print(invoice_resp.content)
        
        invoice_resp = json.loads(invoice_resp.content)
        
        zahialga.qpay_invoice_id = invoice_resp.get('invoice_id')
        zahialga.qpay_qr_text = invoice_resp.get('qr_text')
        zahialga.qpay_qr_image = invoice_resp.get('qr_image')
        zahialga.qpay_shortUrl = invoice_resp.get('qPay_shortUrl')
        zahialga.save()
        
        qpay_deeplinks = invoice_resp.get('urls')
        for link in qpay_deeplinks:
            deep_link = ZahialgaDeepLink(
                zahialga=zahialga,
                name=link['name'],
                logo=link['logo'],
                link=link['link']
            )
            deep_link.save()
        
        return CreateZahialga(success=True, qpay_invoice_code=zahialga.qpay_invoice_id)

class CheckZahialga(graphene.Mutation):
    class Arguments:
        utas = graphene.Int(required=True)

    success = graphene.Boolean(default_value=False)
    status = graphene.String(default_value="PENDING")
    url = graphene.String(default_value=None)
    mute_all = graphene.Boolean(default_value=False)
    root_name = graphene.String(default_value=None)
    zahialga = graphene.Field(ZahialgaType)

    @staticmethod
    def mutate(self, info, utas):
        
        qpay_env_data = resolve_qpay_env_data()   
        
        zahialga = Zahialga.objects.filter(utas=utas).order_by('-pk').first()
        
        request_data = {
            "object_type": "INVOICE",
            "object_id": zahialga.qpay_invoice_id,
            "offset": {
                'page_number': 1,
                'page_limit': 100
            }
        }
        json_request_data = json.dumps(request_data)

        request_headers = CaseInsensitiveDict()
        request_headers["Content-Type"] = "application/json"
        request_headers["charset"] = "utf-8"
        request_headers["Authorization"] = 'Bearer {}'.format(qpay_env_data.token)

        request_url = qpay_env_data.url+'/payment/check'

        request_resp = requests.post(
            request_url,
            headers=request_headers,
            data=json_request_data
        )
        request_resp = json.loads(request_resp.content)
        
        if request_resp['count'] != 0:
            zahialga.tolov = "SUCCESS"
            zahialga.save()
        
        try:
            
            zahialga_hural = ZahialgaHural.objects.get(zahialga=zahialga)    
            
            return CheckZahialga(
                success=True, 
                url=zahialga_hural.zahialga.uuid4, 
                mute_all=zahialga_hural.mute_all, 
                root_name=zahialga_hural.zahialga.ner,
                zahialga=zahialga,
                status=zahialga.tolov
            )
        except Zahialga.DoesNotExist:
            return CheckZahialga(success=False)
        except ZahialgaHural.DoesNotExist:
            return CheckZahialga(success=False, zahialga=zahialga, status=zahialga.tolov)
        
class CreateZahialgaHural(graphene.Mutation):
    class Arguments:
        zahialga = graphene.ID(required=True)
        mute_all = graphene.Boolean(default_value=False)
        
    zahialga_hural = graphene.Field(ZahialgaHuralType)
        
    def mutate(self, info, zahialga, mute_all):
        zahialga_o = Zahialga.objects.get(pk=zahialga)
        zahialga_hural = ZahialgaHural(
            zahialga=zahialga_o,
            mute_all=mute_all
        )
        zahialga_hural.save()
        return CreateZahialgaHural(zahialga_hural=zahialga_hural)
    
class DeleteZahialgaHural(graphene.Mutation):
    class Arguments:
        zahialga = graphene.ID(required=True)

    success = graphene.Boolean(default_value=False)

    def mutate(self, info, zahialga):
        
        zahialga_o = Zahialga.objects.get(pk=zahialga)
        
        try:
            zahialga_hural = ZahialgaHural.objects.get(zahialga=zahialga_o)
            zahialga_hural.delete()
            return DeleteZahialgaHural(success=True)
        except ZahialgaHural.DoesNotExist:
            return DeleteZahialgaHural(success=False)

class JoinZahialgaHural(graphene.Mutation):
    class Arguments:
        zahialga = graphene.ID(required=True)

    success = graphene.Boolean(default_value=False)
    url = graphene.String(default_value=None)
    mute_all = graphene.Boolean(default_value=False)
    root_name = graphene.String(default_value=None)

    def mutate(self, info, zahialga):
        try:
            zahialga_hural = ZahialgaHural.objects.get(zahialga=zahialga)
            return JoinZahialgaHural(success=True, url=zahialga_hural.zahialga.uuid4, mute_all=zahialga_hural.mute_all, root_name="Ламтан")
        except ZahialgaHural.DoesNotExist:
            return JoinZahialgaHural(success=False)

class SetSuccessZahialga(graphene.Mutation):
    class Arguments:
        zahialga = graphene.ID(required=True)

    success = graphene.Boolean(default_value=False)

    def mutate(self, info, zahialga):
        zahialga_o = Zahialga.objects.get(pk=zahialga)
        zahialga_o.tolov = "SUCCESS"
        zahialga_o.save()
        return SetSuccessZahialga(success=True)

class CheckZahialgaByQpayInvoiceID(graphene.Mutation):
    class Arguments:
        qpay_invoice_id = graphene.String(required=True)

    success = graphene.Boolean(default_value=False)
    status = graphene.String(default_value="PENDING")
    zahialga = graphene.Field(ZahialgaType)

    def mutate(self, info, qpay_invoice_id):
        
        qpay_env_data = resolve_qpay_env_data()
        
        try:    
            zahialga = Zahialga.objects.get(qpay_invoice_id=qpay_invoice_id)
        
            request_data = {
                "object_type": "INVOICE",
                "object_id": zahialga.qpay_invoice_id,
                "offset": {
                    'page_number': 1,
                    'page_limit': 100
                }
            }
            json_request_data = json.dumps(request_data)

            request_headers = CaseInsensitiveDict()
            request_headers["Content-Type"] = "application/json"
            request_headers["charset"] = "utf-8"
            request_headers["Authorization"] = 'Bearer {}'.format(qpay_env_data.token)

            request_url = qpay_env_data.url+'/payment/check'

            request_resp = requests.post(
                request_url,
                headers=request_headers,
                data=json_request_data
            )
            request_resp = json.loads(request_resp.content)
            
            if request_resp['count'] != 0:
                zahialga.tolov = "SUCCESS"
                zahialga.save()
            
            return CheckZahialgaByQpayInvoiceID(
                success=True, 
                zahialga=zahialga,
                status=zahialga.tolov
            )
        except Zahialga.DoesNotExist:
            return CheckZahialgaByQpayInvoiceID(success=False)

class Mutation(graphene.ObjectType):
    create_zahialga = CreateZahialga.Field()
    check_zahialga = CheckZahialga.Field()
    set_success_zahialga = SetSuccessZahialga.Field()
    create_zahialga_hural = CreateZahialgaHural.Field()
    delete_zahialga_hural = DeleteZahialgaHural.Field()
    join_zahialga_hural = JoinZahialgaHural.Field()
    check_zahialga_by_qpay_invoice_id = CheckZahialgaByQpayInvoiceID.Field()