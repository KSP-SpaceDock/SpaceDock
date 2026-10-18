editor = new Editor()
editor.render()

Dropzone = require('dropzone').Dropzone


# Display validation errors
error = (name, htmlMsg) ->
    element = document.getElementById(name)
    return unless element?

    element.parentElement.classList.add('has-error')

    alert = $('#error-alert')
    alert.removeClass('hidden')

    message = $('<div></div>').text(htmlMsg).html()

    if alert.text() == ''
        alert.html(message)
    else
        alert.append('<br/>').append(message)


# Validate the update form
valid = ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')

    alert = $('#error-alert')
    alert.addClass('hidden')
    alert.empty()

    error('version', 'Version is required!') if $.trim($('#version').val() or '') == ''

    dz = Dropzone.forElement('#uploader')

    error('uploader', 'No file uploaded!') if not dz? or dz.files.length != 1

    error(
        'changelog',
        "Changelog is #{editor.codemirror.getValue().length} characters, the limit is 10000!"
    ) if editor.codemirror.getValue().length > 10000

    return document.querySelectorAll('.has-error').length == 0


# Submit the update
submitButton = document.getElementById('submit')

if submitButton?
    submitButton.addEventListener 'click', (event) ->
        event.preventDefault()

        return unless valid()

        Dropzone.forElement('#uploader').processQueue()
    , false


# Upload configuration
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

    # Set this on the uploader element using Flask url_for().
    url: document.getElementById('uploader')?.dataset.url

    headers:
        Accept: 'application/json'

    params: (files, xhr, chunk) ->
        return
            dztotalchunkcount: chunk.file.upload.totalChunkCount
            dzchunkindex: chunk.index
            'game-version': $('#game-version').val()
            version: $('#version').val()
            changelog: editor.codemirror.getValue()
            'notify-followers': $('#notify-followers').prop('checked')

    maxfilesexceeded: (file) ->
        Dropzone.forElement('#uploader').removeFile(file)

    success: (file) ->
        try
            response = JSON.parse(file.xhr.response)

            if file.xhr.status < 200 or file.xhr.status >= 300
                throw new Error(response.reason or response.error or 'Update failed.')

            unless response.url?
                throw new Error('The server did not return a redirect URL.')

            window.location = response.url

        catch err
            alert = $('#error-alert')
            alert.text(err.message or 'Invalid response from server.')
            alert.removeClass('hidden')

    error: (file, errorMessage, xhr) ->
        alert = $('#error-alert')

        if typeof errorMessage is 'string'
            message = errorMessage
        else if errorMessage?.reason? and typeof errorMessage.reason is 'string'
            message = errorMessage.reason
        else if errorMessage?.error? and typeof errorMessage.error is 'string'
            message = errorMessage.error
        else
            message = 'Upload failed. HTTP status: ' + (xhr?.status or 'unknown')

        alert.text(message)
        alert.removeClass('hidden')


# Version prefix validation
latest_begins_with_lowercase_v =
    window.mod_default_version_friendly.startsWith('v')

latest_begins_with_uppercase_v =
    window.mod_default_version_friendly.startsWith('V')

version_input = $('#version')
warning_text = $('#version-warning')
ok_button = $('#version-ok')

version_input.on 'input', ->
    validate_version(false)

ok_button.on 'click', ->
    validate_version(true)


validate_version = (apply_change) ->
    value = version_input.val()

    if value.length == 0
        warning_text.addClass('hidden')
        ok_button.addClass('hidden')

    else if latest_begins_with_lowercase_v and not value.startsWith('v')
        if apply_change
            if value.startsWith('V')
                version_input.val('v' + value.substring(1))
            else
                version_input.val('v' + value)

            validate_version(false)
        else
            warning_text.text(
                "Your last version had a 'v' prefix, change this version to match?"
            )
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')

    else if latest_begins_with_uppercase_v and not value.startsWith('V')
        if apply_change
            if value.startsWith('v')
                version_input.val('V' + value.substring(1))
            else
                version_input.val('V' + value)

            validate_version(false)
        else
            warning_text.text(
                "Your last version had a 'V' prefix, change this version to match?"
            )
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')

    else if not latest_begins_with_lowercase_v and value.startsWith('v')
        if apply_change
            version_input.val(value.substring(1))
            validate_version(false)
        else
            warning_text.text(
                "Your last version didn't have a 'v' prefix, change this version to match?"
            )
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')

    else if not latest_begins_with_uppercase_v and value.startsWith('V')
        if apply_change
            version_input.val(value.substring(1))
            validate_version(false)
        else
            warning_text.text(
                "Your last version didn't have a 'V' prefix, change this version to match?"
            )
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')

    else
        warning_text.addClass('hidden')
        ok_button.addClass('hidden')