import typing as t
from enum import Enum

from pydantic import BaseModel


class ParameterTypeEnum(str, Enum):
    FILTER = "FILTER"
    DTO = "DTO"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class _MethodInfo(BaseModel):
    parameterType: ParameterTypeEnum
    httpMethod: HttpMethod
    responseContentType: str
    systemName: str
    path: str


class MethodsConfig(BaseModel):
    methods: t.Dict[str, _MethodInfo] = {}
