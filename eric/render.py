import tenjin
from webext import (escape, escape_html, set_encoding, to_str, get_encoding)
from tenjin.helpers import (cache_as, capture_as, CaptureContext, captured_as,
        echo, echo_cached, fragment_cache, html, new_cycle, re, start_capture,
        stop_capture, sys, unquote, not_cached)

class TenjinTemplate(tenjin.Template):
    preamble = ';'.join((
        "import pprint",
        "globals()['pprint'] = pprint",
        "globals()['_context'] = _context",
        "base_template = lambda name: _context.__setitem__('_layout', name)",
        "debug_context = lambda: pprint.pprint(_context)",
        ))

# Configure Tenjin
tenjin.Engine.templateclass = TenjinTemplate
TenjinTemplate.engine = tenjin.Engine(path=['.'], postfix='.pyhtml')


def with_tenjin(context=None, template=None):
    assert template
    context = context or {}
    return TenjinTemplate.engine.render(template, context)

