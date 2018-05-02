def parse_(code, i = 0):
    symbols = '()+-*/^, '
    word = ''
    res = []
    while i != len(code):
        if code[i] not in symbols:
            word = word + code[i]

        elif code[i] == '(':
            tmp = parse_(code, i = i + 1)
            i = tmp['index']
            c = 0
            ex = tmp['res']
            args_ = []
            for k in xrange(0, len(ex)):
                if ex[k] == ',':
                    tmp = [ex[q] for q in xrange(c, k)]
                    c = k + 1
                    args_.append(tmp)
            tmp = [ex[q] for q in xrange(c, k + 1)]
            args_.append(tmp)
            args = []
            for expr in args_:
                #print'begin',  expr
                if len(expr) == 1:
                    if type(expr[0]) == str:
                        try:
                            x = float(expr[0])
                            try:
                                x = int(expr[0])
                            except:
                                pass
                        except:
                            x = expr[0]
                        finally:    
                            expr = x
                    elif type(expr[0]) == list:
                        if len(expr[0]) == 1:
                            if type(expr[0][0]) == str:
                                try:
                                    x = float(expr[0][0])
                                    try:
                                        x = int(expr[0][0])
                                    except:
                                        pass
                                except:
                                    x = expr[0][0]
                                finally:
                                    expr = x
                            else:
                                expr = expr[0][0]
                        else:
                            expr = expr[0]
                else:
                    for j in xrange(0, len(expr), 2):
                        if type(expr[j]) == list:
                            if len(expr[j]) == 1 and type(expr[j][0]) == str:
                                try:
                                    x = float(expr[j][0])
                                    try:
                                        x = int(expr[j][0])
                                    except:
                                        pass
                                except:
                                    x = expr[j][0]
                                finally:
                                    if len(expr) == 1:
                                        expr = x
                                    else:
                                        expr[j] = x
                            elif len(expr[j]) == 1 and type(expr[j][0]) in [list, int, float]:
                                expr[j] = expr[j][0]
                #print 'end', expr
                if type(expr) == list:
                    deg = []
                    k = -1
                    if '^' in expr:
                        l = len(expr)
                        for j in xrange(1, l, 2):
                            if expr[j] == '^':
                                if k == -1:
                                    k = j
                            elif k != -1:
                                deg = expr[j - 1]
                                for q in xrange(j - 3, k - 2, -2):
                                    deg = [expr[q],'^',deg]
                                expr[k - 1] = deg
                                k = -1
                        if k != -1:
                            j += 2
                            deg = expr[j - 1]
                            for q in xrange(j - 3, k - 2, -2):
                                deg = [expr[q],'^',deg]
                            expr[k - 1] = deg

                        j = 1
                        while j < len(expr):
                            if expr[j] == '^':
                                expr.pop(j)
                                expr.pop(j)
                            else:
                                j += 2
                        if '+' not in expr and '-' not in expr and '*' not in expr and '/' not in expr:
                            expr = expr[0]
                    add = []
                    mult = []
                    if ('+' in expr or '-' in expr) and ('*' in expr or '/' in expr):
                        for j in xrange(1, len(expr), 2):
                            if expr[j] in '+-':
                                if mult == []:
                                    add.append(expr[j - 1])
                                else:
                                    add.append(mult)
                                    mult = []
                                add.append(expr[j])
                            elif expr[j] in '*/':
                                if mult == []:
                                    mult.append(expr[j - 1])
                                    mult.append(expr[j])
                                    mult.append(expr[j + 1])
                                else:
                                    mult.append(expr[j])
                                    mult.append(expr[j + 1])
                                
                        if mult == []:
                            add.append(expr[-1])
                        else:
                            add.append(mult)
                        
                        args.append(add)
                    else:
                        args.append(expr)
                else:
                    args.append(expr)
            #if word != :
            #    if len(args) == 1 and type(args[0]) == list:
            #        args = args[0]
            if word == '':
                #print 228, args
                res.append(args[0])
            else:
                res.append([word, args])
                word = ''

        elif code[i] in '+-*/^,':
            if word != '':
                res = [[word], code[i]]
            elif res != []:
                res.append(code[i])
            tmp = parse_(code, i = i + 1)
            #print tmp
            if len(tmp['res']) == 1 or type(tmp['res']) == str:
                #print tmp
                res.append(tmp['res'])
            else:
                for item in tmp['res']:
                    res.append(item)
            i = tmp['index']
            return {'res': res, 'index': i}

        elif code[i] == ')':
            if word != '':
                if res == []:
                    res = [word]
                else:
                    res.append(word)
            return {'res': res, 'index': i}

        i += 1

    if word != '':
        if res == []:
            res = [word]
        else:
            res.append(word)
    return {'res': res, 'index': i}

def parse(code):
    return parse_(code = '('+code+')')['res']