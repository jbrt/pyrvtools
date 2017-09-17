#!/usr/bin/env python3
# coding : utf-8

import pyrvtools.pyrvtools
from datetime import datetime
from xlrd import book
from xlrd.sheet import Sheet


class ESXBase(object):
    """ Super class of every ESX object """

    def __init__(self, workbook: book, name: str):
        """
        Constructor
        :param workbook: a workbook XLRD
        :param name: Name of that ESX object
        """
        self._book = workbook
        self._name = name
        self._data = None
        self._sheet = None
        self._column = None

    def __eq__(self, other):
        compare = False
        if isinstance(other, str):
            compare = self.name == other
        if isinstance(other, self.__class__):
            compare = self.name == other.name
        return compare

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._name)

    def __str__(self):
        return self._name

    # only_one : just to speed up the search in case of unique value

    def _search(self, sheet: Sheet, column: str, target: str, only_one=False):
        """
        Generic search method
        :param sheet: A Sheet XLRD Object where perform the search
        :param column: Name of the column where perform the search
        :param target: Value to find
        :param only_one: (boolean) search one (true) or multiple values (false)
        :return dict: a dictionary with a complete row of data
        """
        target_rows = []
        column_names = pyrvtools.pyrvtools.PyRvtools.get_columns_names(sheet)
        for row_number in range(sheet.nrows):
            if sheet.cell_value(row_number, column_names[column]) == target:
                target_rows.append(row_number)

                if target_rows and only_one:
                    break

        all_answer = []
        for target_row in target_rows:
            one_answer = {}
            for col_name, col_number in column_names.items():
                one_answer[col_name] = sheet.cell_value(target_row, col_number)
            all_answer.append(one_answer)
        return all_answer

    def _search_one_value(self, item):
        """
        Search only one occurrence of a value in the embedded sheet
        :param item: item to find
        """
        if not self._data:
            self._data = self._search(self._sheet, self._column,
                                      self._name, only_one=True)
        return self._data[0][item]

    @property
    def name(self):
        return self._name


class Cluster(ESXBase):
    """ Object that's represent a vSphere Cluster """

    def __init__(self, workbook: book, name: str):
        """
        Contructor
        :param workbook: a XLRD workbook
        :param name: name of the Cluster
        """
        super().__init__(workbook, name)
        self._sheet = self._book.sheet_by_name('tabvHost')
        self._column = 'Cluster'
        self._hosts = []

    @property
    def datacenter(self):
        return self._search_one_value('Datacenter')

    @property
    def hosts(self):
        if not self._hosts:
            data = self._search(sheet=self._sheet, column='Cluster',
                                target=self._name)
            for host in data:
                self._hosts.append(Host(self._book, host['Host']))

        return self._hosts


class DataCenter(ESXBase):
    """ Object that's represent a vSphere DataCenter """

    def __init__(self, workbook: book, name: str):
        """
        Contructor
        :param workbook: a XLRD workbook
        :param name: name of that DataCenter
        """
        super().__init__(workbook, name)
        self._sheet = self._book.sheet_by_name('tabvHost')
        self._column = 'Datacenter'
        self._clusters = []
        self._hosts = []

    @property
    def clusters(self):
        if not self._clusters:
            data = self._search(sheet=self._sheet, column='Datacenter',
                                target=self._name)
            for cluster in data:
                if any(i.name == cluster['Cluster'] for i in self._clusters):
                    continue

                if not cluster['Cluster']:
                    continue

                self._clusters.append(Cluster(self._book, cluster['Cluster']))

        return self._clusters

    @property
    def hosts(self):
        if not self._hosts:
            data = self._search(sheet=self._sheet, column='Datacenter',
                                target=self._name)
            for host in data:
                self._hosts.append(Host(self._book, host['Host']))

        return self._hosts


