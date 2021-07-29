if $(".dropdown-toggle").length > 0
    $(".dropdown-toggle").dropdown()
((box) ->
    link = box.querySelector('a')
    input = box.querySelector('input')
    progress = box.querySelector('.upload-progress')

    if box.dataset.file?
        input = document.getElementById(box.dataset.file)

    link.addEventListener('click', (e) ->
        e.preventDefault()
        input.click()
    , false)

    input.addEventListener('change', (e) ->
        progress.style.width = 0
        progress.classList.remove('fade-out')
        eval(box.dataset.event + '(input.files, box)')
    , false)

    progress.addEventListener('animationend', (e) ->
        progress.style.width = 0
        progress.classList.remove('fade-out')
    , false)

    if box.classList.contains('scrollable')
        down = false
        startX = startY = x = y = 0
        box.addEventListener('mousedown', (e) ->
            _x = box.style.backgroundPosition.split(' ')[0]
            _y = box.style.backgroundPosition.split(' ')[1]
            x = parseInt(_x.substr(0, _x.length - 2))
            y = parseInt(_y.substr(0, _y.length - 2))
            startX = e.clientX
            startY = e.clientY
            down = true
        , false)
        box.addEventListener('mouseup', (e) ->
            down = false
        , false)
        box.addEventListener('mousemove', (e) ->
            if down
                _x = e.clientX - (startX - x)
                _y = e.clientY - (startY - y)
                if not box.dataset.scrollX?
                    _x = 0
                if not box.dataset.scrollY?
                    _y = 0
                box.style.backgroundPosition = "#{_x}px #{_y}px"
                if box.dataset.scrollX?
                    $('#' + box.dataset.scrollX).val(_x)
                if box.dataset.scrollY?
                    $('#' + box.dataset.scrollY).val(_y)
        , false)
)(box) for box in document.querySelectorAll('.upload-well')

link.addEventListener('click', (e) ->
    e.preventDefault()
    xhr = new XMLHttpRequest()
    follow = false
    mod_id = e.target.dataset.mod
    if e.target.classList.contains('follow-mod-button')
        xhr.open('POST', "/mod/#{mod_id}/follow")
        xhr.setRequestHeader('Accept', 'application/json')
        e.target.classList.remove('follow-mod-button')
        e.target.classList.remove('not-following-mod')
        if $(e.target).parents('.modbox').length > 0
            # This is the follow star in a mod box
            e.target.classList.remove('glyphicon-star-empty')
            e.target.classList.add('glyphicon-star')
            $(".modbox-#{mod_id}-following").show()
        else
            # This is the big follow button on the mod page
            e.target.text = "Unfollow"
        e.target.classList.add('unfollow-mod-button')
        e.target.classList.add('following-mod')
        e.target.title = "Unfollow"
        follow = true
    else
        xhr.open('POST', "/mod/#{mod_id}/unfollow")
        xhr.setRequestHeader('Accept', 'application/json')
        e.target.classList.remove('unfollow-mod-button')
        e.target.classList.remove('following-mod')
        if $(e.target).parents('.modbox').length > 0
            e.target.classList.remove('glyphicon-star')
            e.target.classList.add('glyphicon-star-empty')
            $(".modbox-#{mod_id}-following").hide()
        else
            e.target.text = "Follow"
        e.target.classList.add('follow-mod-button')
        e.target.classList.add('not-following-mod')
        e.target.title = "Follow"
    xhr.onload = () ->
        try
            JSON.parse(this.responseText)
            document.getElementById('alert-follow').classList.remove('hidden') if follow
        catch
            window.location.href = '/register'
    xhr.send()
, false) for link in document.querySelectorAll('.follow-mod-button, .unfollow-mod-button')

link.addEventListener('click', (e) ->
    e.preventDefault()
    xhr = new XMLHttpRequest()
    if e.target.classList.contains('feature-button')
        xhr.open('POST', "/mod/#{e.target.dataset.mod}/feature")
        xhr.setRequestHeader('Accept', 'application/json')
        e.target.classList.remove('feature-button')
        e.target.classList.add('unfeature-button')
        e.target.textContent = 'Unfeature this mod'
    else
        xhr.open('POST', "/mod/#{e.target.dataset.mod}/unfeature")
        xhr.setRequestHeader('Accept', 'application/json')
        e.target.classList.remove('unfeature-button')
        e.target.classList.add('feature-button')
        e.target.textContent = 'Feature this mod'
    xhr.send()
, false) for link in document.querySelectorAll('.feature-button, .unfeature-button')

readCookie = (name) ->
    nameEQ = name + "="
    ca = document.cookie.split(';')
    for c in ca
        while c.charAt(0) == ' '
            c = c.substring(1, c.length)
        if c.indexOf(nameEQ) == 0
            return c.substring(nameEQ.length, c.length)
    return null
window.readCookie = readCookie

createCookie = (name, value, days) ->
    if days
        date = new Date()
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
        expires = "; expires=" + date.toGMTString()
    else
        expires = "; expires=session"
    document.cookie = name + "=" + value + expires + "; path=/; SameSite=Lax; Secure=True"
window.createCookie = createCookie

createCookie('first_visit', 'false', 365 * 10)

$('a[data-scroll]').click((e) ->
    e.preventDefault()
    target = e.target
    if e.target.tagName != 'A'
        target = e.target.parentElement
    $('html, body').animate({
        scrollTop: $(target.hash).offset().top - 20
    }, 1500)
)

donation_alert = document.querySelector("#alert-donate > button.close")

if donation_alert
    donation_alert.addEventListener('click', (e) ->
        createCookie('dismissed_donation', 'true')
    , false)
