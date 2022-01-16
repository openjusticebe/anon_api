from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, Json, PositiveInt


class ListOutModel(BaseModel):
    """
    Modèle de validation des requêtes de l'outil de matching
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    data: List[str] = Field(..., description="List of available algorithms and techniques")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'list': [
                    'algo_1',
                    'algo_2',
                ],
            }}


class FormatTypes(str, Enum):
    text = 'text'


class EncodingTypes(str, Enum):
    utf8 = 'utf8'


class AlgoTypes(str, Enum):
    test = 'test'  # Simply returns submitted text


class AlgoChoice(BaseModel):
    id: str = Field(..., description='Algo identifier')
    params: Json = Field(None, description='Algo parameters')


class RunInModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    algo_list: List[AlgoChoice] = Field(..., description="List of algorithms and techniques to apply")
    format: FormatTypes = Field(..., description="Format of submitted text")
    encoding: EncodingTypes = Field(None, description="Encoding of submitted text (if applicable)")
    text: str = Field(..., description="Text to depersonalize")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'algo_list': [
                    {'id': 'anon_trazor', 'params': "{}"}
                ],
                'format': 'text',
                'encoding': 'utf8',
                'text': 'Robert serait le fils d\'Erlebert et le neveu de Robert, référendaire de Dagobert Ier.'
            }}


class ParseInModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    algo_list: List[AlgoChoice] = Field(..., description="List of algorithms and techniques to apply")
    format: FormatTypes = Field(..., description="Format of submitted text")
    encoding: EncodingTypes = Field(None, description="Encoding of submitted text (if applicable)")
    text: str = Field(..., description="Text to depersonalize")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'algo_list': [
                    {'id': 'anon_trazor', 'params': "{}"}
                ],
                'format': 'text',
                'encoding': 'utf8',
                'text': 'e Microsoft quand Lorem Ipsum et surtout microsoft dans un pc Intel ..'
            }}


class ParseOutModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    entities: Json = Field(..., description="Raw entities (Raw json datatype)")
    log: Json = Field(..., description="Raw log (Raw json datatype)")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'entities': '{}',
                'log': '{}',
            }}


class RunOutModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    log: Json = Field(..., description="Raw log (Raw json datatype)")
    text: str = Field(..., description="Depersonalized text")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'text': 'Lorem ***** ...',
                'log': '{}'
            }}


class ExtractInModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    text: str = Field(..., description="Subject text")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'text': 'Lorem ***** ...',
            }}


class LanguageTypes(str, Enum):
    FR = 'FR'
    NL = 'NL'
    DE = 'DE'


class AppealType(str, Enum):
    nodata = 'nodata'
    yes = 'yes'
    no = 'no'


class ExtractOutModel(BaseModel):
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    country: str = Field(..., description="Country Code")
    court: str = Field(..., description="Court code")
    year: Optional[int] = Field(..., description="Year")
    lang: LanguageTypes = Field(..., description="Document Language")
    appeal: AppealType = Field(..., description="Appeal")
    labels: list

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                'country': 'BE',
                'court': 'RSCE',
                'year': 2010,
                'lang': 'NL',
                'appeal': 'nodata',
                'labels': []
            }}
