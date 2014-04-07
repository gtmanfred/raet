# -*- coding: utf-8 -*-
'''
keeping.py raet protocol keep classes
'''
# pylint: skip-file
# pylint: disable=W0611

# Import python libs
import os
from collections import deque

try:
    import simplejson as json
except ImportError:
    import json

# Import ioflo libs
from ioflo.base.odicting import odict
from ioflo.base import aiding

from . import raeting
from . import nacling

from ioflo.base.consoling import getConsole
console = getConsole()


class Keep(object):
    '''
    RAET protocol base class for data persistence of objects that follow the Lot
    protocol
    '''
    Fields = ['uid', 'name', 'ha']

    def __init__(self, dirpath='', stackname='stack', prefix='data', ext='json', **kwa):
        '''
        Setup Keep instance
        Create directories for saving associated data files
            keep/
                stackname/
                    local/
                        prefix.uid.ext
                    remote/
                        prefix.uid.ext
                        prefix.uid.ext
        '''
        if not dirpath:
            dirpath = os.path.join("/tmp/raet/keep", stackname)
        self.dirpath = os.path.abspath(dirpath)
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)

        self.localdirpath = os.path.join(self.dirpath, 'local')
        if not os.path.exists(self.localdirpath):
            os.makedirs(self.localdirpath)

        self.remotedirpath = os.path.join(self.dirpath, 'remote')
        if not os.path.exists(self.remotedirpath):
            os.makedirs(self.remotedirpath)

        self.prefix = prefix
        self.ext = ext
        self.localfilepath = os.path.join(self.localdirpath,
                "{0}.{1}".format(self.prefix, self.ext))

    @staticmethod
    def dump(data, filepath):
        '''
        Write data as json to filepath
        '''
        if ' ' in filepath:
            raise raeting.KeepError("Invalid filepath '{0}' contains space")

        with aiding.ocfn(filepath, "w+") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    @staticmethod
    def load(filepath):
        '''
        Return data read from filepath as converted json
        Otherwise return None
        '''
        with aiding.ocfn(filepath) as f:
            try:
                it = json.load(f, object_pairs_hook=odict)
            except EOFError:
                return None
            except ValueError:
                return None
            return it
        return None

    def verify(self, data):
        '''
        Returns True if the fields in .Fields match the fields in data
        '''
        return (set(self.Fields) == set(data.keys()))

    def defaults(self):
        '''
        Return odict with items preloaded with defaults
        '''
        data = odict()
        for field in fields:
            data[field] = None
        return data

    def dumpLocalData(self, data):
        '''
        Dump the local data to file
        '''
        self.dump(data, self.localfilepath)

    def loadLocalData(self):
        '''
        Load and Return the data from the local file
        '''
        if not os.path.exists(self.localfilepath):
            return None
        return (self.load(self.localfilepath))

    def clearLocalData(self):
        '''
        Clear the local file
        '''
        if os.path.exists(self.localfilepath):
            os.remove(self.localfilepath)

    def dumpRemoteData(self, data, uid):
        '''
        Dump the remote data to file named with uid
        '''
        filepath = os.path.join(self.remotedirpath,
                "{0}.{1}.{2}".format(self.prefix, uid, self.ext))

        self.dump(data, filepath)

    def dumpAllRemoteData(self, datadict):
        '''
        Dump the data in the datadict keyed by uid to remote data files
        '''
        for uid, data in datadict.items():
            self.dumpRemoteData(data, uid)

    def loadRemoteData(self, uid):
        '''
        Load and Return the data from the remote file named with uid
        '''
        filepath = os.path.join(self.remotedirpath,
                        "{0}.{1}.{2}".format(self.prefix, uid, self.ext))
        if not os.path.exists(filepath):
            return None
        return (self.load(filepath))

    def clearRemoteData(self, uid):
        '''
        Clear data from the remote data file named with uid
        '''
        filepath = os.path.join(self.remotedirpath,
                        "{0}.{1}.{2}".format(self.prefix, uid, self.ext))
        if os.path.exists(filepath):
            os.remove(filepath)

    def loadAllRemoteData(self):
        '''
        Load and Return the datadict from the all the remote data files
        indexed by uid in filenames
        '''
        datadict = odict()
        for filename in os.listdir(self.remotedirpath):
            root, ext = os.path.splitext(filename)
            if ext != '.json' or not root.startswith(self.prefix):
                continue
            prefix, sep, uid = root.partition('.')
            if not uid or prefix != self.prefix:
                continue
            filepath = os.path.join(self.remotedirpath, filename)
            datadict[uid] = self.load(filepath)
        return datadict

    def clearAllRemoteData(self):
        '''
        Remove all the remote data files
        '''
        for filename in os.listdir(self.remotedirpath):
            root, ext = os.path.splitext(filename)
            if ext != '.json' or not root.startswith(self.prefix):
                continue
            prefix, eid = os.path.splitext(root)
            eid = eid.lstrip('.')
            if not eid:
                continue
            filepath = os.path.join(self.remotedirpath, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

class LotKeep(keeping.Keep):
    '''
    RAET protocol endpoint lot persistence

    '''
    Fields = ['uid', 'name', 'ha']

    def __init__(self, prefix='lot', **kwa):
        '''
        Setup LotKeep instance
        '''
        super(LotKeep, self).__init__(prefix=prefix, **kwa)