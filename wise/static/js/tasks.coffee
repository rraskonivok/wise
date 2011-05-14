# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

{Task} = require 'messages'

module 'tasks', (exports) ->

    # High water mark for ResultQueue, maximum number of queued
    # result callbacks
    window.ResultQueue_HWM = 5
    window.ResultQueue = []
    window.ResultCallback = {}

    # ---------------------------
    # Rule Application          |
    # -----------------------------------------------------------
    # Take a rule and a set of objects and return the           |
    # application # of the rule on the given objects. Map the   |
    # resulting set one to one onto the preimage.               |
    # -----------------------------------------------------------

    ApplyRule = (rule, operands, callback) ->

        # If nodes are not explicitely passed then use
        # the workspace's current selection
        if not operands

            if Wise.Selection.isEmpty()
                 return

            # Fetch the sexps for each of the selections and pass it
            # as a JSON array
            operands = Wise.Selection.sexps()
            _operands = Wise.Selection.toArray()

        else
            # Operands can a mix of Expression objects or literal string
            # sexp in either case we pass the sexp to the sever
            _operands = _.map operands, (obj) ->
                if (obj.constructor == String)
                    return obj
                else
                    return obj.sexp()

        task = new Task
            task     : 'rule'
            args     : rule
            operands : operands
            nsi      : NAMESPACE_INDEX


        image = []

        # The uid for this given task, used to track during all queing
        # processes
        uid = task.uid

        #if Wise.debug
        log.profile(uid)

        Wise.Socket.send(task)

        ResultQueue.push(uid)
        ResultCallback[uid] = (result) ->
            result = JSON.parse(result)
            window.result = result
            len = result.new_html.length - 1
            window.NAMESPACE_INDEX = result.namespace_index
            console.log(window.NAMESPACE_INDEX, result.namespace_index)

            for i in [0..len]
                preimage   = _operands[i]
                image_json = result.new_json[i]
                image_html = result.new_html[i]

                switch image_html
                    when 'delete' then preimage.remove()
                    when undefined then preimage.remove()
                    else
                        newnode = graft(preimage, image_json, image_html)
                        Wise.last_expr = newnode.root
                        Wise.Selection.clear()

            log.profile(uid)

    # ---------------------------
    # Evaluation                |
    # -----------------------------------------------------------
    # Take a string of Pure code and evalutes it out into       |
    # objects in the worksheet.                                 |
    # -----------------------------------------------------------

    EvalCode = (code) ->

        if Wise.Selection.isEmpty()
            $('#selectionlist').effect("highlight", { color: '#E6867A' }, 500)
            return

        if Wise.Selection.at(0).get('toplevel')
            error('Cannot rewrite toplevel element')
            Wise.Selection.at(0).errorFlash()
            return

        operands = Wise.Selection.toArray()

        task = new Task
            task     : 'eval'
            args     : code
            operands : operands
            nsi      : NAMESPACE_INDEX

        image = []

        # The uid for this given task, used to track during all queing
        # processes
        uid = task.uid

        #if Wise.debug
        log.profile(uid)

        Wise.Socket.send(task)

        ResultQueue.push(uid)
        ResultCallback[uid] = (result) ->
            result = JSON.parse(result)
            window.result = result
            console.log result

            if result.error
                Wise.CmdLine.show()
                Wise.CmdLine.setValue(code)
                Wise.CmdLine.error(result.error)
                # TODO: focus on CmdLine
                return
            else
                Wise.CmdLine.hide()
                Wise.CmdLine.hideError()

            window.result = result
            len = result.new_html.length - 1
            window.NAMESPACE_INDEX = result.namespace_index

            for i in [0..len]
                preimage   = operands[i]
                image_json = result.new_json[i]
                image_html = result.new_html[i]

                switch image_html
                    when 'delete' then preimage.remove()
                    when undefined then preimage.remove()
                    else
                        newnode = graft(preimage, image_json, image_html)
                        Wise.last_expr = newnode.root
                        Wise.Selection.clear()

            log.profile(uid)


    # ----------------
    # Result Observer
    # ----------------
    Wise.Socket.socket.on 'message', (msg) ->
        # If result is the at the top of the queue then just do
        # execute the callback and we're done
        if ResultQueue[0] == msg.uid
            # console.log 'processing task', msg.uid
            ResultQueue.pop()
            ResultCallback[msg.uid].call(null, JSON.parse(msg.result))

    ResultFlush = () ->
        window.ResultQueue = []
        window.ResultCallback = {}

    window.apply_rule = ApplyRule
    window.use_infix = EvalCode

    window.ResultFlush = ResultFlush
    window.ResultQueue = ResultQueue

    exports.ApplyRule = ApplyRule
    exports.EvalCode = EvalCode
