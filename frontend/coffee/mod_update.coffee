editor = new mdEditor({autoDownloadFontAwesome: false})
editor.render()
dropzone = require('dropzone').Dropzone

error = (name) ->
    document.getElementById(name).parentElement.classList.add('has-error')
    document.getElementById('error-alert').classList.remove('hidden')

valid = ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')
    document.getElementById('error-alert').classList.add('hidden')

    error('version') if $("#version").val() == ''
    error('uploader') if dropzone.forElement('#uploader').files.length != 1

    return document.querySelectorAll('.has-error').length == 0

document.getElementById('submit').addEventListener('click', () ->
    return unless valid()
    dropzone.forElement('#uploader').processQueue()
, false)

dropzone.options.uploader =
    chunking: true,
    forceChunking: true,
    parallelChunkUploads: false,
    maxFiles: 1,
    maxFilesize: 10000,
    autoProcessQueue: false,
    addRemoveLinks: true,
    acceptedFiles: 'application/zip,.zip',
    paramName: 'zipball',
    url: '/api/mod/' + window.mod_id + '/update',
    headers: { 'Accept': 'application/json' },

    params: (files, xhr, chunk) ->
        return {
            'dztotalchunkcount': chunk.file.upload.totalChunkCount,
            'dzchunkindex': chunk.index,
            'game-version': $('#game-version').val(),
            'version': $('#version').val(),
            'changelog': $('#changelog').val(),
            'notify-followers': $('#notify-followers').prop('checked'),
        }

    maxfilesexceeded: (file) ->
        dropzone.forElement('#uploader').removeFile(file)

    success: (file) ->
        response = JSON.parse(file.xhr.response)
        window.location = response.url

    error: (file, errorMessage, xhr) ->
        alert = $("#error-alert")
        alert.text(errorMessage.reason)
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
