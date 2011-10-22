import sys
import traceback
from pprint import pprint
from collections import deque


class Eval(object):
    """ Template EVAL statement. """
    def __init__(self, stmt):
        self.stmt = stmt

    def render(self, context):
        """ Renders a statement in a context.  """
        try:
            return unicode(eval(self.stmt, context))
        except SyntaxError:
            exec self.stmt in context
            return ''


class AttrDict(dict):
    """
    Dictionary class that allows for accessing members as attributes or via
    regular dictionary lookup.

    """
    def __init__(self, init=None, **kwargs):
        if init and kwargs:
            raise TypeError
        if init:
            self.__dict__.update(init)
        if kwargs:
            self.__dict__.update(kwargs)

    def __setitem__(self, item, val):
        self.__dict__[item] = val

    def __getitem__(self, item):
        return self.__dict__[item]

    def __delitem__(self, item):
        del self.__dict__[item]

    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __eq__(self, rhs):
        return self.__dict__.__eq__(rhs)

    def __nonzero__(self):
        return self.__dict__.__nonzero__()

    def __repr__(self):
        return self.__dict__.__repr__()

    def __str__(self):
        return self.__dict__.__str__()


class Context(AttrDict):
    """
    A render context.

    """


def compile_template(template, context, show_debug=False):
    end = len(template)
    index = deque()
    rendered = deque()
    funcs = deque()
    contexts = deque()
    closing = deque()
    branches = deque()

    def debug(stmt):
        if show_debug:
            pprint(stmt)

    def get_context():
        cont = {}
        for i in xrange(len(contexts)):
            cont.update(contexts[i])
        debug("CONTEXT: %s" % cont)
        return cont

    def find_tag():
        # Branching
        # 2 - skipping due to exclusion
        # 1 - skipping due to False
        # 0 - good to go

        def render(stuff):
            if (branches and not branches[-1]) or not branches:
                rendered.append(stuff)

        search_start = index[-1]
        i = search_start
        i = template.find('%', search_start)

        if i == -1:
            debug("EOF")
            render(template[search_start:i])
            return

        i += 1
        if template[i] != '{':
            debug("NO TAG")
            index[-1] = i
            funcs.append(find_tag)
            render(template[search_start:i])
            return

        tag_start = i + 1
        i = template.find('}', tag_start)

        if i == -1:
            debug("ERROR: unclosed tag")
            raise RuntimeError("ERROR: unclosed tag")

        tag_end = i
        tag = template[tag_start:tag_end].strip()
        debug("FOUND: %s" % template[tag_start:tag_end])

        render(template[search_start:tag_start-2])
        tag_end += 1

        def for_stmt():
            for_tag = tag_end
            iter_expr = tag[4:].split(' in ')
            names = [_.strip() for _ in iter_expr[0].split(',')]
            iterable = iter_expr[1].strip()
            debug("FOR %s in %s" % (names, iterable))
            iterable = iter(eval(iterable, get_context()))
            index.append(for_tag)

            def for_loop():
                vals = iterable.next()
                debug("ITERATING LOOP")
                if not isinstance(vals, (list, tuple)):
                    vals = [vals]
                index.append(for_tag)
                contexts.append(dict(zip(names, vals)))
                # funcs.append(find_tag)

            def end_for(tag_end):
                # def end_for():
                index.pop()
                contexts.pop()
                try:
                    for_loop()
                    closing.append(end_for)
                except StopIteration:
                    debug("END ITERATION")
                    index.pop()
                    index[-1] = tag_end

            for_loop()
            closing.append(end_for)

        def end_if(tag_end):
            branches.pop()
            index[-1] = tag_end

        if tag.startswith('if '):
            debug("IF statement")
            if (branches and not branches[-1]) or not branches:
                expr = tag[3:]
                if eval(expr, get_context()):
                    branches.append(0)
                else:
                    branches.append(1)
            else:
                branches.append(2)
            closing.append(end_if)
        elif tag.startswith('for '):
            debug("FOR statement")
            if (branches and not branches[-1]) or not branches:
                for_stmt()
        elif tag.startswith('elif '):
            debug("ELIF statement")
            if branches:
                if branches.pop() == 1:
                    expr = tag[5:]
                    if eval(expr, get_context()):
                        branches.append(0)
                    else:
                        branches.append(1)
                else:
                    branches.append(2)
            else:
                raise RuntimeError("Mismatched ELIF.")
        elif tag == 'else':
            debug("ELSE statement")
            if branches:
                if branches.pop() == 1:
                    branches.append(0)
                else:
                    branches.append(2)
            else:
                raise RuntimeError("Mismatched ELSE.")
        elif tag == 'end':
            debug("END statement")
            closing.pop()(tag_end)
            funcs.append(find_tag)
            return
        else:
            debug("EVAL statement")
            render(eval(tag, get_context()))

        index[-1] = tag_end
        funcs.append(find_tag)

    index.append(0)
    contexts.append(context)
    funcs.append(find_tag)
    while funcs:
        funcs.pop()()

    return ''.join(unicode(_) for _ in rendered)



