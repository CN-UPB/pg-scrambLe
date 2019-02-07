import hashlib
import json
import tarfile

class Helpers():

    @staticmethod
    def md5(filename):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: filename.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    # def _descriptor_update(tarf, data_path):
    #     # extract the package on a tmp directory
    #     tarf.extractall('/tmp')
    #     with open(data_path, 'r') as dfile:
    #         _data=dfile.read()
    #     print _data
    #     for name in tarf.getnames():
    #         print(name)
    #         if name.endswith(".yaml") or name.endswith(".yml"):
    #             with open('/tmp/' + name, 'w') as outfile:
    #                 json.safe_dumps(_data, outfile, default_flow_style=False)
    #         break

    #     tarf_temp = tarfile.open("/tmp/{0}.tar.gz".format("test"), "w:gz")

    #     for tarinfo in tarf:
    #         tarf_temp.add('/tmp/' + tarinfo.name, tarinfo.name, recursive=False)
    #     tarf_temp.close()
    #     return tarf
    
