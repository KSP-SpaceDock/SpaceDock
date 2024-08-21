editor = new Editor()
editor.render()

Dropzone = require('dropzone').Dropzone

error = (name, htmlMsg) ->
    document.getElementById(name).parentElement.classList.add('has-error')
    document.getElementById('error-alert').classList.remove('hidden')
    alert = $("#error-alert")
    alert.html if alert.text() == '' then alert.html().concat(htmlMsg) else alert.html().concat("<br/>").concat(htmlMsg)

valid = ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')
    document.getElementById('error-alert').classList.add('hidden')
    $("#error-alert").text('')

    error('version', 'Version is required!') if $("#version").val() == ''
    error('uploader', 'No file uploaded!') if Dropzone.forElement('#uploader').files.length != 1
    error('changelog', "Changelog is #{editor.codemirror.getValue().length} bytes, the limit is 10000!") if editor.codemirror.getValue().length > 10000

    return document.querySelectorAll('.has-error').length == 0

document.getElementById('submit').addEventListener('click', () ->
    return unless valid()
    Dropzone.forElement('#uploader').processQueue()
, false)

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
    url: '/api/mod/' + window.mod_id + '/update'
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
        response = JSON.parse(file.xhr.response)
        window.location = response.url

    error: (file, errorMessage, xhr) ->
        alert = $("#error-alert")
        alert.text(
            if typeof errorMessage is 'string'
                errorMessage
            else if errorMessage.reason? and typeof errorMessage.reason is 'string'
                errorMessage.reason
            else if errorMessage.error? and typeof errorMessage.error is 'string'
                errorMessage.error
            else
                # Give them _something_ to report to us if not in any expected format
                JSON.stringify(errorMessage)
        )
        alert.removeClass('hidden')


latest_begins_with_lowercase_v = window.mod_default_version_friendly.startsWith('v')
latest_begins_with_uppercase_v = window.mod_default_version_friendly.startsWith('V')
version_input = $('#version')
warning_text = $('#version-warning')
ok_button = $('#version-ok')

version_input.on('input', () -> validate_version(false))
ok_button.on('click', () -> validate_version(true))

validate_version = (apply_change) ->
    if version_input.val().length == 0
        warning_text.addClass('hidden')
        ok_button.addClass('hidden')
    else if latest_begins_with_lowercase_v && !version_input.val().startsWith('v')
        if version_input.val().startsWith('V')
            if apply_change
                version_input.val('v' + version_input.val().substring(1))
                # Rerun to hide the warning or discover further issues (e.g. double v prefix)
                validate_version(false)
            else
                warning_text.text('Your last version had a \'v\' prefix, change this version to match?')
                warning_text.removeClass('hidden')
                ok_button.removeClass('hidden')
        else
            if apply_change
                version_input.val('v' + version_input.val())
                validate_version(false)
            else
                warning_text.text('Your last version had a \'v\' prefix, change this version to match?')
                warning_text.removeClass('hidden')
                ok_button.removeClass('hidden')
    else if latest_begins_with_uppercase_v && !version_input.val().startsWith('V')
        if version_input.val().startsWith('v')
            if apply_change
                version_input.val('V' + version_input.val().substring(1))
                validate_version(false)
            else
                warning_text.text('Your last version had a \'V\' prefix, change this version to match?')
                warning_text.removeClass('hidden')
                ok_button.removeClass('hidden')
        else
            if apply_change
                version_input.val('V' + version_input.val())
                validate_version(false)
            else
                warning_text.text('Your last version had a \'V\' prefix, change this version to match?')
                warning_text.removeClass('hidden')
                ok_button.removeClass('hidden')
    else if !latest_begins_with_lowercase_v && version_input.val().startsWith('v')
        if apply_change
            version_input.val(version_input.val().substring(1))
            validate_version(false)
        else
            warning_text.text('Your last version didn\'t have a \'v\' prefix, change this version to match?')
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')
    else if !latest_begins_with_uppercase_v && version_input.val().startsWith('V')
        if apply_change
            version_input.val(version_input.val().substring(1))
            validate_version(false)
        else
            warning_text.text('Your last version didn\'t have a \'V\' prefix, change this version to match?')
            warning_text.removeClass('hidden')
            ok_button.removeClass('hidden')
    else
        warning_text.addClass('hidden')
        ok_button.addClass('hidden')
