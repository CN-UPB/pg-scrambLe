import subprocess
import os

_CWD = os.path.dirname(os.path.realpath(__file__))

def generatePackage(packageType, noRemoveFiles=False, destinationDir="/tmp", descriptorName=None, payload=None, _generate_descriptor_pkg_path="./generate_descriptor_pkg.sh"):
    
    if payload is None:
        return False

    if descriptorName is None:
        return False    

    if not packageType in ["vnfd", "nsd"]:
        return False

    # Create temp folders
    if packageType == "nsd":
        # "./generate_descriptor_pkg.sh -t nsd  -c -d ./ test"
        print(_CWD)
        subprocess.call([_generate_descriptor_pkg_path, "-t", "nsd", "-c", "-d", destinationDir, descriptorName], cwd=_CWD)

        _nsd_folder = os.path.join(destinationDir, "{0}_nsd".format(descriptorName)) 
        _nsd_file = os.path.join(destinationDir, "{0}_nsd".format(descriptorName), "{0}_nsd.yaml".format(descriptorName)) 

        with open(_nsd_file, 'w') as filetowrite:
            filetowrite.write(payload)

        _cmd = [_generate_descriptor_pkg_path, "-t", "nsd"]

        if noRemoveFiles:
            _cmd.append("-N")

        _cmd.append(_nsd_folder)
        _cmd.extend(["-d", destinationDir])

        subprocess.call(_cmd, cwd=_CWD)


    elif packageType == "vnfd":
        # "./generate_descriptor_pkg.sh -t vnfd -c -d ./ --image a test"
        subprocess.call([_generate_descriptor_pkg_path, "-t", "vnfd", "-c", "--image", "dummy", "-d", destinationDir, descriptorName], cwd=_CWD)
        
        _vnfd_folder = os.path.join(destinationDir, "{0}_vnfd".format(descriptorName)) 
        _vnfd_file = os.path.join(destinationDir, "{0}_vnfd".format(descriptorName), "{0}_vnfd.yaml".format(descriptorName)) 

        with open(_vnfd_file, 'w') as filetowrite:
            filetowrite.write(payload)

        _cmd = [_generate_descriptor_pkg_path, "-t", "vnfd"]

        if noRemoveFiles:
            _cmd.append("-N")
        
        _cmd.append(_vnfd_folder)
        _cmd.extend(["-d", destinationDir])

        subprocess.call(_cmd, cwd=_CWD)


#if __name__ == "__main__":
#    generatePackage(packageType="nsd", descriptorName="test", payload="ssup", destinationDir=_CWD)
#    generatePackage(packageType="vnfd", descriptorName="test", payload="ssup", destinationDir=_CWD)