#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2010 Christian Dannie Storgaard
#
# AUTHOR:
# Christian Dannie Storgaard <cybolic@gmail.com>
#

from __future__ import print_function

import subprocess, os, sys, copy, struct, re
import copy as _copy

XDG_MENU_CATEGORIES = (
    # Main
    'AudioVideo',
    'Audio',
    'Video',
    'Development',
    'Education',
    'Game',
    'Graphics',
    'Network',
    'Office',
    'Settings',
    'System',
    'Utility',
    # Additional
    'Building',
    'Debugger',
    'IDE',
    'GUIDesigner',
    'Profiling',
    'RevisionControl',
    'Translation',
    'Calendar',
    'ContactManagement',
    'Database',
    'Dictionary',
    'Chart',
    'Email',
    'Finance',
    'FlowChart',
    'PDA',
    'ProjectManagement',
    'Presentation',
    'Spreadsheet',
    'WordProcessor',
    '2DGraphics',
    'VectorGraphics',
    'RasterGraphics',
    '3DGraphics',
    'Scanning',
    'OCR',
    'Photography',
    'Publishing',
    'Viewer',
    'TextTools',
    'DesktopSettings',
    'HardwareSettings',
    'Printing',
    'PackageManager',
    'Dialup',
    'InstantMessaging',
    'Chat',
    'IRCClient',
    'FileTransfer',
    'HamRadio',
    'News',
    'P2P',
    'RemoteAccess',
    'Telephony',
    'TelephonyTools',
    'VideoConference',
    'WebBrowser',
    'WebDevelopment',
    'Midi',
    'Mixer',
    'Sequencer',
    'Tuner',
    'TV',
    'AudioVideoEditing',
    'Player',
    'Recorder',
    'DiscBurning',
    'ActionGame',
    'AdventureGame',
    'ArcadeGame',
    'BoardGame',
    'BlocksGame',
    'CardGame',
    'KidsGame',
    'LogicGame',
    'RolePlaying',
    'Simulation',
    'SportsGame',
    'StrategyGame',
    'Art',
    'Construction',
    'Music',
    'Languages',
    'Science',
    'ArtificialIntelligence',
    'Astronomy',
    'Biology',
    'Chemistry',
    'ComputerScience',
    'DataVisualization',
    'Economy',
    'Electricity',
    'Geography',
    'Geology',
    'Geoscience',
    'History',
    'ImageProcessing',
    'Literature',
    'Math',
    'NumericalAnalysis',
    'MedicalSoftware',
    'Physics',
    'Robotics',
    'Sports',
    'ParallelComputing',
    'Amusement',
    'Archiving',
    'Compression',
    'Electronics',
    'Emulator',
    'Engineering',
    'FileTools',
    'FileManager',
    'TerminalEmulator',
    'Filesystem',
    'Monitor',
    'Security',
    'Accessibility',
    'Calculator',
    'Clock',
    'TextEditor',
    'Documentation',
    'Core',
    'KDE',
    'GNOME',
    'GTK',
    'Qt',
    'Motif',
    'Java',
    'ConsoleOnly'
)

WINDOWS_FORMATS = ('application/dos-exe',
                   'application/msdos-windows',
                   'application/x-ms-dos-executable',
                   'application/x-msdos-program',
                   'application/x-msdownload',
                   'application/exe',
                   'application/x-exe',
                   'application/x-dosexec',
                   'application/x-winexe',
                   'application/x-zip-compressed',
                   'application/x-executable',
                   'application/x-msi',
                   'vms/exe',
                   'application/octet-stream', # This is not strictly a Wine format, but EXEs are sometimes reported as it
                   'application/x-ms-shortcut' # This is normally read and changed to a xdg-open cmd, but better safe...
)

BUILTIN_EXECUTABLES = [
    'aspnet_regiis',
    'attrib',
    'cacls',
    'clock',
    'cmd',
    'control',
    'dxdiag',
    'eject',
    'expand',
    'explorer',
    'extrac32',
    'gdi',
    'hh',
    'icinfo',
    'iexplore',
    'ipconfig',
    'krnl386',
    'libntoskrnl',
    'lodctr',
    'mofcomp',
    'mshta',
    'msiexec',
    'net',
    'ngen',
    'notepad',
    'ntoskrnl',
    'oleview',
    'ping',
    'progman'
    'progman',
    'reg',
    'regedit',
    'regsvcs',
    'regsvr32',
    'rpcss',
    'rundll',
    'rundll32',
    'sc',
    'secedit',
    'servicemodelreg',
    'services',
    'spoolsv',
    'start',
    'svchost',
    'taskkill',
    'taskmgr',
    'termsv',
    'uninstaller',
    'unlodctr',
    'user',
    'wineboot',
    'winebrowser',
    'winecfg',
    'wineconsole',
    'winedbg',
    'winedevice',
    'winefile',
    'winemenubuilder',
    'winemine',
    'winepath',
    'winevdm',
    'winhelp',
    'winhlp32',
    'winver',
    'wordpad',
    'write',
    'wscript',
    'xcopy'
]

