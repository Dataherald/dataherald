from utils.s3 import S3

if __name__ == "__main__":
    s3 = S3()
    with open("database/scripts/my_pem_key", encoding="utf-8") as file:
        path = s3.create_and_upload(file.read(), "staging_pem_key")
        print(path)