class DataStore(ESXBase):
    """ Object that's represent a vSphere DataStore """

    def __init__(self, workbook: book, name: str):
        """
        Constructor
        :param workbook: a XLRD workbook
        :param name: name of that DataStore
        """
        super().__init__(workbook, name)
        self._sheet = self._book.sheet_by_name('tabvDatastore')
        self._column = 'Name'
        self._hosts = []

    @property
    def capacity_mb(self):
        return int(self._search_one_value('Capacity MB'))

    @property
    def free_mb(self):
        return int(self._search_one_value('Free MB'))

    @property
    def free_percent(self):
        return int(self._search_one_value('Free %'))

    @property
    def hosts(self):
        if not self._hosts:
            hosts = self._search_one_value('Hosts')
            for host in hosts.split(', '):
                self._hosts.append(Host(self._book, host))

        return self._hosts

    @property
    def inuse_mb(self):
        return int(self._search_one_value('In Use MB'))

    @property
    def naa(self):
        naa = self._search_one_value('Address')
        naa = naa.split('.')[1] if naa and naa.startswith('naa.') else ''
        return naa

    @property
    def number_of_hosts(self):
        return int(self._search_one_value('# Hosts'))

    @property
    def number_of_vms(self):
        return int(self._search_one_value('# VMs'))

    @property
    def provisioned_mb(self):
        return int(self._search_one_value('Provisioned MB'))

    @property
    def sioc_enable(self):
        return bool(self._search_one_value('SIOC enabled'))

    @property
    def type(self):
        return self._search_one_value('Type')

    @property
    def version(self):
        return str(self._search_one_value('Major Version'))


class HBA(object):
    """ Tiny object that's represent an HBA adapter """

    def __init__(self, **kwargs):
        self._hba = kwargs

    def __repr__(self):
        return 'HBA(%s)' % self._hba['Device']

    def __str__(self):
        return self._hba['Device']

    @property
    def device(self):
        return self._hba['Device']

    @property
    def status(self):
        return self._hba['Status']

    @property
    def type(self):
        return self._hba['Type']

    @property
    def driver(self):
        return self._hba['Driver']

    @property
    def model(self):
        return self._hba['Model']

    @property
    def wwn(self):
        wwn = None
        if self.type == 'Fibre Channel':
            wwn = self._hba['WWN'].split(' ')
        return wwn


class Host(ESXBase):
    """ Object that's represent a vSphere DataStore """

    def __init__(self, workbook: book, name: str):
        """
        Constructor
        :param workbook: a XLRD workbook
        :param name: name of that Host
        """
        super().__init__(workbook, name)
        self._sheet = self._book.sheet_by_name('tabvHost')
        self._column = 'Host'
        self._hba = []
        self._vms = []

    @property
    def boot_time(self):
        date = self._search_one_value('Boot time')
        return datetime.strptime(date, '%d/%m/%Y %H:%M:%S')

    @property
    def cluster(self):
        return self._search_one_value('Cluster')

    @property
    def cpu_usage_percent(self):
        return int(self._search_one_value('CPU usage %'))

    @property
    def datacenter(self):
        return self._search_one_value('Datacenter')

    @property
    def esx_version(self):
        return self._search_one_value('ESX Version')

    @property
    def hba(self):
        if not self._hba:
            data = self._search(sheet=self._book.sheet_by_name('tabvHBA'),
                                column='Host',
                                target=self._name)
            for one_hba in data:
                self._hba.append(HBA(**one_hba))

        return self._hba

    @property
    def memory_mb(self):
        return int(self._search_one_value('# Memory'))

    @property
    def memory_usage_percent(self):
        return int(self._search_one_value('Memory usage %'))

    @property
    def model(self):
        return self._search_one_value('Model')

    @property
    def number_of_cores(self):
        return int(self._search_one_value('# Cores'))

    @property
    def number_of_cpu(self):
        return int(self._search_one_value('# CPU'))

    @property
    def number_of_vcpu(self):
        return int(self._search_one_value('# vCPUs'))

    @property
    def number_of_vm(self):
        return int(self._search_one_value('# VMs'))

    @property
    def vm(self):
        if not self._vms:
            data = self._search(sheet=self._book.sheet_by_name('tabvInfo'),
                                column='Host',
                                target=self._name)
            for vm in data:
                self._vms.append(VirtualMachine(self._book, vm['VM']))

        return self._vms


