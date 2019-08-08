import wrappers

# Delete existing NSD, VNF
def _del(file_path, _type):
    pass

# Upload NSD, VNF
def _upload(file_path, _type):
    pass



if __name__ == "__main__":
    # Take arguments
    # Capture arg vnf

    # _vnf = get argument here
    # _nsd = get argument here
    # _type = get argument here

    if _type == "nsd":
        _del(file_path, "nsd")
        _upload(file_path, "nsd")
    elif _type == "vnfd":
        _del(file_path, "vnfd")
        _upload(file_path, "vnfd")

    del_vnf()
    upload_vnf
    pass