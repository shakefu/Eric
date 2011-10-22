import sys
import pdb
import traceback
from pprint import pprint
from collections import deque, MutableMapping


class UNSET(object):
    def __repr__(self):
        return "UNSET"

    def __nonzero__(self):
        return False

    def __eq__(self, rhs):
        return self.__class__ == rhs.__class__

UNSET = UNSET()


# class Statement(object):
#     def render(self, context):
#         return ''
#
#     def render(self, context, branch):
#         return None

class Branching(object):
    def __init__(self):
        self.state = deque()

    def push(self):
        self.debug("BRANCH PUSH %s" % self.state)
        self.state.append(None)

    def skip(self):
        self.debug("BRANCH SKIP %s" % self.state)
        self.state.append(True)

    def next(self):
        self.debug("BRANCH NEXT %s" % self.state)
        self.state.append(False)

    def pop(self):
        self.debug("BRANCH POP %s" % self.state)
        return self.state.pop()

    def debug(self, stmt):
        if False:
            print "  " * (len(self.state) + 1) + stmt

    @property
    def branch(self):
        if not self.state:
            return None
        return self.state[-1]


    def allow_if(self, val):
        self.debug("BRANCH IF")
        if self.branch is not None:
            raise RuntimeError("Mismatched IF")
        if val:
            self.skip()
            self.push()
            return True
        else:
            self.next()
            return False

    def allow_elif(self, val):
        self.debug("BRANCH ELIF")
        if self.branch is None:
            raise RuntimeError("Mismatched ELIF")
        if self.branch:
            return False
        if val:
            self.skip()
            self.push()
            return True
        else:
            return False

    def allow_else(self):
        self.debug("BRANCH ELSE")
        if self.branch is None:
            pdb.set_trace()
            raise RuntimeError("Mismatched ELSE")
        if self.branch:
            return False
        self.pop()
        self.push()
        return True


class Literal(object):
    def __init__(self, stmt):
        self.stmt = unicode(stmt)

    def render(self, context, branch):
        branch.debug("LITERAL: %s" % self.stmt)
        if branch.branch is not None:
            branch.pop()
        yield self.stmt


class Eval(object):
    def __init__(self, stmt):
        self.stmt = stmt

    def render(self, context, branch):
        branch.debug("EVAL: %s" % self.stmt)
        if branch.branch is not None:
            branch.pop()
        try:
            yield unicode(eval(self.stmt, {}, context))
        except SyntaxError:
            exec self.stmt in context.as_dict()
            yield ''


class Block(object):
    def __init__(self):
        self.stmts = []

    def append(self, stmt):
        self.stmts.append(stmt)

    def extend(self, stmts):
        self.stmts.extend(stmts)

    def _render(self, context, branch):
        for stmt in self.stmts:
            for item in stmt.render(context, branch):
                yield item

    render = _render


class CompiledTemplate(Block):
    def render(self, context):
        if not isinstance(context, Context):
            context = Context(context)
        return ''.join(_ for _ in self._render(context, Branching()))


class If(Block):
    def __init__(self, expr):
        super(If, self).__init__()
        self.expr = expr

    def render(self, context, branch):
        branch.debug("IF %s" % self.expr)
        if branch.allow_if(eval(self.expr, {}, context)):
            for item in self._render(context, branch):
                yield item
            branch.pop()
            yield ''


class ElIf(Block):
    def __init__(self, expr):
        super(ElIf, self).__init__()
        self.expr = expr

    def render(self, context, branch):
        branch.debug("ELIF %s" % self.expr)
        if branch.allow_elif(eval(self.expr, {}, context)):
            for item in self._render(context, branch):
                yield item
            branch.pop()
            yield ''


class Else(Block):
    def render(self, context, branch):
        branch.debug("ELSE")
        if branch.allow_else():
            for item in self._render(context, branch):
                yield item
            branch.pop()
            yield ''
        else:
            branch.pop()
            yield ''


class For(Block):
    def __init__(self, iter_expr):
        super(For, self).__init__()
        iter_expr = iter_expr.split(' in ')
        self.names = [_.strip() for _ in iter_expr[0].split(',')]
        self.expr = iter_expr[1].strip()

    def render(self, context, branch):
        branch.debug("FOR %s in %s" % (self.names, self.expr))
        if branch.branch is not None:
            branch.pop()
        for vals in iter(eval(self.expr, {}, context)):
            for stmt in self.stmts:
                for item in stmt.render(context.push(Context(zip(
                    self.names, vals \
                            if isinstance(vals, (list, tuple)) \
                            else [vals]))),
                            branch):
                    yield item


