from datetime import datetime

import pytest
from checkers import upload_files, ssh_checkout, ssh_getout
import yaml

with open('config.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)

log_start = datetime.now()


def import_log(start_time, name):
    with open(f'{data["log_folder"]}/{log_start.strftime("%Y.%m.%d-%H:%M:%S")}-{name}', 'w') as f:
        exit_code, out = ssh_getout(f'journalctl --since \'{start_time}\'')
        f.write(out)


class Test7z:
    def test_deploy(self, start_time):
        res = []
        upload_files(f'./{data["pkgname"]}.deb', "/home/{}/{}.deb".format(data["user"], data["pkgname"]))
        cmd = f'echo \'{data["passwd"]}\' | sudo -S dpkg -i /home/{data["user"]}/{data["pkgname"]}.deb'
        res.append(ssh_checkout(cmd, "Настраивается пакет"))
        cmd = f'echo \'{data["passwd"]}\' | sudo -S dpkg -s {data["pkgname"]}'
        res.append(ssh_checkout(cmd, "Status: install ok installed"))
        import_log(start_time, "test_deploy.log")
        assert all(res), "deploy_test FAIL"

    def test_add(self, start_time, make_folders, make_files):
        res = []
        cmd = f'cd {data["folder_in"]}; 7z a {data["folder_out"]}arch -t{data["type"]}';
        res.append(ssh_checkout(cmd, "Everything is Ok"))
        cmd = f'ls {data["folder_out"]}'
        res.append(ssh_checkout(cmd, f'arch.{data["type"]}'))
        import_log(start_time, "test_add.log")
        assert all(res), "test_add FAIL"

    def test_delete(self, start_time, make_folders, make_files, make_archive):
        res = []
        for item in make_files:
            cmd = f'cd {data["folder_out"]}; 7z d ./arch.{data["type"]} {item}'
            res.append(ssh_checkout(cmd, "Everything is Ok"))
        cmd = f'cd {data["folder_out"]}; 7z l ./arch.{data["type"]}'
        res.append(ssh_checkout(cmd, "0 files"))
        import_log(start_time, "test_delete.log")
        assert all(res), "test_delete FAIL"

    def test_list(self, start_time, make_folders, make_files, make_archive):
        res = []
        for item in make_files:
            res.append(ssh_checkout(f'7z l {data["folder_out"]}arch.{data["type"]}', item))
        res.append(ssh_checkout(f'7z l {data["folder_out"]}arch.{data["type"]}', f'{len(make_files)} files'))
        import_log(start_time, "test_list.log")
        assert all(res), "test_list FAIL"

    def test_extract(self, start_time, make_folders, make_files, make_archive):
        res = []
        cmd = f'7z x {data["folder_out"]}arch.{data["type"]} -o{data["folder_ext"]}'
        res.append(ssh_checkout(cmd, "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(f'ls {data["folder_ext"]}', item))
        res.append(ssh_checkout(f'ls {data["folder_ext"]} -s', f'итого {data["bs"] * data["count"] * 4}'))
        import_log(start_time, "test_extract.log")
        assert all(res), "test_extract FAIL"

    def test_deinstall(self, start_time):
       res = []
       res.append(ssh_checkout(f'echo \'{data["passwd"]}\' | sudo -S dpkg -r {data["pkgname"]}', "Удаляется"))
       res.append(ssh_checkout(f'echo \'{data["passwd"]}\' | sudo -S dpkg -s {data["pkgname"]}', "Status: deinstall ok"))
       import_log(start_time, "test_deinstall.log")
       assert all(res), "test_deinstall FAIL"


if __name__ == '__main__':
    pytest.main(["-v"])
