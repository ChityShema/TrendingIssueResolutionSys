from google.cloud import datastore_v1
from google.cloud import datastore

def test_datastore_connection():
    try:
        # Try both client initialization methods
        try:
            client = datastore.Client()
            print("Successfully connected using datastore.Client()")
        except Exception as e1:
            print(f"First method failed: {e1}")
            client = datastore_v1.DatastoreClient()
            print("Successfully connected using datastore_v1.DatastoreClient()")

        # Try to create a test entity
        kind = 'TestKind'
        name = 'test1'
        key = client.key(kind, name)
        entity = datastore.Entity(key=key)
        entity.update({
            'description': 'Test entity'
        })
        client.put(entity)
        print("Successfully created test entity")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("Type of error:", type(e))

if __name__ == "__main__":
    test_datastore_connection()
