import graphene
from graphene_django.types import DjangoObjectType
import requests
import json
from requests.auth import HTTPBasicAuth
from .models import TsagaanSar
from utils.utils import calculate_mongolian_zodiac

class TsagaanSarType(DjangoObjectType):
    class Meta:
        model = TsagaanSar
        fields = ["id", "ner", "ognoo"]

class JilType(graphene.ObjectType):
    year = graphene.Int()
    animal = graphene.String()
    element = graphene.String()
        
class Query(graphene.ObjectType):
    tsagaan_sar = graphene.List(TsagaanSarType)
    tsagaan_sar_by_id = graphene.Field(TsagaanSarType, id=graphene.Int(required=True))
    jil_ognoogoor = graphene.Field(JilType, ognoo=graphene.Int(required=True))
    test = graphene.String()

    def resolve_tsagaan_sar(self, info):
        return TsagaanSar.objects.all()
    
    def resolve_tsagaan_sar_by_id(self, info, id):
        return TsagaanSar.objects.get(pk=id)
    
    def resolve_jil_ognoogoor(self, info, ognoo):

        jil = calculate_mongolian_zodiac(ognoo)
        
        return JilType(
            year=jil['year'],
            animal=jil['animal'],
            element=jil['element']
        )

    def resolve_test(self, info):
        
        API_KEY = "your_whereby_api_key"  # Replace with your actual API key
        API_URL = "https://api.whereby.dev/v1/rooms"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "isLocked": True,  # Lock the room by default
            "roomName": "Nee's room",
            "roomMode": "normal",  # Options: normal or group
            "endDate": "2025-01-10T23:59:59Z"  # Optional: Auto-delete the room after this date
        }

        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            room_data = response.json()
            print("Room created successfully!")
            print("Room URL:", room_data["roomUrl"])
        else:
            print(f"Error: {response.status_code} - {response.text}")