def ENV_NO_GECKO(env = None):
    """Don't trigger mshtml's gecko install dialog"""
    if env == None:
        env = copy(ENV)
    else:
        env = copy(env)
    env['WINEDLLOVERRIDES'] = 'mshtml='
    return env

def ENV_NO_DISPLAY(env = None):
    if env == None:
        env = copy(ENV)
    else:
        env = copy(env)
    env['DISPLAY'] = '-999:-99.-99'
    return env


class Popen(subprocess.Popen):
    """
    A simple subclass of subprocess.Popen that just hides the bug that appears once in a while
    concerning a missing 'error' attribute in NoneType in the __del__ function of subprocess.Popen"""
    def __init__(self, args, **kwargs):
        if 'env' not in kwargs:
            kwargs['env'] = os.environ

        with open(os.devnull, 'w') as dev_null:
            for std_x in ('stdin', 'stdout', 'stderr'):
                if std_x not in kwargs:
                    kwargs[std_x] = subprocess.PIPE
                elif kwargs[std_x] == 'null':
                    kwargs[std_x] = dev_null
            if (
                kwargs['stderr'] == dev_null or
                kwargs['stderr'] == dev_null
            ) and 'bufsize' not in kwargs:
                kwargs['bufsize'] = 0

            subprocess.Popen.__init__(self, args, **kwargs)

    def __del__(self, *args, **kwargs):
        return_value = None
        try:
            return_value = subprocess.Popen.__del__(self, *args, **kwargs)
        except AttributeError, reason:
            pass
            """try:
                print("Caught that weird Popen error:\n\tError: %s\n\tType: %s" % (
                    reason, type(reason)
                ), file=sys.stderr)
            except AttributeError:
                pass"""
        return return_value

    def result(self):
        """Like communicate() but appends the return code to the returned tuple."""
        output = self.communicate()
        return tuple(list(output[:])+[self.returncode])

def run(*args, **kwargs):
    """
    This command is a shortcut for running Popen and then calling communicate() on the process object.
    As communicate() it returns a tuple in the form of (stdout_string, stderr_string).
    If the keyword argument include_return_code is set as True, the returncode is appended to the tuple."""
    if 'include_return_code' in kwargs and kwargs['include_return_code']:
        del kwargs['include_return_code']
        return Popen(*args, **kwargs).result()
    else:
        return Popen(*args, **kwargs).communicate()

def system(*args, **kwargs):
    """
    A shortcut for running Popen, returning only the return code - a bit like os.system."""
    kwargs['stdin'] = kwargs['stdout'] = kwargs['stderr'] = 'null'
    process = Popen(*args, **kwargs)
    process.communicate()
    return process.returncode

def pipe(commands, **kwargs):
    processes = []
    if 'include_return_code' in kwargs and kwargs['include_return_code']:
        include_return_code = True
        del kwargs['include_return_code']
    else:
        include_return_code = False

    for index, command in enumerate(commands):
        if index == 0:
            processes.append(Popen(
                command,
                **kwargs
            ))
        else:
            processes.append(Popen(
                command,
                stdin = processes[-1].stdout,
                **kwargs
            ))
    if include_return_code:
        return processes[-1].result()
    else:
        return processes[-1].communicate()


def which(command, env=None, extra_paths=None):
    # Adapted from the which() function in pexpect
    # Original copyright 2008 Noah Spurrier under an Open Source license
    # Please see original code at http://pexpect.sourceforge.net/ for full license.

    # If command is a list type, return the first command item that is found
    if type(command) in (list, tuple):
        for subcommand in command:
            new_command = which(subcommand, env)
            if new_command != None:
                return new_command
        return None

    # If command is directly executable, return it as is
    if (command[0] == '/' or command[0] == './') and os.access(command, os.X_OK):
        return command

    if env == None:
        if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
            paths = os.defpath
        else:
            paths = os.environ['PATH']
    else:
        paths = env['PATH']

    pathlist = paths.split(str(os.pathsep))

    if extra_paths != None:
        pathlist += extra_paths

    for path in pathlist:
        filename = os.path.join(path, command)
        if os.access(filename, os.X_OK):
            return filename
    return None


