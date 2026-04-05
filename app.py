import json
import uuid
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("NotesTable")

def lambda_handler(event, context):

    method = (
        event.get("httpMethod")
        or event.get("requestContext", {}).get("http", {}).get("method")
    )

    path = event.get("path") or event.get("rawPath") or ""
    path = path.replace("/Prod", "")

    body = event.get("body")
    if body:
        body = json.loads(body)
    else:
        body = {}

    # -------------------
    # CREATE NOTE
    # -------------------
    if method == "POST" and path == "/notes":

        note_id = str(uuid.uuid4())

        item = {
            "id": note_id,
            "title": body.get("title"),
            "content": body.get("content")
        }

        table.put_item(Item=item)

        return response(201, item)

    # -------------------
    # GET ALL NOTES
    # -------------------
    if method == "GET" and path == "/notes":

        data = table.scan()

        return response(200, data.get("Items", []))

    # -------------------
    # DELETE NOTE
    # -------------------
    if method == "DELETE" and path.startswith("/notes/"):

        note_id = path.split("/")[-1]

        table.delete_item(Key={"id": note_id})

        return response(200, {"message": "Deleted", "id": note_id})

    return response(404, {"message": "Route not found"})


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }