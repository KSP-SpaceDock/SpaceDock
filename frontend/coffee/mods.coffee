if $('textarea').length
    editor = new Editor()
    editor.render()

Dropzone = require('dropzone').Dropzone

# Build URLs using the current canonical mod URL.
# These values should be provided by the page template.
modUrl = window.mod_url
modId = window.mod_id

if not modUrl
    modUrl = window.location.pathname.replace(/\/+$/, '')

modActionUrl = (action) ->
    "#{modUrl}/#{action}"

apiModUrl = (action) ->
    "/api/mod/#{modId}/#{action}"

versionDeleteUrl = (version) ->
    "#{modUrl}/version/#{version}/delete"

featureUrl = (action) ->
    "#{modUrl}/#{action}"

post = (url, callback) ->
    xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.setRequestHeader('Accept', 'application/json')
    xhr.onload = ->
        if xhr.status >= 200 and xhr.status < 300
            if callback
                callback(xhr)
        else
            alert "Request failed (#{xhr.status}): #{xhr.responseText}"
    xhr.onerror = ->
        alert 'Network error while sending request.'
    xhr.send()
    xhr

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
    url: apiModUrl('edit_version')
    headers:
        Accept: 'application/json'

    params: (files, xhr, chunk) ->
        return
            dztotalchunkcount: chunk.file.upload.totalChunkCount
            dzchunkindex: chunk.index
            'version-id': $('#version-edit-id').val()
            changelog: editor.codemirror.getValue()

    maxfilesexceeded: (file) ->
        Dropzone.forElement('#uploader').removeFile(file)

    success: (file) ->
        window.location.reload()

    error: (file, errorMessage, xhr) ->
        if errorMessage and errorMessage.reason
            alert errorMessage.reason
        else
            alert "Upload failed (#{xhr?.status or 'unknown error'})."

window.activateStats()

# Edit version
document.addEventListener 'click', (e) ->
    edit = e.target.closest('.edit-version')
    return unless edit

    e.preventDefault()

    p = edit.parentElement.parentElement
    v = edit.parentElement.dataset.version
    c = p.querySelector('.raw-changelog').innerHTML
    m = document.getElementById('version-edit-modal')

    m.querySelector('.version-id').value = v
    m.querySelector('.version-number').innerText =
        edit.parentElement.dataset.friendly_version

    editor.codemirror.setValue(c)

    dz = Dropzone.forElement('#uploader')
    dz.removeAllFiles(true)

    $(m).modal()

, false

m = $('#version-edit-modal')
if m.length
    m.on 'shown.bs.modal', (e) ->
        editor.codemirror.refresh()

# Submit version edit
document.addEventListener 'click', (e) ->
    btn = e.target.closest('#submit-version-edit')
    return unless btn

    e.preventDefault()

    dz = Dropzone.forElement('#uploader')

    if dz.getQueuedFiles().length == 0
        xhr = new XMLHttpRequest()
        xhr.open('POST', apiModUrl('edit_version'))
        xhr.setRequestHeader('Accept', 'application/json')

        xhr.onload = ->
            response = JSON.parse(xhr.responseText)

            if xhr.status < 200 or xhr.status >= 300 or response.error
                alert response.reason or "Request failed (#{xhr.status})."
            else
                window.location.reload()

        data = new FormData()
        data.append('version-id', $('#version-edit-id').val())
        data.append('changelog', editor.codemirror.getValue())
        xhr.send(data)
    else
        dz.processQueue()

, false

# Delete version
document.addEventListener 'click', (e) ->
    edit = e.target.closest('.delete-version')
    return unless edit

    e.preventDefault()

    m = document.getElementById('confirm-delete-version')
    m.querySelector('form').action =
        versionDeleteUrl(edit.dataset.version)

    $(m).modal()

, false

# Set default version
document.addEventListener 'click', (e) ->
    b = e.target.closest('.set-default-version')
    return unless b

    e.preventDefault()

    version = b.dataset.version

    post apiModUrl("set-default/#{version}"), ->
        window.location.reload()

, false

# Download registration prompt
downloadLink = document.getElementById('download-link-primary')
if downloadLink
    downloadLink.addEventListener 'click', (e) ->
        if not readCookie('do-not-offer-registration') and not window.logged_in
            setTimeout ->
                $("#register-for-updates").modal()
            , 2000
    , false

dontOffer = document.getElementById('do-not-offer-registration')
if dontOffer
    dontOffer.addEventListener 'click', (e) ->
        createCookie('do-not-offer-registration', 1, 365 * 10)
    , false

# Accept authorship invitation
accept = document.getElementById('accept-authorship-invite')
if accept
    accept.addEventListener 'click', (e) ->
        e.preventDefault()

        post apiModUrl('accept_grant'), ->
            window.location.reload()

    , false

# Reject authorship invitation
reject = document.getElementById('reject-authorship-invite')
if reject
    reject.addEventListener 'click', (e) ->
        e.preventDefault()

        post apiModUrl('reject_grant'), ->
            window.location.reload()

    , false

# Feature mod
document.addEventListener 'click', (e) ->
    b = e.target.closest('.feature-mod')
    return unless b

    e.preventDefault()

    post featureUrl('feature'), ->
        window.location.reload()

, false

# Unfeature mod
document.addEventListener 'click', (e) ->
    b = e.target.closest('.unfeature-mod')
    return unless b

    e.preventDefault()

    post featureUrl('unfeature'), ->
        window.location.reload()

, false

# Move featured mod down
document.addEventListener 'click', (e) ->
    b = e.target.closest('.feature-down')
    return unless b

    e.preventDefault()

    post featureUrl('feature-down'), ->
        window.location.reload()

, false

# Move featured mod up
document.addEventListener 'click', (e) ->
    b = e.target.closest('.feature-up')
    return unless b

    e.preventDefault()

    post featureUrl('feature-up'), ->
        window.location.reload()

, false

# Load changelog
loadChangelog = ->
    xhr = new XMLHttpRequest()
    xhr.open('GET', '/mod_changelog/' + modId)

    xhr.onload = ->
        return unless xhr.status >= 200 and xhr.status < 300

        $("#changelog").html(xhr.responseText)

    xhr.send()

# Tabs
switchTab = ->
    switch location.hash
        when '#info', ''
            $(".tab-pane.active").removeClass('active')
            $("#info").addClass('active')

        when '#changelog'
            $(".tab-pane.active").removeClass('active')
            $("#changelog").addClass('active')

            if $("#changelog").children('.timeline-entry').length == 0
                loadChangelog()

        when '#stats'
            $(".tab-pane.active").removeClass('active')
            $("#stats").addClass('active')

$("a[href^='#']").click (e) ->
    target = e.target.closest('a[href^="#"]')
    if target
        window.location.hash = target.getAttribute('href')

window.addEventListener 'hashchange', (e) ->
    switchTab()

switchTab()