class deferreddict(dict):
    """A subclass of the standard dict class that waits until it is first accessed to run a given function that should return a dict used to fill in the keys and values of the deferreddict\nFirst argument should be the function to run on access."""
    def __init__(self, init_function):
        dict.__init__(self)
        self.__init_function = init_function
        self.__initialised = False

    def __setitem__(self, name, value):
        if not self.__initialised:
            dict.update(self, self.__init_function())
            self.__initialised = True
        return dict.__setitem__(self, name, value)

    def __getitem__(self, name):
        if not self.__initialised:
            dict.update(self, self.__init_function())
            self.__initialised = True
        return dict.__getitem__(self, name)

def value_as_bool(value):
    if (
        value == True or value == 1
    ) or (
        type(value) in (str, unicode) and (
            value.strip().lower() == 'true' or
            value.strip().lower() == 'enabled' or
            'y' in '%s' % value.lower()
        )
    ):
        return True
    elif (
        value == False or value == 0
    ) or (
        type(value) in (str, unicode) and (
            value.strip().lower() == 'false' or
            value.strip().lower() == 'disabled' or
            'n' in '%s' % value.lower()
        )
    ):
        return False
    else:
        return None

def value_type(value):
    """ Return the type of value. Works with strings containing an int, float, list and so on."""
    try:
        value_type = type(eval('%s' % value))
    except:
        value_type = type('')
    return value_type

def any_in_string(chars, string):
    for char in chars:
        if char in string:
            return True
    return False
any_in_object = any_in_string

def all_in_object(objects, object):
    return all((
        i in object
        for i
        in object
    ))

def any_is(any_object, is_object):
    for i in any_object:
        if i == is_object:
            return True
    return False

def list_to_english_or(list_object):
    # Return a literal listing of the list_object, separated with ", " and with
    # "or" before the last item.
    # E.g. ['parrot', 'norwegian', 'polly'] becomes "parrot, norwegian or polly"
    list_object = list(list_object)
    if len(list_object) > 1:
        return _("%s or %s") % (', '.join(list_object[:-1]), list_object[-1])
    else:
        return list_object[0]

def list_to_english_and(list_object):
    # Return a literal listing of the list_object, separated with ", " and with
    # "and" before the last item.
    # E.g. ['parrot', 'norwegian', 'polly'] becomes "parrot, norwegian and polly"
    list_object = list(list_object)
    if len(list_object) > 1:
        return _("%s and %s") % (', '.join(list_object[:-1]), list_object[-1])
    else:
        return list_object[0]

def copy(object):
    """Copy an object. Like copy.deepcopy but hopefully falling over less."""
    object_type = type(object)

    if object_type is int:
        return int(object)

    elif object_type is float:
        return float(object)

    elif object_type is tuple:
        return tuple(( copy(i) for i in object ))

    elif object_type is list:
        return list(( copy(i) for i in object ))

    elif object_type in (str, unicode):
        return object[:]

    elif hasattr(object, 'iteritems'):
        return dict((
            (copy(key), copy(value))
            for key,value in object.iteritems()
        ))

    else:
        return sys.modules['copy'].deepcopy(object)


#
# bitfield manipulation
#
# by Sébastien Keim, available at
# http://code.activestate.com/recipes/113799-bit-field-manipulation/
# Added code to handle registry hex-values.

class bitfield(object):
    def __init__(self,value=0):
        if type(value) in (str, unicode) and value.lower().startswith('hex:'):
            # Reverse it for little-endian
            value = value.split(':')[1].split(',')
            value.reverse()
            # And convert it to an integer
            value = int('0x%s' % ''.join(value), 16)
        self._d = value

    def __getitem__(self, index):
        return (self._d >> index) & 1

    def __setitem__(self,index,value):
        value    = (value&1L)<<index
        mask     = (1L)<<index
        self._d  = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        mask = 2L**(end - start) -1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        mask = 2L**(end - start) -1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        return self._d

    def registry_value(self):
        # Convert the integer to hex and split to two-char chunks
        value = hex(self._d)
        if value.endswith('L'):
            value = value[:-1]
        value = '{0:<08}'.format(value[2:]) # zero-padding
        value = [ value[i:i+2] for i in range(0, len(value), 2) ]
        # Reverse it for big-endian format
        value.reverse()
        # Format it for the registry and return it
        return 'hex:%s' % ','.join( value )