def render_template(template, context, show_debug=False):
    end = len(template)
    index = deque()
    rendered = deque()
    funcs = deque()
    contexts = deque()
    closing = deque()
    branches = deque()

    def debug(stmt):
        if show_debug:
            pprint(stmt)

    def get_context():
        cont = {}
        for i in xrange(len(contexts)):
            cont.update(contexts[i])
        debug("CONTEXT: %s" % cont)
        return cont

    def find_tag():
        # Branching
        # 2 - skipping due to exclusion
        # 1 - skipping due to False
        # 0 - good to go

        def render(stuff):
            if (branches and not branches[-1]) or not branches:
                rendered.append(stuff)

        search_start = index[-1]
        i = search_start
        while i < end and template[i] != '%':
            i += 1

        if i >= end - 1:
            debug("EOF")
            render(template[search_start:i])
            return

        i += 1
        if template[i] != '{':
            debug("NO TAG")
            index[-1] = i
            funcs.append(find_tag)
            render(template[search_start:i])
            return

        tag_start = i + 1
        while i < end and template[i] != '}':
            i += 1

        if i == end:
            debug("ERROR: unclosed tag")
            raise RuntimeError("ERROR: unclosed tag")

        tag_end = i
        tag = template[tag_start:tag_end].strip()
        debug("FOUND: %s" % template[tag_start:tag_end])

        render(template[search_start:tag_start-2])
        tag_end += 1

        def for_stmt():
            for_tag = tag_end
            iter_expr = tag[4:].split(' in ')
            names = [_.strip() for _ in iter_expr[0].split(',')]
            iterable = iter_expr[1].strip()
            debug("FOR %s in %s" % (names, iterable))
            iterable = iter(eval(iterable, get_context()))
            index.append(for_tag)

            def for_loop():
                vals = iterable.next()
                debug("ITERATING LOOP")
                if not isinstance(vals, (list, tuple)):
                    vals = [vals]
                index.append(for_tag)
                contexts.append(dict(zip(names, vals)))
                # funcs.append(find_tag)

            def end_for(tag_end):
                # def end_for():
                index.pop()
                contexts.pop()
                try:
                    for_loop()
                    closing.append(end_for)
                except StopIteration:
                    debug("END ITERATION")
                    index.pop()
                    index[-1] = tag_end

            for_loop()
            closing.append(end_for)

        def end_if(tag_end):
            branches.pop()
            index[-1] = tag_end

        if tag.startswith('if '):
            debug("IF statement")
            if (branches and not branches[-1]) or not branches:
                expr = tag[3:]
                if eval(expr, get_context()):
                    branches.append(0)
                else:
                    branches.append(1)
            else:
                branches.append(2)
            closing.append(end_if)
        elif tag.startswith('for '):
            debug("FOR statement")
            if (branches and not branches[-1]) or not branches:
                for_stmt()
        elif tag.startswith('elif '):
            debug("ELIF statement")
            if branches:
                if branches.pop() == 1:
                    expr = tag[5:]
                    if eval(expr, get_context()):
                        branches.append(0)
                    else:
                        branches.append(1)
                else:
                    branches.append(2)
            else:
                raise RuntimeError("Mismatched ELIF.")
        elif tag == 'else':
            debug("ELSE statement")
            if branches:
                if branches.pop() == 1:
                    branches.append(0)
                else:
                    branches.append(2)
            else:
                raise RuntimeError("Mismatched ELSE.")
        elif tag == 'end':
            debug("END statement")
            closing.pop()(tag_end)
            funcs.append(find_tag)
            return
        else:
            debug("EVAL statement")
            render(eval(tag, get_context()))

        index[-1] = tag_end
        funcs.append(find_tag)

    index.append(0)
    contexts.append(context)
    funcs.append(find_tag)
    while funcs:
        funcs.pop()()

    return ''.join(unicode(_) for _ in rendered)


