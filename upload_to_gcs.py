import glob
from google.cloud import storage

BUCKET = "cx-testing"


def upload_wms_images(directory):
    # list all files in local `output` directory
    files = glob.glob("{}/*".format(directory))
    # iterate through local `output` files
    for f in files:
        source_file_name = f
        # this is NOT robust
        blob_name = f.split("/")[1]
        destination_blob_name = "{}/{}".format(directory, blob_name)
        # initialize the GCS client
        storage_client = storage.Client()
        # get the destination GCS bucket
        bucket = storage_client.bucket(BUCKET)
        # specify the GCS blob name
        blob = bucket.blob(destination_blob_name)
        # upload to GCS
        blob.upload_from_filename(source_file_name)
        # notify script user of successful upload
        print(
            "File `{}` uploaded to GCS: `{}`.".format(
                source_file_name, destination_blob_name
            )
        )


upload_wms_images("output")
