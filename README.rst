PyRVtools
=========

Extract useful information from an RVTools ESX inventory file.

Purpose of that module
----------------------

Did you have ever ask to an VMWare administrator to have an access to
his vCenter to run some scripts by API ? No ? Me yes and a least that
can i say : it's not easy ! ;-)

More seriously, it very often hard to get access to this kind of VM
because it's very sensitive part of the infrastructure and because the
guys generally are not in the same team as you and they not trust you
(neither in your scripts !), so it does not help. But, to be honest,
you'll probably do the same thing if the situation was reversed.

But sometimes, they can send you an RVTools extraction (so an Excel
file) from that vCenter and you want to use it in a Python script.
You'll prefer have to access directly to the vCenter by API call to get
fresh data but it's better than nothing...

That's why i coded this library : to help to use this kind of inputs to
extract some useful information from it.

How to install it
-----------------

You can install pyRvtools by using pip :

``pip install pyrvtools``

How to use it
-------------

You can search for 5 kind of major objects with that module: -
DataCenter - Clusters - Hosts - DataStores - VirtualMachine

Each of them have a specific number of properties. You can iterate on
all object or focus only on one of them giving his name.

Here is some examples (please refer to the list of properties below if
you're looking for a metric):

.. code:: python

    import os
    from pyrvtools import PyRvtools

    PATH = os.sep.join(['your_path', 'your_file.xls'])
    rvtools = PyRvtools(PATH)

    # For all the dataCenters
    for dc in rvtools.get_datacenters():
        print('DC: %s Clusters: %s' % (dc, dc.clusters))

    # Only for a specific DataCenter
    one_dc = rvtools.get_datacenter_by_name('MY_DC')
    print('DC: %s Clusters: %s' % (one_dc, one_dc.clusters))

    # For all the Cluster
    for cluster in rvtools.get_clusters():
        print('Cluster: %s Hosts: %s' % (cluster, cluster.hosts))

    # Only for a specific Cluster
    one_cluster = rvtools.get_clusters_by_name('MY_CLUSTER')
    print('Cluster: %s Hosts: %s' % (one_cluster, one_cluster.hosts))

    # For all the DataStores
    for ds in rvtools.get_datastores():
        print('DS: %s Hosts: %s' % (ds, ds.hosts))

    # Only for a specific DataStore
    one_ds = rvtools.get_datastore_by_name('MY_DS')
    print('DS: %s Hosts: %s' % (one_ds, one_ds.hosts))

    # For all the hosts
    for esx in rvtools.get_hosts():
        print('ESX: %s VM:%s' % (esx, esx.vm))

    # Only for a specific host
    one_esx = rvtools.get_host_by_name('MY_ESX_NAME')
    print('ESX: %s VM:%s' % (one_esx, one_esx.vm))

    # For all the VirtualMachine
    for vm in rvtools.get_vm():
        print('VM: %s DataStore:%s' % (vm, vm.datastore))

    # Only for a specific VM
    one_vm = rvtools.get_vm_by_name('MY_VM')
    print('VM: %s DataStore:%s' % (one_vm, one_vm.datastore))

Properties of objects
---------------------

**Cluster** 
- datacenter 
- hosts

**DataCenter** 
- clusters 
- hosts

**DataStore** 
- capacity_mb 
- free_mb 
- free_percent 
- hosts 
- inuse_mb 
- naa 
- number_of_hosts 
- number_of_vms 
- provisioned_mb
- sioc_enable 
- type 
- version

**Host** 
- boot_time 
- cluster 
- cpu_usage_percent 
- datacenter 
- esx_version 
- hba 
- memory_mb 
- memory_usage_percent 
- model 
- number_of_cores 
- number_of_cpu 
- number_of_vcpu 
- number_of_vm
- vm

**VirtualMachine** 
- cluster 
- cpu 
- datacenter 
- datastore 
- host 
- inuse_mb 
- memory 
- os 
- power_on 
- power_state 
- provisioned_mb 
- unshared_mb 
- vmdk 
- vnetwork 
- vpartition

License
-------

This library is licensed under GPL3.
