import libvirt
import sys

try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError:
    print("Failed to open connection to the hypervisor")
    sys.exit(1)

try:
    ls = conn.listAllDomains()
    for l in ls:
        print(l.name())
    # dom0 = conn.lookupByName("Domain-0")
except libvirt.libvirtError:
    print("Failed to find the main domain")
    sys.exit(1)

# print("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
# print(dom0.info())
