import hotshot
import os
import time
import settings
import tempfile

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = tempfile.gettempdir()


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer

import StringIO
import hotshot.stats
import traceback
from django.template import Template, Context
from debug_toolbar.panels import DebugPanel


#Debug toolbar profile panel
class ProfilingPanel(DebugPanel):
    """
    Panel that runs the hotshot profiler during the request.
    """

    name = 'Profiling'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(ProfilingPanel, self).__init__(*args, **kwargs)
        self.formatted_stats = ''
        self.stats = None

    def nav_title(self):
        """Title showing in toolbar"""
        return 'Profiling'

    def nav_subtitle(self):
        """Subtitle showing until title in toolbar"""
        if self.stats:
            return "%d function calls in %.3f CPU seconds" % (self.stats.total_calls, self.stats.total_tt)
        else:
            return "self.stats evaluates to False"

    def title(self):
        """Title showing in panel"""
        return 'Profiling'

    def url(self):
        return ''

    def content(self):
        if self.stats and not self.formatted_stats:
            try:
                buffer = StringIO.StringIO()
                self.stats.stream = buffer
                self.stats.sort_stats('time', 'calls')
                self.stats.print_stats(100)
                self.formatted_stats = buffer.getvalue()
            except:
                print "Error getting hotshot stats:"
                traceback.print_exc()

        template = Template("""<code>{{ formatted_stats }}</code>""")
        context = Context()
        context.update(self.context)
        context.update({
            'formatted_stats': self.formatted_stats,
        })
        return template.render(context)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith(settings.ADMIN_MEDIA_PREFIX) or request.path.startswith('/__debug__/'):
            return None

        # Add a timestamp to the profile output when the callable is actually called.
        handle, filename = tempfile.mkstemp(prefix='profiling')
        os.close(handle)
        prof = hotshot.Profile(filename)
        try:
            try:
                try:
                    result = prof.runcall(view_func, *((request,) + view_args), **view_kwargs)
                finally:
                    prof.close()
            except:
                raise
            else:
                self.stats = hotshot.stats.load(filename)
                return result
        finally:
            os.unlink(filename)