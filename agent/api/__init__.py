# api
try:
    from tools.common.omni_v12 import install_omni_v12_patch
    install_omni_v12_patch()
except ImportError:
    pass
