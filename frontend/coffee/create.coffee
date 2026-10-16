
editor = new Editor()
editor.render()

Dropzone = require('dropzone').Dropzone

error = (name) ->
    element = document.getElementById(name)
    return unless element?

    parent = element.parentElement
    parent.classList.add('has-error')

    document.getElementById('error-alert').classList.remove('hidden')


valid = ->
    document.querySelectorAll('.has-error').forEach (element) ->
        element.classList.remove('has-error')

    alert = document.getElementById('error-alert')
    alert.classList.add('hidden')
    alert.textContent = ''

    error('mod-name') if $.trim($("#mod-name").val() or '') == ''
    error('mod-short-description') if $.trim($("#mod-short-description").val() or '') == ''
    error('description') if $.trim(editor.codemirror.getValue()) == ''
    error('mod-license') if $("#mod-license").val() == ''
    error('mod-version') if $.trim($("#mod-version").val() or '') == ''
    error('mod-game') if $("#mod-game").val() == null
    error('mod-game-version') if $("#mod-game-version").val() == null
    error('mod-category') if $("#mod-category").val() == null or $("#mod-category").val() == ''
    error('uploader') if not Dropzone.forElement('#uploader')? or Dropzone.forElement('#uploader').files.length != 1

    return document.querySelectorAll('.has-error').length == 0


document.getElementById('submit').addEventListener 'click', (event) ->
    event.preventDefault()

    return unless valid()

    dz = Dropzone.forElement('#uploader')

    dz.processQueue()
, false


Dropzone.options.uploader =
    chunking: true
    forceChunking: true
    parallelChunkUploads: false
    maxFiles: 1
    maxFilesize: 10000
    autoProcessQueue: false
    addRemoveLinks: true
    acceptedFiles: 'application/zip,.zip'
    paramName: 'zipball'
    url: '/api/mod/create'
    headers:
        Accept: 'application/json'

    params: (files, xhr, chunk) ->
        return
            dztotalchunkcount: chunk.file.upload.totalChunkCount
            dzchunkindex: chunk.index
            name: $("#mod-name").val()
            'short-description': $("#mod-short-description").val()
            description: editor.codemirror.getValue()
            version: $("#mod-version").val()
            'game-id': $('#mod-game').val()
            'game-version': $('#mod-game-version').val()
            category: $("#mod-category").val()
            license: $("#mod-license").val()
            notifications: $('#notifications input:checked').map(->
                $(this).attr('id').replace('notif-', '')
            ).get()

    maxfilesexceeded: (file) ->
        Dropzone.forElement('#uploader').removeFile(file)

    success: (file) ->
        try
            response = JSON.parse(file.xhr.response)

            if response.url?
                window.location = response.url
            else
                throw new Error('The server did not return a redirect URL.')
        catch e
            alert = $("#error-alert")
            alert.text(e.message)
            alert.removeClass('hidden')

    error: (file, errorMessage, xhr) ->
        alert = $("#error-alert")

        if typeof errorMessage is 'string'
            message = errorMessage
        else if errorMessage?.reason?
            message = errorMessage.reason
        else if errorMessage?.error?
            message = errorMessage.error
        else
            message = 'Upload failed. Please try again.'

        alert.text(message)
        alert.removeClass('hidden')


updateCategoryNames = ->
    categoryName = $('#mod-category option:selected').text().trim()
    $('.mod-category-name').text(categoryName)


updategameversions = (gameid) ->
    select = $("#mod-game-version")

    select.empty()
    select.append(
        $('<option></option>')
            .val('')
            .text('Loading versions...')
            .prop('disabled', true)
            .prop('selected', true)
    )

    select.trigger("chosen:updated")

    $.ajax(
        method: 'GET'
        url: "/api/#{gameid}/versions"
        dataType: 'json'
        success: (msg) ->
            select.empty()

            $.each msg, (el, data) ->
                $('<option></option>')
                    .val(data.friendly_version)
                    .text(data.friendly_version)
                    .appendTo(select)

            select.trigger("chosen:updated")

        error: ->
            select.empty()
            select.append(
                $('<option></option>')
                    .val('')
                    .text('Failed to load versions')
                    .prop('disabled', true)
                    .prop('selected', true)
            )
            select.trigger("chosen:updated")
    )