def test_compile_template_with_template_test_html():
    txt = open('tmp/template_test.html', 'r')
    _ = txt.read()
    txt.close()
    txt = _

    context = {
            'var':'successful test',
            'num':5,
            }
    output = u'''<html>\n    <head>\n        <title>This is a test!</title>\n    </head>\n    <body>\n        <h1>This is a successful test.</h1>\n        <h2>This is an expression SUCCESSFUL TEST.</h1>\n        <ul>\n            \n            <li>Here we have 0 (even).</li>\n            \n            <li>Here we have 1 (odd).</li>\n            \n            <li>Here we have 2 (even).</li>\n            \n            <li>Here we have 3 (odd).</li>\n            \n            <li>Here we have 4 (even).</li>\n            \n        </ul>\n        <ul>\n            \n            <li>My foo is few.</li>\n            \n            <li>My bar is barr.</li>\n            \n        </ul>\n        <ul>\n            \n            <li>Two:\n                <ul>\n                    \n                    <li>0... </li>\n                    \n                    <li>1... </li>\n                    \n                </ul>\n            </li>\n            \n            <li>Three:\n                <ul>\n                    \n                    <li>1... </li>\n                    \n                    <li>2... </li>\n                    \n                    <li>3... </li>\n                    \n                </ul>\n            </li>\n            \n        </ul>\n        <p>This is a % but not a tag.</p>\n        <p>This is a { but not a tag.</p>\n        <p>This } should be ignored completely.</p>\n        \n        <h5>The number was 5.</h5>\n        \n        \n        <h2>The number was five or smaller.</h2>\n        \n        <h5>It was 5, how boring.</h5>\n        \n        <h3>0, 1, 2, 3, 4, </h3>\n        <h4>0,1,2,3,4</h4>\n        \n    </body>\n</html>\n'''.strip()

    result = compile_template(txt, context).strip()
    assert output == result


def test_attrdict_init_empty():
    AttrDict()

def test_attrdict_init_with_kwargs():
    assert {'foo':'bar'} == AttrDict(foo='bar')

def test_attrdict_init_with_dict():
    assert {'foo':'bar'} == AttrDict({'foo':'bar'})


def test_eval_expression():
    assert u'5' == Eval('num').render(Context(num=5))


def test_eval_statement():
    context = Context()
    assert '' == Eval('num = 5').render(context)
    assert 5 == context.num


def run_tests(verbose=False):
    tests = {}
    for name, obj in globals().iteritems():
        if name.startswith('test_') and callable(obj):
            tests[name] = obj

    for name in sorted(tests.keys()):
        try:
            tests[name]()
            if verbose:
                print "success: %s" % name
            else:
                sys.stdout.write('.')
        except:
            print "FAIL: %s" % name
            traceback.print_exc()
    print


if __name__ == '__main__':
    run_tests()