class VirtualMachine(ESXBase):
    """ Object that's represent a vSphere Virtual Machine """

    def __init__(self, workbook: book, name: str):
        """
        Constructor
        :param workbook: a XLRD workbook
        :param name: name of that VirtualMachine
        """
        super().__init__(workbook, name)
        self._sheet = self._book.sheet_by_name('tabvInfo')
        self._column = 'VM'
        self._vdisks = []
        self._vpartitions = []
        self._vnetworks = []

    @property
    def cluster(self):
        return Cluster(self._book, self._search_one_value('Cluster'))

    @property
    def cpu(self):
        return int(self._search_one_value('CPUs'))

    @property
    def datacenter(self):
        return DataCenter(self._book, self._search_one_value('Datacenter'))

    @property
    def datastore(self):
        path = self._search_one_value('Path')
        return DataStore(self._book, path[path.find('[')+1:path.find(']')])

    @property
    def host(self):
        return Host(self._book, self._search_one_value('Host'))

    @property
    def inuse_mb(self):
        return int(self._search_one_value('In Use MB'))

    @property
    def memory(self):
        return int(self._search_one_value('Memory'))

    @property
    def os(self):
        return self._search_one_value('OS')

    @property
    def power_on(self):
        timestamp = None
        date = self._search_one_value('PowerOn')
        if date:
            timestamp = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
        return timestamp

    @property
    def power_state(self):
        return self._search_one_value('Powerstate')

    @property
    def provisioned_mb(self):
        return int(self._search_one_value('Provisioned MB'))

    @property
    def unshared_mb(self):
        return int(self._search_one_value('Unshared MB'))

    @property
    def vmdk(self):
        if not self._vdisks:
            data = self._search(sheet=self._book.sheet_by_name('tabvDisk'),
                                column='VM',
                                target=self._name)

            for disk in data:
                self._vdisks.append(VDisk(book=self._book, **disk))

        return self._vdisks

    @property
    def vnetwork(self):
        if not self._vnetworks:
            data = self._search(sheet=self._book.sheet_by_name('tabvNetwork'),
                                column='VM',
                                target=self._name)

            for network in data:
                self._vnetworks.append(VNetwork(**network))

        return self._vnetworks

    @property
    def vpartition(self):
        if not self._vpartitions:
            data = self._search(sheet=self._book.sheet_by_name('tabvPartition'),
                                column='VM',
                                target=self._name)

            for disk in data:
                self._vpartitions.append(VPartition(**disk))

        return self._vpartitions


class VDisk(object):
    """ Tiny object that's represent a VMDK disk """

    def __init__(self, **kwargs):
        self._data = kwargs
        self._book = kwargs['book']

    def __repr__(self):
        return 'VMDK(%s)' % self._data['Disk']

    def __str__(self):
        return self._data['Disk']

    @property
    def capacity_mb(self):
        return int(self._data['Capacity MB'])

    @property
    def datastore(self):
        path = self._data['Path']
        return DataStore(self._book, path[path.find('[')+1:path.find(']')])

    @property
    def eagerly_scrub(self):
        return bool(self._data['Eagerly Scrub'])

    @property
    def thin(self):
        return bool(self._data['Thin'])


class VNetwork(object):
    """ Tiny object that's represent a virtual network adapter """

    def __init__(self, **kwargs):
        self._data = kwargs

    def __repr__(self):
        return 'VNetwork(%s,%s,%s)' % (self._data['VM'],
                                       self._data['Adapter'],
                                       self._data['Network'])

    def __str__(self):
        return '%s,%s,%s' % (self._data['VM'],
                             self._data['Adapter'],
                             self._data['Network'])

    @property
    def adapter(self):
        return self._data['Adapter']

    @property
    def connected(self):
        return bool(self._data['Connected'])

    @property
    def ip_address(self):
        ip = []
        if self._data['IP Address']:
            if not self._data['IP Address'] == 'unknown':
                ip = self._data['IP Address'].split(', ')

        return ip

    @property
    def mac_address(self):
        return self._data['Mac Address']

    @property
    def network(self):
        return self._data['Network'] if self._data['Network'] else None

    @property
    def powerstate(self):
        return self._data['Powerstate']

    @property
    def switch(self):
        return self._data['Switch']


class VPartition(object):
    """ Tiny object that's represent the data (partitions) inside a VM """

    def __init__(self, **kwargs):
        self._data = kwargs

    def __repr__(self):
        return 'VPartition(%s)' % self._data['Disk']

    def __str__(self):
        return self._data['Disk']

    @property
    def capacity_mb(self):
        return int(self._data['Capacity MB'])

    @property
    def disk(self):
        return self._data['Disk']

    @property
    def free_mb(self):
        return int(self._data['Free MB'])

    @property
    def free_percent(self):
        return int(self._data['Free % '])
