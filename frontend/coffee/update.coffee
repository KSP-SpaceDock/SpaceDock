dropzone = require('dropzone')

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
