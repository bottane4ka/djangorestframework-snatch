DEFAULT_METHODS_CONFIG = {
    "methods": {
        "list": {
            "parameterType": "FILTER",
            "httpMethod": "GET",
            "responseContentType": "application/json",
            "systemName": "getList",
            "path": "/list",
        },
        "retrieve": {
            "parameterType": "FILTER",
            "httpMethod": "GET",
            "responseContentType": "application/json",
            "systemName": "getEntity",
            "path": "/",
        },
        "create": {
            "parameterType": "DTO",
            "httpMethod": "POST",
            "responseContentType": "application/json",
            "systemName": "save",
            "path": "/",
        },
        "update": {
            "parameterType": "DTO",
            "httpMethod": "PUT",
            "responseContentType": "application/json",
            "systemName": "update",
            "path": "/",
        },
        "destroy": {
            "parameterType": "FILTER",
            "httpMethod": "DELETE",
            "responseContentType": "application/json",
            "systemName": "delete",
            "path": "/",
        },
        "size": {
            "parameterType": "FILTER",
            "httpMethod": "GET",
            "responseContentType": "text/plain",
            "systemName": "getListSize",
            "path": "/size",
        },
    }
}
