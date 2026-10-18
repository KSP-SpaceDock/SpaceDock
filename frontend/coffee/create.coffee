editor = new Editor()
editor.render()

Dropzone = require('dropzone').Dropzone

error = (name) ->
    element = document.getElementById(name)
    return unless element?

    parent = element.parentElement
    parent.classList.add('has-error')

    alert = document.getElementById('error-alert')
    alert.classList.remove('hidden')


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

    dz = Dropzone.forElement('#uploader')
    error('uploader') if not dz? or dz.files.length != 1

    return document.querySelectorAll('.has-error').length == 0


# Submit the mod after validation.
submitButton = document.getElementById('submit')

if submitButton?
    submitButton.addEventListener 'click', (event) ->
        event.preventDefault()

        return unless valid()

        Dropzone.forElement('#uploader').processQueue()
    , false


# Create a mod using the configured API endpoint.
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

    select.trigger('chosen:updated')

    $.ajax(
        method: 'GET'
        url: "/api/#{encodeURIComponent(gameid)}/versions"
        dataType: 'json'
        success: (msg) ->
            select.empty()

            $.each msg, (el, data) ->
                $('<option></option