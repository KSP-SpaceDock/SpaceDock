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
    error('mod-category') if $("#mod-category").val() == null or $("#mod-category").val() == ''
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
            'category': $("#mod-category").val()
            license: $("#mod-license").val()
            notifications: $('#notifications input:checked').map((e) ->
                $(this).attr('id').replace('notif-', '')
            ).get()

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
        method: "GET"
        url: "/api/" + gameid + "/categories"
        success: (msg) ->
            categorySelect.empty()

            $.each(msg, (el, category) ->
                return unless category.enabled

                option = $('<option></option>')
                    .val(category.id)
                    .text(category.name)
                    .attr(
                        'data-notify',
                        if category.notify then 'true' else 'false'
                    )

                categorySelect.append(option)
            )

            if categorySelect.find("option").length == 0
                categorySelect.append(
                    $('<option></option>')
                        .val('')
                        .text('No categories available')
                        .prop('disabled', true)
                        .prop('selected', true)
                )

            categorySelect.trigger("chosen:updated")
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
        url: '/api/' + gameid + '/notifications'
        success: (msg) ->
            $('#notifications').empty()

            $.each(msg, (el, notif) ->
                if notif.add_url or notif.change_url
                    $('<label class="notification"><input type="checkbox" id="notif-' + notif.id + '" name="notif-' + notif.name + '" />Request addition to ' + notif.name + '<span class="glyphicon glyphicon-question-sign" data-toggle="tooltip" data-placement="left" title="This makes it so that users can automate the installation of your mod. Your mod won\'t be added until you publish it."></span></label>').appendTo('#notifications')
            )

            $('[data-toggle="tooltip"]').tooltip()
            updatecategorynotifications()
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
        game_id = $(this).val()
        return unless game_id?

        updategameversions(game_id)
        updatenotifications(game_id)
        updatecategories(game_id)

    $("#mod-category").change ->
        updatecategorynotifications()

    licsel = $("#mod-license option:selected").html()

    if licsel == "Other"
        $("#mod-other-license").removeClass("hidden").show()
    else
        $("#mod-other-license").addClass("hidden").hide()

    $("#mod-license").change (evt, par) ->
        if par? and par.selected == "Other"
            $("#mod-other-license").removeClass("hidden").show()
        else if par?
            $("#mod-other-license").addClass("hidden").hide()