class sorteddict(list):
    def __init__(self, *values):
        if values == None:
            list.__init__(self)
        else:
            list.__init__(self, values)

    def __getitem__(self, key):
        for ikey,value in iter(self):
            if key == ikey:
                return value
        raise KeyError(key)

    def __setitem__(self, key, value):
        return self.append((key, value))

    def get_index(self, index):
        return list.__getitem__(self, index)

    def remove_key(self, key):
        if self.__contains__(key):
            for i in range(len(self)):
                i_key, value = self.get_index(i)
                if i_key == key:
                    del self[i]
                    return
            raise KeyError(key)
        elif type(key) == int:
            del self[key]
        else:
            raise KeyError(key)

    def __contains__(self, key):
        for i_key,i_value in self.iteritems():
            if i_key == key:
                return True
        return False

    def get_key_from_value(self, value):
        for i_key,i_value in self.iteritems():
            if i_value == value:
                return i_key
        return None

    def keys(self):
        return [ key for key,value in self ]

    def values(self):
        return [ value for key,value in self ]

    def iteritems(self):
        return ( (key,value) for key,value in self )

    def iterkeys(self):
        return ( key for key,value in self )

    def itervalues(self):
        return ( value for key,value in self )

    def copy(self):
        return sys.modules['copy'].deepcopy(self)

    def dict(self):
        return dict(self)


def read_cache(cache_key):
    def decorator(func):
        def f(*args, **kwargs):
            try:
                return CACHE[cache_key]
            except KeyError:
                value = func(*args, **kwargs)
                CACHE[cache_key] = value
                return value
        return f
    return decorator

def write_cache(cache_key):
    def decorator(func):
        def f(*args, **kwargs):
            new_value, return_value = func(*args, **kwargs)
            CACHE[cache_key] = new_value
            return return_value
        return f
    return decorator

def clear_cache(cache_key):
    def decorator(func):
        def f(*args, **kwargs):
            #try:
            del CACHE[cache_key]
            #print "Removed cached value for", cache_key
            #except:
            #    pass
            value = func(*args, **kwargs)
            return value
        return f
    return decorator


def detect_wine_installations(extra_paths = None):
    installations = {}
    paths = ENV['PATH'].split(':')
    if extra_paths is not None:
        path += extra_paths
    binaries_found = []
    for path in paths:
        wine_binary = os.path.join(path, 'wine')
        if os.path.exists(wine_binary):
            binaries_found.append(wine_binary)

    search_paths = [
        "/opt/",
        "%s/.local/share/wineversions/" % ENV['HOME'],
        "%s/.PlayOnLinux/wine/linux-amd64/" % ENV['HOME'],
        "%s/.PlayOnLinux/wine/linux-x86/" % ENV['HOME']
    ]
    for search_path in search_paths:
        if os.path.isdir(search_path):
            for file in os.listdir(search_path):
                wine_binary = os.path.join(search_path, file, 'bin', 'wine')
                if os.path.exists(wine_binary):
                    binaries_found.append(wine_binary)

    # Now that we've found a number of Wine binaries
    # let's get their versions and figure out their environment and features
    for wine_binary in binaries_found:
        try:
            version = get_wine_version(wine_binary)
            installations[wine_binary] = version
        except:
            print("Couldn't get version of %s, not using." % wine_binary)
            continue
        installations[wine_binary]['binaries'] = {}
        installations[wine_binary]['binaries']['wine'] = wine_binary
        if os.path.exists(wine_binary+'loader'):
            installations[wine_binary]['binaries']['wineloader'] = wine_binary+'loader'
        else:
            installations[wine_binary]['binaries']['wineloader'] = wine_binary
        if os.path.exists(wine_binary+'server'):
            installations[wine_binary]['binaries']['wineserver'] = wine_binary+'server'
        else:
            installations[wine_binary]['binaries']['wineserver'] = wine_binary

        installations[wine_binary]['supports'] = {
            '64bit': installations[wine_binary]['float'] >= 1.2,
            'csmt': False,
            'check_float_constants': False,
            'dxva2_vaapi': False,
            'eax': False
        }

        base_path = os.path.abspath(wine_binary+'/../../')
        for dll_path in ('lib64', 'lib', 'lib/x86_64-linux-gnu'):

            if not installations[wine_binary]['supports']['csmt']:
                if os.path.exists(os.path.join(base_path, dll_path, 'wine', 'wined3d-csmt.dll.so')):
                    installations[wine_binary]['supports']['csmt'] = True
                    installations[wine_binary]['supports']['csmt_type'] = 'dll'
                elif os.path.exists(os.path.join(base_path, dll_path, 'wine', 'wined3d.dll.so')):
                    for line in open(os.path.join(base_path, dll_path, 'wine', 'wined3d.dll.so')):
                        if 'wined3d_device_get_bo' in line:
                            installations[wine_binary]['supports']['csmt'] = True
                            installations[wine_binary]['supports']['csmt_type'] = 'registry'
                            break

            if not installations[wine_binary]['supports']['check_float_constants']:
                if os.path.exists(os.path.join(base_path, dll_path, 'wine', 'wined3d.dll.so')):
                    for line in open(os.path.join(base_path, dll_path, 'wine', 'wined3d.dll.so')):
                        if 'CheckFloatConstants' in line:
                            installations[wine_binary]['supports']['check_float_constants'] = True
                            break

            if not installations[wine_binary]['supports']['dxva2_vaapi']:
                if os.path.exists(os.path.join(base_path, dll_path, 'wine', 'dxva2.dll.so')):
                    for line in open(os.path.join(base_path, dll_path, 'wine', 'dxva2.dll.so')):
                        if 'vaapi.c' in line: # or 'Software\\Wine\\DXVA2'
                            installations[wine_binary]['supports']['dxva2_vaapi'] = True
                            break

            if not installations[wine_binary]['supports']['eax']:
                if os.path.exists(os.path.join(base_path, dll_path, 'wine', 'dsound.dll.so')):
                    for line in open(os.path.join(base_path, dll_path, 'wine', 'dsound.dll.so')):
                        if 'ds_eax_enabled' in line:
                            installations[wine_binary]['supports']['eax'] = True
                            break

    return installations

