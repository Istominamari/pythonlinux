import pytest
from checkers import ssh_getout
import yaml
import random
import string
from datetime import datetime


with open('config.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)


@pytest.fixture()
def make_folders():
    ssh_getout("mkdir {} {} {}".format(data["folder_in"], data["folder_out"], data["folder_ext"]))
    yield
    ssh_getout("rm -rf {} {} {}".format(data["folder_in"], data["folder_out"], data["folder_ext"]))


@pytest.fixture()
def make_files():
    list_off_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        ssh_getout(f'cd {data["folder_in"]}; dd if=/dev/urandom of={filename} bs={data["bs"]}K count=1 iflag=fullblock')
        list_off_files.append(filename)
    return list_off_files


@pytest.fixture()
def make_archive():
    ssh_getout(f'cd {data["folder_in"]}; 7z a {data["folder_out"]}arch -t{data["type"]}')

@pytest.fixture()
def start_time():
   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
