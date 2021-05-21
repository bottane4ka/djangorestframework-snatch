from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import utilities.url_name as url_name
from snatch.old.options.info_utils import to_info
from .services import capitalize_name
from .services import search_fk_in_data


class ModelInfo(APIView):
    """
    GET: Получение информации об информационном ресурсе
    """

    def get(self, request, schema, table):
        view_name = request._request.path
        model_name = capitalize_name(table)
        data = to_info(view_name, schema, model_name)
        return Response(data, status=status.HTTP_200_OK)


class ModelInfoReverse(APIView):
    """
    GET: Получение записи ресурса, на который ссылается атрибут первичного ресурса
    """

    def get(self, request, schema, table, attribute):
        params = request.GET
        if params:
            view_name = request._request.path
            model_name = capitalize_name(table)
            data = to_info(view_name, schema, model_name, search_attribute=True)
            attribute_list = data.get("attributes", None)
            if attribute_list:
                fk_table, class_name = search_fk_in_data(attribute_list, attribute)
                if fk_table:
                    fk_table = "{}_detail".format(fk_table)
                    class_name = "Url{}".format(capitalize_name(class_name))
                    view_name = getattr(getattr(url_name, class_name), fk_table)
                    params = ["{}={}".format(key, params[key]) for key in params.keys()]
                    url = "{}?{}".format(reverse(view_name), "&".join(params))
                    return HttpResponseRedirect(url)
        return Response(status=status.HTTP_404_NOT_FOUND)


class ModelInfoReverseList(APIView):
    """
    GET: Получение списка записей ресурса, на который ссылается атрибут первичного ресурса
    """

    def get(self, request, schema, table, attribute):
        params = request.GET
        view_name = request._request.path
        model_name = capitalize_name(table)
        data = to_info(view_name, schema, model_name, search_attribute=True)
        attribute_list = data.get("attributes", None)
        if attribute_list:
            fk_table, class_name = search_fk_in_data(attribute_list, attribute)
            if fk_table:
                fk_table = "{}_list".format(fk_table)
                class_name = "Url{}".format(capitalize_name(class_name))
                view_name = getattr(getattr(url_name, class_name), fk_table)
                if params:
                    params = ["{}={}".format(key, params[key]) for key in params.keys()]
                    url = "{}?{}".format(reverse(view_name), "&".join(params))
                else:
                    url = reverse(view_name)
                return HttpResponseRedirect(url)
        return Response(status=status.HTTP_404_NOT_FOUND)