updatecategories = (gameid) ->
    categorySelect = $("#mod-category")

    categorySelect.empty()
    categorySelect.append(
        $('<option></option>')
            .val('')
            .text('Loading categories...')
            .prop('disabled', true)
            .prop('selected', true)
    )

    categorySelect.trigger("chosen:updated")

    $.ajax(
        method: 'GET'
        url: "/api/#{gameid}/categories"
        dataType: 'json'
        success: (msg) ->
            categorySelect.empty()

            $.each msg, (el, category) ->
                return unless category.enabled

                $('<option></option>')
                    .val(category.id)
                    .text(category.name)
                    .attr(
                        'data-notify'
                        if category.notify then 'true' else 'false'
                    )
                    .appendTo(categorySelect)

            if categorySelect.find('option').length == 0
                categorySelect.append(
                    $('<option></option>')
                        .val('')
                        .text('No categories available')
                        .prop('disabled', true)
                        .prop('selected', true)
                )

            categorySelect.trigger("chosen:updated")
            updateCategoryNames()
            updatecategorynotifications()

        error: ->
            categorySelect.empty()
            categorySelect.append(
                $('<option></option>')
                    .val('')
                    .text('Failed to load categories')
                    .prop('disabled', true)
                    .prop('selected', true)
            )

            categorySelect.trigger("chosen:updated")
            updateCategoryNames()
            $("#notifications").addClass('hidden')
    )


updatecategorynotifications = ->
    selected = $("#mod-category option:selected")
    shouldNotify = selected.attr('data-notify') == 'true'

    if shouldNotify
        $("#notifications").removeClass('hidden')
    else
        $("#notifications").addClass('hidden')
        $('#notifications input[type="checkbox"]').prop('checked', false)


updatenotifications = (gameid) ->
    $.ajax(
        method: 'GET'
        url: "/api/#{gameid}/notifications"
        dataType: 'json'
        success: (msg) ->
            $('#notifications').empty()

            $.each msg, (el, notif) ->
                return unless notif.add_url or notif.change_url

                label = $('<label class="notification"></label>')
                checkbox = $('<input type="checkbox">')
                    .attr('id', "notif-#{notif.id}")
                    .attr('name', "notif-#{notif.name}")

                tooltip = $('<span class="glyphicon glyphicon-question-sign"></span>')
                    .attr('data-toggle', 'tooltip')
                    .attr('data-placement', 'left')
                    .attr(
                        'title',
                        'This makes it so that users can automate the installation of your mod. Your mod won\'t be added until you publish it.'
                    )

                label.append(checkbox)
                label.append(document.createTextNode("Request addition to #{notif.name}"))
                label.append(tooltip)
                label.appendTo('#notifications')

            $('[data-toggle="tooltip"]').tooltip()
            updatecategorynotifications()

        error: ->
            $('#notifications').empty()
            $("#notifications").addClass('hidden')
    )


$('[data-toggle="tooltip"]').tooltip()


$(document).ready ->
    $("#mod-game-version").chosen(
        max_selected_options: 1
        no_results_text: "No Options found"
        width: '100%'
    )

    $("#mod-game").chosen(
        max_selected_options: 1
        no_results_text: "No Options found"
        width: '100%'
    )

    $("#mod-category").chosen(
        max_selected_options: 1
        no_results_text: "No Options found"
        width: '100%'
    )

    $("#mod-license").chosen(
        max_selected_options: 1
        no_results_text: "No Options found"
        width: '100%'
    )

    preselected = $("#mod-game option:selected").val()

    if preselected?
        updategameversions(preselected)
        updatenotifications(preselected)
        updatecategories(preselected)
    else
        $("#notifications").addClass('hidden')

    $("#mod-game").change ->
        gameId = $(this).val()
        return unless gameId?

        updategameversions(gameId)
        updatenotifications(gameId)
        updatecategories(gameId)

    $("#mod-category").change ->
        updateCategoryNames()
        updatecategorynotifications()

    license = $("#mod-license option:selected").text()

    if license == "Other"
        $("#mod-other-license").removeClass("hidden").show()
    else
        $("#mod-other-license").addClass("hidden").hide()

    $("#mod-license").change (evt, params) ->
        license = if params? then params.selected else $(this).val()

        if license == "Other"
            $("#mod-other-license").removeClass("hidden").show()
        else
            $("#mod-other-license").addClass("hidden").hide()
