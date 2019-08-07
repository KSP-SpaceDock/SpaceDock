window.activateStats()
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
        xhr.onload = () ->
            window.location = window.location
        xhr.send()
    , false)
