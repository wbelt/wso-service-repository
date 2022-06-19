
import os
from azure.cosmos import exceptions, CosmosClient, PartitionKey
from functools import wraps

endpoint = "https://diydev-control-plane-db.documents.azure.com:443/"


def provide_db_client(func):
    @wraps(func)
    def new_function(*args, **kwargs):
        client = CosmosClient(endpoint, os.environ.get('dbSECRETkey'))
        return func(client, *args, **kwargs)
    return new_function


def provide_db_service_repository(func):
    @wraps(func)
    @provide_db_client
    def new_function(client, *args, **kwargs):
        db = client.get_database_client("service-repository")
        return func(db, *args, **kwargs)
    return new_function


def provide_db_services_c(func):
    @wraps(func)
    @provide_db_service_repository
    def new_function(db, *args, **kwargs):
        c = db.get_container_client("services")
        return func(c, *args, **kwargs)
    return new_function


@provide_db_client
def list_databases(client):
    databases = list(client.list_databases())
    if not databases:
        return
    for database in databases:
        print(database['id'])


@provide_db_service_repository
def list_containers(db):
    containers = list(db.list_containers())
    if not containers:
        return
    for container in containers:
        print(container['id'])


@provide_db_services_c
def list_items(c):
    items = list(c.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    ))
    if not items:
        return
    for item in items:
        print(item['id'])


if __name__ == '__main__':
    print(list_containers())
