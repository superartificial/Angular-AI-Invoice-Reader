from huggingface_hub import HfApi

api = HfApi()

username = "ClemAotearoa"
space_name = "InvoiceReaderDemo"

space_sdk_version = "0.13.2"

api.upload_folder(
    folder_path=".",
    path_in_repo="",
    repo_id=f"{username}/{space_name}",
    repo_type="space",

)