def get_wine_version(wine_binary=None):
    if wine_binary is None:
        wine_binary = ENV['WINE']

    name = "Wine"
    version = run([wine_binary, '--version'], env=ENV_NO_DISPLAY())[0]
    if version.startswith('wine-'):
        if 'staging' in version.lower():
            name = "Wine Staging"
        elif 'wine-devel' in wine_binary:
            name = "Wine Development"
        version = version.split('wine-')[1].strip()
    # CrossOver type version info
    elif 'product name' in version.lower() and 'product version' in version.lower():
        # Split by lines
        version = re.split('\n+', version)
        # Split by ':', maximum two entries per line, ignore empty lines
        version = [ re.split('\s?:\s?', line, 2) for line in version if len(line) ]
        # Lower case the first entry of each line and build dictionary from result
        version_info = dict([ [ entry[0].lower(), entry[1].strip() ] for entry in version ])
        version = version_info['product version']
        name    = version_info['product name']

    version_parts = [
        int(''.join([ i for i in part.split('-')[0] if i in list('0123456789') ]))
        for part in version.split('.')
    ]
    version_major, version_minor, version_micro, version_nano = version_parts[:4] + [0]*(4 -len(version_parts))

    if '(' in version:
        version_extra = version.split('(')[-1].split(')')[0].strip()
    else:
        version_extra = '-'.join(version.split('-')[1:]).strip()
    if version_extra is None and version_nano != None:
        version_extra = version_nano
    # Ignore "Staging", we already set the name variable for this case
    if version_extra.lower() == 'staging':
        # version_extra = None
        version = re.sub(r'\s*\([Ss]taging\)\s*', '', version)

    version_float = float('%s.%s%s%s' % (version_major, version_minor, version_micro, version_nano))

    return {
        'version' : version,
        'major'   : version_major,
        'minor'   : version_minor,
        'micro'   : version_micro,
        'extra'   : version_extra,
        'float'   : version_float,
        'name'    : name
    }

#ENV = copy.deepcopy(os.environ) # This doesn't seem to actually deepcopy :/
ENV = copy(os.environ)

WINE_ORIGINAL = which('wine')

