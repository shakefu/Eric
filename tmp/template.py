import traceback
from pprint import pprint
from collections import deque


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


def run_tests():
    tests = {}
    for name, obj in globals().iteritems():
        if name.startswith('test_') and callable(obj):
            tests[name] = obj

    for name, test in tests.iteritems():
        try:
            test()
        except:
            print "Test %s failed." % name
            traceback.printexc()

