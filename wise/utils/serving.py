# Copyright (c) 2010 by the Werkzeug Team, see AUTHORS for more details.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * The names of the contributors may not be used to endorse or
#       promote products derived from this software without specific
#       prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys, os
import thread
import subprocess
import time

def reloader_loop(extra_files=None, interval=1):
    """When this function is run from the main thread, it will force other
    threads to exit when any modules currently loaded change.

    Copyright notice.  This function is based on the autoreload.py from
    the CherryPy trac which originated from WSGIKit which is now dead.

    :param extra_files: a list of additional files it should watch.
    """
    def iter_module_files():
        for module in sys.modules.values():
            filename = getattr(module, '__file__', None)
            if filename:
                old = None
                while not os.path.isfile(filename):
                    old = filename
                    filename = os.path.dirname(filename)
                    if filename == old:
                        break
                else:
                    if filename[-4:] in ('.pyc', '.pyo'):
                        filename = filename[:-1]
                    yield filename

    fnames = []
    fnames.extend(iter_module_files())
    fnames.extend(extra_files or ())

    reloader(fnames, interval=interval)

def _reloader_stat_loop(fnames, interval=1):
    mtimes = {}
    while 1:
        for filename in fnames:
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue

            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                #_log('info', ' * Detected change in %r, reloading' % filename)
                sys.exit(3)
        time.sleep(interval)

def _reloader_inotify(fnames, interval=None):
    #: Mutated by inotify loop when changes occur.
    changed = [False]

    # Setup inotify watches
    from pyinotify import WatchManager, EventsCodes, Notifier
    wm = WatchManager()
    mask = "IN_DELETE_SELF IN_MOVE_SELF IN_MODIFY IN_ATTRIB".split()
    mask = reduce(lambda m, a: m | getattr(EventsCodes, a), mask, 0)

    def signal_changed(event):
        if changed[0]:
            return
        #_log('info', ' * Detected change in %r, reloading' % event.path)
        changed[:] = [True]

    for fname in fnames:
        wm.add_watch(fname, mask, signal_changed)

    # ... And now we wait...
    notif = Notifier(wm)
    try:
        while not changed[0]:
            notif.process_events()
            if notif.check_events(timeout=interval):
                notif.read_events()
            # TODO Set timeout to something small and check parent liveliness
    finally:
        notif.stop()
    sys.exit(3)

# Decide which reloader to use
try:
    __import__("pyinotify")   # Pyflakes-avoidant
except ImportError:
    reloader = _reloader_stat_loop
    reloader_name = "stat() polling"
else:
    reloader = _reloader_inotify
    reloader_name = "inotify events"


def restart_with_reloader():
    """Spawn a new Python interpreter with the same arguments as this one,
    but running the reloader thread.
    """
    while 1:
        #_log('info', ' * Restarting with reloader: %s', reloader_name)
        args = [sys.executable] + sys.argv
        new_environ = os.environ.copy()
        new_environ['WERKZEUG_RUN_MAIN'] = 'true'

        # a weird bug on windows. sometimes unicode strings end up in the
        # environment and subprocess.call does not like this, encode them
        # to latin1 and continue.
        if os.name == 'nt':
            for key, value in new_environ.iteritems():
                if isinstance(value, unicode):
                    new_environ[key] = value.encode('iso-8859-1')

        exit_code = subprocess.call(args, env=new_environ)
        if exit_code != 3:
            return exit_code


def run_with_reloader(main_func, extra_files=None, interval=1):
    """Run the given function in an independent python interpreter."""
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        thread.start_new_thread(main_func, ())
        try:
            reloader_loop(extra_files, interval)
        except KeyboardInterrupt:
            return
    try:
        sys.exit(restart_with_reloader())
    except KeyboardInterrupt:
        pass
