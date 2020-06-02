zipFile = null
loading = false
valid = true
get = (name) -> document.getElementById(name).value
error = (name) ->
    document.getElementById(name).parentElement.classList.add('has-error')
    document.getElementById('error-alert').classList.remove('hidden')
    valid = false

document.getElementById('submit').addEventListener('click', () ->
    a.classList.remove('has-error') for a in document.querySelectorAll('.has-error')
    document.getElementById('error-alert').classList.add('hidden')
    valid = true

    name = get('mod-name')
    shortDescription = get('mod-short-description')
    license = get('mod-license')
    if license == 'Other'
        license = get('mod-other-license')
    version = get('mod-version')
    gameVersion = get('mod-game-version')
    game = get('mod-game')
    ckan = document.getElementById("ckan").checked

    error('mod-name') if name == ''
    error('mod-short-description') if shortDescription == ''
    error('mod-license') if license == ''
    error('mod-version') if version == ''
    error('game') if game == null
    if zipFile == null
        valid = false

    return unless valid
    return if loading
    loading = true

    progress = document.getElementById('progress')
    xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/mod/create')
    xhr.upload.onprogress = (e) ->
        if e.lengthComputable
            value = (e.loaded / e.total) * 100
            progress.querySelector('.progress-bar').style.width = value + '%'
    xhr.onload = () ->
        if this.statusCode == 502
            result = { error: true, message: "This mod is too big to upload. Contact {{ support_mail }}" }
        else
            result = JSON.parse(this.responseText)
        progress.classList.remove('active')
        if not result.error?
            window.location = JSON.parse(this.responseText).url + "?new=True"
        else
            alert = document.getElementById('error-alert')
            alert.classList.remove('hidden')
            alert.textContent = result.reason
            document.getElementById('submit').removeAttribute('disabled')
            document.querySelector('.upload-mod a').classList.remove('hidden')
            document.querySelector('.upload-mod p').classList.add('hidden')
            loading = false
    form = new FormData()
    form.append('game-id', game)
    form.append('name', name)
    form.append('short-description', shortDescription)
    form.append('license', license)
    form.append('version', version)
    form.append('game-version', gameVersion)
    form.append('ckan', ckan)
    form.append('zipball', zipFile)
    document.getElementById('submit').setAttribute('disabled', 'disabled')
    progress.querySelector('.progress-bar').style.width = '0%'
    progress.classList.add('active')
    xhr.send(form)
, false)

document.getElementById('mod-license').addEventListener('change', () ->
    license = get('mod-license')
    if license == 'Other'
        document.getElementById('mod-other-license').classList.remove('hidden')
    else
        document.getElementById('mod-other-license').classList.add('hidden')
, false)

selectFile = (file) ->
    zipFile = file
    parent = document.querySelector('.upload-mod')
    parent.querySelector('a').classList.add('hidden')
    p = document.createElement('p')
    p.textContent = 'Ready.'
    parent.appendChild(p)

document.querySelector('.upload-mod a').addEventListener('click', (e) ->
    e.preventDefault()
    document.querySelector('.upload-mod input').click()
, false)

document.querySelector('.upload-mod input').addEventListener('change', (e) ->
    selectFile(e.target.files[0])
, false)

dragNop = (e) ->
    e.stopPropagation()
    e.preventDefault()

window.addEventListener('dragenter', dragNop, false)
window.addEventListener('dragleave', dragNop, false)
window.addEventListener('dragover', dragNop, false)
window.addEventListener('drop', (e) ->
    dragNop(e)
    selectFile(e.dataTransfer.files[0])
, false)

document.getElementById('submit').removeAttribute('disabled')
$('[data-toggle="tooltip"]').tooltip()


updategame = ->
    gid = $("#mod-game option:selected").attr("value")
    # TODO: don't hardcode the production game id here.
    #       Do we have a game.ckan_enabled property?
    if gid != "3102"
        # if not ksp then hide ckan checkbox
        $(".ckan").hide()
    else
        $(".ckan").show()


updategameversions = (gameid) ->
    $.ajax(
        method: "GET",
        url: "/api/" + gameid + "/versions",
        success: (msg) ->
            $("#mod-game-version option").remove()
            $.each(msg, (el, data) ->
                $('<option value="' + data.friendly_version + '">' + data.friendly_version + '</option>').appendTo("#mod-game-version")
            )
            $("#mod-game-version").trigger("chosen:updated")
    )


# Check if there's a game preselected, if yes, get the game versions for it.
preselected = $("#mod-game option:selected").attr("value")
if preselected != null
    updategame()
    updategameversions(preselected)


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
    updategame()
    updategameversions($(this).val())
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