class AttrDict(MutableMapping):
    """
    Dictionary class that allows for accessing members as attributes or via
    regular dictionary lookup.

    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __cmp__(self, rhs):
        return self.__dict__.__cmp__(rhs)

    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __delitem__(self, item):
        return self.__dict__.__delitem__(item)

    def __eq__(self, rhs):
        return self.__dict__.__eq__(rhs)

    def __format__(self):
        return self.__dict__.__format__()

    def __ge__(self, rhs):
        return self.__dict__.__ge__(rhs)

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)

    def __gt__(self, rhs):
        return self.__dict__.__gt__(rhs)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __le__(self, rhs):
        return self.__dict__.__le__(rhs)

    def __len__(self):
        return self.__dict__.__len__()

    def __lt__(self, rhs):
        return self.__dict__.__lt__(rhs)

    def __ne__(self, rhs):
        return self.__dict__.__ne__(rhs)

    def __repr__(self):
        return self.__dict__.__repr__()

    def __setitem__(self, item, val):
        return self.__dict__.__setitem__(item, val)

    def __str__(self):
        return self.__dict__.__str__()

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__class__(self.__dict__.copy())

    def fromkeys(self, keys, values=None):
        return self.__dict__.fromkeys(keys, values)

    def get(self, item, default=UNSET):
        if default != UNSET:
            return self.__dict__.get(item, default)
        return self.__dict__.get(item)

    def has_key(self, key):
        return self.__dict__.has_key(key)

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return self.__dict__.iteritems()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def keys(self):
        return self.__dict__.keys()

    def pop(self, key, default=UNSET):
        if default != UNSET:
            return self.__dict__.pop(key, default)
        return self.__dict__.pop(key)

    def popitem(self):
        return self.__dict__.popitem()

    def setdefault(self, default):
        return self.__dict__.setdefault(default)

    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def values(self):
        return self.__dict__.values()

    def viewitems(self):
        return self.__dict__.viewitems()

    def viewkeys(self):
        return self.__dict__.viewkeys()

    def as_dict(self):
        return self.__dict__


class Context(AttrDict):
    """
    A render context.

    """
    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)

    def push(self, sub):
        context = self.copy()
        context.update(sub)
        return context


class TemplateError(Exception):
    pass


TAG = '%'
TAG_OPEN = '{'
TAG_END = '}'

def parse(template, show_debug=False):
    end = len(template)
    line = 1
    tag_end = 0
    stack = deque()
    #TODO: Pass name and stuff in here
    stack.append(CompiledTemplate())

    def debug(stmt):
        if show_debug:
            print stmt

    while tag_end < end:
        i = template.find(TAG, tag_end)
        if i == -1 or i >= end - 1:
            debug("EOF: %s" % template[tag_end:])
            stack[-1].append(Literal(template[tag_end:]))
            break

        i += 1
        if template[i] != TAG_OPEN:
            debug("NO TAG: %s" % template[tag_end:i])
            stack[-1].append(Literal(template[tag_end:i]))
            tag_end = i
            continue

        tag_start = i + 1
        search_start = tag_end
        tag_end = template.find(TAG_END, tag_start)
        if i == -1:
            debug("ERROR: unclosed tag")
            raise RuntimeError("ERROR: unclosed tag")

        tag_expr = template[tag_start:tag_end]
        debug("FOUND: %s" % tag_expr)

        stack[-1].append(Literal(template[search_start:tag_start-2]))
        tag_end += 1

        if tag_expr.startswith('if '):
            debug("IF %s" % tag_expr)
            tag = If(tag_expr[3:])
            stack[-1].append(tag)
            stack.append(tag)
        elif tag_expr.startswith('for '):
            debug("FOR %s" % tag_expr)
            tag = For(tag_expr[4:])
            stack[-1].append(tag)
            stack.append(tag)
        elif tag_expr.startswith('elif '):
            debug("ELIF %s" % tag_expr)
            if not isinstance(stack.pop(), If):
                raise TemplateError("Mismatched ELIF")
            tag = ElIf(tag_expr[5:])
            stack[-1].append(tag)
            stack.append(tag)
        elif tag_expr == 'else':
            debug("ELSE")
            if not isinstance(stack.pop(), (If, ElIf)):
                raise TemplateError("Mismatched ELSE")
            tag = Else()
            stack[-1].append(tag)
            stack.append(tag)
        elif tag_expr == 'end':
            debug("END")
            if not isinstance(stack.pop(), (For, If, ElIf, Else)):
                raise TemplateError("Mismatched END")
        else:
            debug("EVAL %s" % tag_expr)
            tag = Eval(tag_expr)
            stack[-1].append(tag)

    if len(stack) > 1:
        debug("Unmatched tags. Stack height: %s" % len(stack))
    return stack[0]


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


def test_if():
    assert "If" == parse("%{if True}If%{end}").render({})


def test_if_not():
    assert '' == parse("%{if False}If%{end}").render({})


def test_else():
    assert "Else" == parse("%{if False}If%{else}Else%{end}").render({})


def test_if_not_else():
    assert "If" == parse("%{if True}If%{else}Else%{end}").render({})


def test_if_not_elif():
    assert "If" == parse("%{if True}If%{elif True}Elif%{end}").render({})


def test_if_elif():
    assert "Elif" == parse("%{if False}If%{elif True}Elif%{end}").render({})


def test_not_if_elif():
    assert "Neither" == parse("%{if False}If%{elif False}Elif%{end}Neither").render({})


def test_if_elif_not_else():
    assert "Else" == parse("%{if False}If%{elif False}Elif%{else}Else%{end}").render({})

def test_not_if_else_more():
    assert "ElseMore" == parse("%{if False}If%{else}Else%{end}More").render({})


def test_template_test_html():
    txt = open('tmp/template_test.html', 'r')
    _ = txt.read()
    txt.close()
    txt = _

    context = {
            'var':'successful test',
            'num':5,
            }
    output = u'''<html>\n    <head>\n        <title>This is a test!</title>\n    </head>\n    <body>\n        <h1>This is a successful test.</h1>\n        <h2>This is an expression SUCCESSFUL TEST.</h1>\n        <ul>\n            \n            <li>Here we have 0 (even).</li>\n            \n            <li>Here we have 1 (odd).</li>\n            \n            <li>Here we have 2 (even).</li>\n            \n            <li>Here we have 3 (odd).</li>\n            \n            <li>Here we have 4 (even).</li>\n            \n        </ul>\n        <ul>\n            \n            <li>My foo is few.</li>\n            \n            <li>My bar is barr.</li>\n            \n        </ul>\n        <ul>\n            \n            <li>Two:\n                <ul>\n                    \n                    <li>0... </li>\n                    \n                    <li>1... </li>\n                    \n                </ul>\n            </li>\n            \n            <li>Three:\n                <ul>\n                    \n                    <li>1... </li>\n                    \n                    <li>2... </li>\n                    \n                    <li>3... </li>\n                    \n                </ul>\n            </li>\n            \n        </ul>\n        <p>This is a % but not a tag.</p>\n        <p>This is a { but not a tag.</p>\n        <p>This } should be ignored completely.</p>\n        \n        <h5>The number was 5.</h5>\n        \n        \n        <h2>The number was five or smaller.</h2>\n        \n        <h5>It was 5, how boring.</h5>\n        \n        <h3>0, 1, 2, 3, 4, </h3>\n        <h4>0,1,2,3,4</h4>\n        \n    </body>\n</html>\n'''.strip()

    result = parse(txt).render(context).strip()
    assert output == result


def test_eval_expression():
    context = Context(num=5)
    assert u'5' == parse('%{num}').render(context)
    assert u'10' == parse('%{num * 2}').render(context)
    assert u'True' == parse('%{bool(num)}').render(context)


def test_eval_statement():
    context = Context()
    assert '' == parse('%{num = 5}').render(context)
    assert 5 == context.num


def test_context_init():
    context = Context({'foo':'bar'})
    assert 'bar' == context['foo']


def test_context_init_from_context():
    context = Context(Context({'foo':'bar'}))
    assert 'bar' == context['foo']


def test_context_update():
    context = Context({'foo':'bar'})
    context.update({'foo':'fish'})
    assert context['foo'] == 'fish'


def test_context_update_context():
    context = Context({'foo':'bar'})
    context.update(Context({'foo':'fish'}))
    assert context['foo'] == 'fish'


def test_context_keys():
    context = Context({'foo':'bar'})
    assert ['foo'] == context.keys()

def test_attrdict_init_empty():
    assert {} == AttrDict()


def test_attrdict_init_with_kwargs():
    assert {'foo':'bar'} == AttrDict(foo='bar')


def test_attrdict_init_with_dict():
    assert {'foo':'bar'} == AttrDict({'foo':'bar'})


def test_attrdict_has_key():
    assert True == AttrDict({'foo':'bar'}).has_key('foo')
    assert False == AttrDict({'foo':'bar'}).has_key('bar')


def test_attrdict_str():
    assert str({'foo':'bar'}) == str(AttrDict({'foo':'bar'}))


def test_attrdict_update_existing_dict():
    d = AttrDict({'foo':'bar'})
    d.update({'foo':'fish'})
    assert d['foo'] == 'fish'


def test_attrdict_update_new_dict():
    d = AttrDict({'foo':'bar'})
    d.update({'bar':'fish'})
    assert d['bar'] == 'fish'


def test_attrdict_update_kw():
    a = AttrDict({'foo':'bar'})
    a.update(foo='fish')
    assert a['foo'] == 'fish'


def test_attrdict_clear():
    d = AttrDict({'foo':'bar'})
    d.clear()
    assert {} == d


def test_attrdict_copy_different():
    d = AttrDict({'foo':'bar'})
    assert d.copy() is not d


def test_attrdict_copy_cls():
    assert isinstance(AttrDict().copy(), AttrDict)


def test_attrdict_get_exists():
    assert 'bar' == AttrDict({'foo':'bar'}).get('foo')


def test_attrdict_get_default():
    assert 'fish' == AttrDict({'foo':'bar'}).get('bar', 'fish')


def test_attrdict_pop():
    assert 'bar' == AttrDict({'foo':'bar'}).pop('foo')


def test_attrdict_popitem():
    assert ('foo', 'bar') == AttrDict({'foo':'bar'}).popitem()


def test_attrdict_cmp():
    assert {'foo':'baz'} != AttrDict({'foo':'bar'})


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

