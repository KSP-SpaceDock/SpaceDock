Dropzone = require('dropzone').Dropzone

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
    url: '/api/mod/' + window.mod_id + '/edit_version'
    headers:
        Accept: 'application/json'

    params: (files, xhr, chunk) ->
        return
            dztotalchunkcount: chunk.file.upload.totalChunkCount
            dzchunkindex: chunk.index
            version-id: $('#version-edit-id').val()
            changelog: $('#version-edit-changelog').val()

    maxfilesexceeded: (file) ->
        Dropzone.forElement('#uploader').removeFile(file)

    success: (file) ->
        window.location.reload()

    error: (file, errorMessage, xhr) ->
        alert errorMessage.reason

window.activateStats()

edit.addEventListener('click', (e) ->
    e.preventDefault()
    p = e.target.parentElement.parentElement
    v = e.target.parentElement.dataset.version
    c = p.querySelector('.raw-changelog').innerHTML
    m = document.getElementById('version-edit-modal')
    m.querySelector('.version-id').value = v
    m.querySelector('.version-number').innerText = e.target.parentElement.dataset.friendly_version
    m.querySelector('.changelog-text').innerHTML = c
    dz = Dropzone.forElement('#uploader')
    dz.removeAllFiles(true)
    $(m).modal()
, false) for edit in document.querySelectorAll('.edit-version')

document.getElementById('submit-version-edit').addEventListener('click', () ->
    dz = Dropzone.forElement('#uploader')
    if dz.getQueuedFiles().length == 0
        xhr = new XMLHttpRequest()
        xhr.open('POST', '/api/mod/' + window.mod_id + '/edit_version')
        xhr.setRequestHeader('Accept', 'application/json')
        xhr.onload = () ->
            response = JSON.parse(this.responseText)
            if response.error
                alert response.reason
            else
                window.location.reload()
        data = new FormData()
        data.append('version-id', $('#version-edit-id').val())
        data.append('changelog', $('#version-edit-changelog').val())
        xhr.send(data)
    else
        dz.processQueue()
, false)


edit.addEventListener('click', (e) ->
    e.preventDefault()
    m = document.getElementById('confirm-delete-version')
    m.querySelector('form').action = "/mod/#{mod_id}/version/#{e.target.dataset.version}/delete"
    $(m).modal()
, false) for edit in document.querySelectorAll('.delete-version')

b.addEventListener('click', (e) ->
    e.preventDefault()
    target = e.target
    while target.tagName != 'P'
        target = target.parentElement
    version = target.dataset.version
    mod = window.mod_id
    xhr = new XMLHttpRequest()
    xhr.open('POST', "/api/mod/#{mod}/set-default/#{version}")
    xhr.setRequestHeader('Accept', 'application/json')
    xhr.onload = () ->
        window.location = window.location
    xhr.send()
, false) for b in document.querySelectorAll('.set-default-version')

document.getElementById('download-link-primary').addEventListener('click', (e) ->
    if not readCookie('do-not-offer-registration') and not window.logged_in
        setTimeout(() ->
            $("#register-for-updates").modal()
        , 2000)
, false)

document.getElementById('do-not-offer-registration').addEventListener('click', (e) ->
    createCookie('do-not-offer-registration', 1, 365 * 10)
, false)

accept = document.getElementById('accept-authorship-invite')
if accept
    accept.addEventListener('click', (e) ->
        e.preventDefault()
        xhr = new XMLHttpRequest()
        xhr.open('POST', '/api/mod/' + mod_id + '/accept_grant')
        xhr.setRequestHeader('Accept', 'application/json')
        xhr.onload = () ->
            window.location = window.location
        xhr.send()
    , false)

reject = document.getElementById('reject-authorship-invite')
if reject
    reject.addEventListener('click', (e) ->
        e.preventDefault()
        xhr = new XMLHttpRequest()
        xhr.open('POST', '/api/mod/' + mod_id + '/reject_grant')
        xhr.setRequestHeader('Accept', 'application/json')
        xhr.onload = () ->
            window.location = window.location
        xhr.send()
    , false)

loadChangelog = () ->
    xhr = new XMLHttpRequest()
    xhr.open('GET', '/mod_changelog/' + mod_id)
    xhr.onload = () ->
        $("#changelog").html(xhr.responseText)

        edit.addEventListener('click', (e) ->
            e.preventDefault()
            p = e.target.parentElement.parentElement
            v = e.target.parentElement.dataset.version
            c = p.querySelector('.raw-changelog').innerHTML
            m = document.getElementById('version-edit-modal')
            m.querySelector('.version-id').value = v
            m.querySelector('.changelog-text').innerHTML = c
            $(m).modal()
        , false) for edit in document.querySelectorAll('.edit-version')

        edit.addEventListener('click', (e) ->
            e.preventDefault()
            m = document.getElementById('confirm-delete-version')
            m.querySelector('form').action = "/mod/#{mod_id}/version/#{e.target.dataset.version}/delete"
            $(m).modal()
        , false) for edit in document.querySelectorAll('.delete-version')

        b.addEventListener('click', (e) ->
            e.preventDefault()
            target = e.target
            while target.tagName != 'P'
                target = target.parentElement
            version = target.dataset.version
            mod = window.mod_id
            xhr = new XMLHttpRequest()
            xhr.open('POST', "/api/mod/#{mod}/set-default/#{version}")
            xhr.setRequestHeader('Accept', 'application/json')
            xhr.onload = () ->
                window.location = window.location
            xhr.send()
        , false) for b in document.querySelectorAll('.set-default-version')
    xhr.send()

switchTab = () ->
    switch location.hash
        when '#info', ''
            $(".tab-pane.active").removeClass('active')
            $("#info").addClass('active')
        when '#changelog'
            $(".tab-pane.active").removeClass('active')
            $("#changelog").addClass('active')
            if $("#changelog").children('.timeline-entry').length == 0
                loadChangelog()
        when "#stats"
            $(".tab-pane.active").removeClass('active')
            $("#stats").addClass('active')

$("a[href^='#'").click((e) -> window.location.hash = $(e.target).attr('href'))
window.addEventListener('hashchange', (e) ->switchTab())
switchTab()
