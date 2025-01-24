import graphene
from graphene_django.types import DjangoObjectType
import requests
import json
import environ
from datetime import datetime
from .models import Zahialga, ZahialgaNom, QpayToken

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
        fields = ["id", "utas", "ner", "hend", "jil", "huis", "tolov", "torson_ognoo", "uussen_ognoo", "shinechlegdsen_ognoo"]
        
class ZahialgaNomType(DjangoObjectType):
    class Meta:
        model = ZahialgaNom
        fields = ["id", "zahialga", "nom", "une"]

class ZahialgaNomInputType(graphene.ObjectType):
    nom = graphene.ID(required=True)
    une = graphene.Int()
    

class Query(graphene.ObjectType):
    check_invoice = graphene.Field(ZahialgaType, utas=graphene.Int(required=True))
    
class CreateZahialga(graphene.Mutation):
    class Arguments:
        utas = graphene.Int(required=True)
        ner = graphene.String(required=True)
        hend = graphene.String(required=True)
        jil = graphene.String(required=True)
        huis = graphene.String(required=True)
        torson_ognoo = graphene.Int(required=True)
        nom = graphene.List(ZahialgaNomInputType, required=True)
        
    success = graphene.Boolean(default_value=False)
    qpay_invoice_code = graphene.String(default_value=None)
    
    @staticmethod
    def mutate(self, info, utas, ner, hend, jil, huis, torson_ognoo, nom):
        
        qpay_env_data = resolve_qpay_env_data()    
        
        qpay_call_back_url = "http://tenger.pro:8000/graphql#query=%0Aquery%20check_invoice_status%20%7B%0A%20%20checkInvoiceStatus%20(invoice%3A%20{})%0A%7D"
        
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
            uniin_dun=0
        )
        zahialga.save()
        
        invoice_data = {
            "invoice_code": qpay_env_data.invoice_code,
            "sender_invoice_no": zahialga.uuid4,
            "invoice_receiver_code": zahialga.uuid4,
            "sender_branch_code": "test",
            "amount": invoice.amount,
            "invoice_description": "(бүртгэлийн хураамж)",
            "callback_url": qpay_call_back_url.format(invoice.pk)
        }
        
        return CreateZahialga(zahialga=zahialga)
    
class Mutation(graphene.ObjectType):
    create_zahialga = CreateZahialga.Field()