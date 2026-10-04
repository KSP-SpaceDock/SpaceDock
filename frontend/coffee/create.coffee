editor = new Editor()
editor.render()
Dropzone = require('dropzone').Dropzone

error = (name) ->
    document.getElementById(name).parentElement.classList.add('has-error')
    document.getElementById('error-alert').classList.remove('hidden')

valid = ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')
    document.getElementById('error-alert').classList.add('hidden')

    error('mod-name') if $("#mod-name").val() == ''
    error('mod-short-description') if $("#mod-short-description").val() == ''
    error('description') if editor.codemirror.getValue() == ''
    error('mod-license') if $("#mod-license").val() == ''
    error('mod-version') if $("#mod-version").val() == ''
    error('mod-game') if $("#mod-game").val() == null
    error('mod-game-version') if $("#mod-game-version").val() == null
    error('uploader') if Dropzone.forElement('#uploader').files.length != 1

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
            license: $("#mod-license").val()
            notifications: $('#notifications input:checked').map((e) -> $(this).attr('id').replace('notif-', '')).get()

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

document.getElementById('mod-license').addEventListener('change', () ->
    license = get('mod-license')
    if license == 'Other'
        document.getElementById('mod-other-license').classList.remove('hidden')
    else
        document.getElementById('mod-other-license').classList.add('hidden')
, false)

$('[data-toggle="tooltip"]').tooltip()


updategameversions = (gameid) ->
    $.ajax(
        method: "GET"
        url: "/api/" + gameid + "/versions"
        success: (msg) ->
            $("#mod-game-version option").remove()
            $.each(msg, (el, data) ->
                $('<option value="' + data.friendly_version + '">' + data.friendly_version + '</option>').appendTo("#mod-game-version")
            )
            $("#mod-game-version").trigger("chosen:updated")
    )

updatenotifications = (gameid) ->
    $.ajax(
        method: 'GET'
        url: '/api/' + gameid + '/notifications'
        success: (msg) ->
            $('#notifications').empty()
            $.each(msg, (el, notif) ->
                if notif.add_url or notif.change_url
                    $('<label class="notification"><input type="checkbox" id="notif-' + notif.id + '" name="notif-' + notif.name + '" />Request addition to ' + notif.name + '<span class="glyphicon glyphicon-question-sign" data-toggle="tooltip" data-placement="left" title="This makes it so that users can automate the installation of your mod. Your mod won\'t be added until you publish it."></span></label>').appendTo('#notifications'))
    )


$(document).ready ->
    # Check if there's a game preselected, if yes, get the game versions for it.
    preselected = $("#mod-game option:selected").attr("value")
    if preselected != null
        updategameversions(preselected)
        updatenotifications(preselected)


    $("#mod-game-version").chosen(
        max_selected_options: 1,
        no_results_text: "No Options found",
        width: '100%'
    )
    $("#mod-game").chosen(
        max_selected_options: 1, no_results_text: "No Options found",
        width: '100%'
    )
    $("#mod-license").chosen(
        max_selected_options: 1,
        no_results_text: "No Options found",
        width: '100%'
    )
    $("#mod-game").chosen({width: '100%'}).change(() ->
        game_id = $(this).val()
        updategameversions(game_id)
        updatenotifications(game_id)
    )

    licsel = $("#mod-license option:selected").html()
    if licsel == "Other"
        $("#mod-other-license").removeClass("hidden").show()
    else
        $("#mod-other-license").addClass("hidden").hide()

    $("#mod-license").chosen({width: '100%'}).change((evt, par) ->
        if par.selected == "Other"
            $("#mod-other-license").removeClass("hidden").show()
        else
            $("#mod-other-license").addClass("hidden").hide()
    )
