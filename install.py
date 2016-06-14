import pip

def pipimport(packageName, pipInfo):
    try:
        __import__(packageName)
        print("[Setup] " + packageName + " already installed")

    except:
        pip.main(['install', pipInfo])
        print("[Setup] " + packageName + " installed")