if WINE_ORIGINAL is None:
    wine_versions = detect_wine_installations()
    if len(wine_versions.keys()):
        wine_versions = {
            version_info['float']: binary_path for
            binary_path, version_info in wine_versions.items()
        }
        WINE_ORIGINAL = wine_versions[ sorted(wine_versions.keys())[-1] ]

        if ENV.has_key('WINE'):
            print("Notice: The Wine binary set in the environment variable 'WINE' doesn't exist. Using '%s' instead." % WINE_ORIGINAL)
        else:
            print("Notice: Wine was not found in PATH. Using '%s' instead." % WINE_ORIGINAL)
        ENV['WINE'] = WINE_ORIGINAL
        ENV['WINELOADER'] = WINE_ORIGINAL
        ENV['WINESERVER'] = WINE_ORIGINAL+'server'
    else:
        print("Error: Wine is not installed.", file=sys.stderr)
        exit(1)

if 'HOME' not in ENV:
    ENV['HOME'] = os.path.expanduser('~')
if 'WINEPREFIX' not in ENV:
    ENV['WINEPREFIX'] = os.path.expanduser('~/.wine')
if 'WINEDEBUG' not in ENV:
    ENV['WINEDEBUG'] = 'fixme-all,trace-all'
if 'WINE' not in ENV:
    ENV['WINE'] = WINE_ORIGINAL
if 'WINELOADER' not in ENV:
    ENV['WINELOADER'] = WINE_ORIGINAL
if 'WINESERVER' not in ENV:
    ENV['WINESERVER'] = WINE_ORIGINAL+'server'
ENV['VINEYARD_DATA'] = os.path.join(ENV['WINEPREFIX'], 'vineyard')

_current_file_dir = os.path.abspath(os.path.curdir)
ENV['VINEYARDDATAPATH'] = _current_file_dir
if all(
    os.path.exists(
        i.format(current_file_dir = _current_file_dir)
    )
    for i in [
        '{current_file_dir}/data',
        '{current_file_dir}/python-wine',
        '{current_file_dir}/vineyard',
    ]
):
    ENV['VINEYARDDATAPATH'] = os.path.abspath('{0}/data'.format(_current_file_dir))
else:
    for _prefix in [
        os.path.sep.join(i.split(os.path.sep)[:-1])
        for i
        in ENV.get('PATH', (
            os.path.expanduser('~/.local'), '/usr/local', '/usr')
        ).split(':')
    ]:
        if os.path.isdir( "{prefix}/share/vineyard".format(prefix = _prefix) ):
            ENV['VINEYARDDATAPATH'] = i
            break

if 'VINEYARDPATH' not in ENV:
    ENV['VINEYARDPATH'] = os.path.expanduser('~/.vineyard')
ENV['VINEYARDCONF'] = ''
ENV['VINEYARDCONFNAME'] = ''

if 'VINEYARDTMP' not in ENV or not os.access(ENV['VINEYARDTMP'], os.W_OK):
    ENV['VINEYARDTMP'] = '/tmp/vineyard-{uid}'.format(uid = os.getuid())
if not os.path.isdir(ENV['VINEYARDTMP']):
    os.mkdir(ENV['VINEYARDTMP'])

if 'LD_LIBRARY_PATH' in ENV:
    ENV['LD_LIBRARY_PATH'] = '{vineyard_path}/lib:{existing_paths}'.format(
        vineyard_path = ENV['VINEYARDPATH'],
        existing_paths = ENV['LD_LIBRARY_PATH']
    )
else:
    ENV['LD_LIBRARY_PATH'] = '{vineyard_path}/lib'.format(
        vineyard_path = ENV['VINEYARDPATH']
    )
_paths = ':'.join([
    '{0}/bin'.format(ENV['VINEYARDPATH']),
    '{0}/bin'.format(ENV['VINEYARDDATAPATH']),
    '/usr/local/share/vineyard/bin',
    '/usr/share/vineyard/bin'
])
if 'PATH' in ENV:
    ENV['PATH'] = '{paths}:{existing_paths}'.format(
        paths = _paths,
        existing_paths = ENV['PATH']
    )
else:
    ENV['PATH'] = _paths

ENV_BASE = copy(ENV)


for path in (
    ENV['VINEYARDPATH'],
    '{0}/process_info'.format(ENV['VINEYARDPATH']),
    '{0}/mounted_files'.format(ENV['VINEYARDPATH'])
):
    if not os.path.exists(path):
        os.mkdir(path)


VERSION_INFO = get_wine_version()
VERSION, VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO, VERSION_EXTRA = (VERSION_INFO[k] for k in ['version', 'major', 'minor', 'micro', 'extra'])

DONT_PARSE_EXECUTABLES_WITH_SIZE_ABOVE_MB = 50

