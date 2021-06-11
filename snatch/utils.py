from rest_framework.reverse import reverse


def get_link_many(field, instance):
    table_schema, table_name = field.model._meta.db_table.split('"."')
    url = reverse(f"{table_schema}_{table_name}_list")
    return f"{url}?query={field.name}.eq.{instance.pk}"


def get_link_one(self, instance):
    pk_name = instance._meta.pk.name
    table_schema, table_name = self.Meta.model._meta.db_table.split('"."')
    url = reverse(f"{table_schema}_{table_name}_detail")
    return f"{url}?query={pk_name}.eq.{instance.pk}"
