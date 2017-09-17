#!/usr/bin/env python3
# coding : utf-8

import os
from pyrvtools.esx_types import Cluster, DataCenter, DataStore, Host, VirtualMachine
from pyrvtools.errors import PyRvtoolsError, ObjectNotFoundError, FileNonConformantError
from xlrd import open_workbook
from xlrd.sheet import Sheet


class PyRvtools(object):
    """ Extract useful information from an RVTools file """

    def __init__(self, filename: str):
        """
        Constructor
        :param filename: RVTools inventory file
        """

        if not os.path.isfile(filename):
            raise PyRvtoolsError('Incorrect filename: %s' % filename)

        if not os.access(filename, os.R_OK):
            raise PyRvtoolsError('Can\'t read file: %s' % filename)

        self._book = open_workbook(filename, on_demand=True)
        # self._health_check() # Slow with this method, full sheet load ?

    @staticmethod
    def get_columns_names(sheet: Sheet):
        """
        Return a dictionary with COLUMN_NAME:ID_COLUMN
        :param sheet: a Sheet object
        """

        mapping = {}
        for col_index in range(sheet.ncols):
            mapping[sheet.cell_value(0, col_index)] = col_index
        return mapping

    def _get_names(self, sheet_name: str, value_name: str):
        """
        Generator - Return a range of values from a column
        :param sheet_name: Name of the sheet to parse
        :param value_name: Value you are looking for
        """
        sheet = self._book.sheet_by_name(sheet_name)
        mapping = self.get_columns_names(sheet)
        for idx in range(sheet.nrows):
            if idx == 0:
                continue
            yield sheet.cell_value(idx, mapping[value_name])

    def _health_check(self):
        """ Do some health check before go ahead """

        all_tabs = []
        needed_tabs = ['tabvInfo', 'tabvDisk', 'tabvPartition',
                       'tabvHost', 'tabvHBA', 'tabvDatastore']

        for sheet in self._book.sheets():
            all_tabs.append(sheet.name)

        if not set(needed_tabs).issubset(set(all_tabs)):
            msg = 'The file is not a RVTools file'
            raise FileNonConformantError(msg)

    def get_clusters(self):
        """
        Generator - return a list of Cluster objects
        :return Cluster
        """

        for cluster in set(self._get_names('tabvHost', 'Cluster')):
            if cluster:
                yield Cluster(self._book, cluster)

    def get_clusters_by_name(self, name):
        """
        Search a Cluster object and return it
        :param name: Name of that Cluster
        """

        found = None
        for cluster in self._get_names('tabvHost', 'Cluster'):
            if cluster == name:
                found = Cluster(self._book, cluster)
                break

        if not found:
            raise ObjectNotFoundError('Cluster %s not found' % name)

        return found

    def get_datacenters(self):
        """
        Generator - return a list of DataCenter objects
        :return DataCenter
        """

        for datacenter in set(self._get_names('tabvHost', 'Datacenter')):
            if datacenter:
                yield DataCenter(self._book, datacenter)

    def get_datacenter_by_name(self, name):
        """
        Search a DataCenter object and return it
        :param name: Name of that DataCenter
        """

        found = None
        for datacenter in self._get_names('tabvHost', 'Datacenter'):
            if datacenter == name:
                found = DataCenter(self._book, datacenter)
                break

        if not found:
            raise ObjectNotFoundError('Datacenter %s not found' % name)

        return found

    def get_datastores(self):
        """
        Generator - return a list of DataStore objects
        :return DataStore
        """

        for datastore in self._get_names('tabvDatastore', 'Name'):
            yield DataStore(self._book, datastore)

    def get_datastore_by_name(self, name):
        """
        Search a DataStore object and return it
        :param name: Name of that DataStore
        """

        found = None
        for datastore in self._get_names('tabvDatastore', 'Name'):
            if datastore == name:
                found = DataStore(self._book, datastore)
                break

        if not found:
            raise ObjectNotFoundError('Datastore %s not found' % name)
        return found

    def get_hosts(self):
        """
        Generator - return a list of Host objects
        :return Host
        """

        for host in self._get_names('tabvHost', 'Host'):
            yield Host(self._book, host)

    def get_host_by_name(self, name):
        """
        Search a Host object and return it
        :param name: Name of that Host
        """

        found = None
        for host in self._get_names('tabvHost', 'Host'):
            if host == name:
                found = Host(self._book, host)
                break

        if not found:
            raise ObjectNotFoundError('Host %s not found' % name)
        return found

    def get_vm(self):
        """
        Generator - return a list of VirtualMachine objects
        :return VirtualMachine
        """

        for vm in self._get_names('tabvInfo', 'VM'):
            yield VirtualMachine(self._book, vm)

    def get_vm_by_name(self, name):
        """
        Search a VirtualMachine object and return it
        :param name: Name of that VirtualMachine
        """

        found = None
        for vm in self._get_names('tabvInfo', 'VM'):
            if vm == name:
                found = VirtualMachine(self._book, vm)
                break

        if not found:
            raise ObjectNotFoundError('VirtualMachine %s not found' % name)

        return found
