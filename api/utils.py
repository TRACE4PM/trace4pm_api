import hashlib
import os

# Function to get the list of files in a directory
# Return a list of files
def get_file_in_dir(dir: str) -> list:
    list_file = []
    for file in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, file)):
            list_file.append(file)
    return list_file


# A utility function that create hash SHA256 of a file
async def compute_sha256(file_name):
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()