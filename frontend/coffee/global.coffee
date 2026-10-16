
# Initialize Bootstrap dropdowns
if $(".dropdown-toggle").length > 0
    $(".dropdown-toggle").dropdown()


# Upload wells
((box) ->
    link = box.querySelector('a')
    input = box.querySelector('input')
    progress = box.querySelector('.upload-progress')

    if box.dataset.file?
        input = document.getElementById(box.dataset.file)

    return unless link? and input?

    link.addEventListener('click', (e) ->
        e.preventDefault()
        input.click()
    , false)

    input.addEventListener('change', (e) ->
        return unless input.files? and input.files.length > 0

        if progress?
            progress.style.width = '0%'
            progress.classList.remove('fade-out')

        eventName = box.dataset.event

        if eventName? and typeof window[eventName] is 'function'
            window[eventName](input.files, box)
        else
            console.error('Upload handler not found:', eventName)
    , false)

    if progress?
        progress.addEventListener('animationend', ->
            progress.style.width = '0%'
            progress.classList.remove('fade-out')
        , false)

    if box.classList.contains('scrollable')
        down = false
        startX = 0
        startY = 0
        x = 0
        y = 0

        box.addEventListener('mousedown', (e) ->
            position = window.getComputedStyle(box).backgroundPosition.split(' ')
            x = parseInt(position[0], 10) or 0
            y = parseInt(position[1], 10) or 0

            startX = e.clientX
            startY = e.clientY
            down = true
        , false)

        box.addEventListener('mouseup', ->
            down = false
        , false)

        box.addEventListener('mouseleave', ->
            down = false
        , false)

        box.addEventListener('mousemove', (e) ->
            return unless down

            newX = e.clientX - startX + x
            newY = e.clientY - startY + y

            newX = 0 unless box.dataset.scrollX?
            newY = 0 unless box.dataset.scrollY?

            box.style.backgroundPosition = "#{newX}px #{newY}px"

            if box.dataset.scrollX?
                $('#' + box.dataset.scrollX).val(newX)

            if box.dataset.scrollY?
                $('#' + box.dataset.scrollY).val(newY)
        , false)

)(box) for box in document.querySelectorAll('.upload-well')


# Hide alerts instead of removing them from the DOM
$('#alert-follow').on 'close.bs.alert', ->
    $('#alert-follow').addClass('hidden')
    false

$('#alert-error').on 'close.bs.alert', ->
    $('#alert-error').addClass('hidden')
    false


# Dark mode
darkModeToggle = document.getElementById('dark-mode-toggle')

if darkModeToggle?
    root = document.documentElement

    updateDarkModeButton = ->
        active = root.classList.contains('dark-mode')
        darkModeToggle.setAttribute('aria-pressed', active.toString())

    hasExplicitChoice = ->
        try
            localStorage.getItem('dark-mode') isnt null
        catch error
            false

    applySystemTheme = (e) ->
        unless hasExplicitChoice()
            root.classList.toggle('dark-mode', e.matches)
            updateDarkModeButton()

    updateDarkModeButton()

    darkModeToggle.addEventListener('click', (e) ->
        e.preventDefault()

        active = root.classList.toggle('dark-mode')

        try
            localStorage.setItem('dark-mode', active.toString())
        catch error
            # Storage may be unavailable.

        updateDarkModeButton()
    , false)

    if window.matchMedia?
        mq = window.matchMedia('(prefers-color-scheme: dark)')

        if mq.addEventListener?
            mq.addEventListener('change', applySystemTheme)
        else if mq.addListener?
            mq.addListener(applySystemTheme)


# Search tips
$('.search-tips-button').on 'click', (e) ->
    e.preventDefault()
    $('.search-tips').addClass('search-tips-visible')

$('.search-tips').on 'click', ->
    $('.search-tips').removeClass('search-tips-visible')


# Shared AJAX helpers
showError = (reason) ->
    $('#alert-error-text').text(reason or 'An unexpected error occurred.')
    $('#alert-error').removeClass('hidden')

parseResponse = (xhr) ->
    try
        JSON.parse(xhr.responseText)
    catch error
        success: false
        reason: 'The server returned an invalid response.'

postRequest = (url, callback) ->
    xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.setRequestHeader('Accept', 'application/json')

    xhr.onload = ->
        response = parseResponse(xhr)

        if xhr.status < 200 or xhr.status >= 300
            response.success = false unless response.success is true
            response.reason or= 'Request failed (HTTP ' + xhr.status + ').'

        callback(response)

    xhr.onerror = ->
        callback(
            success: false
            reason: 'Network error. Please try again.'
        )

    xhr.send()


# Follow mods
link.addEventListener('click', (e) ->
    e.preventDefault()

    target = e.currentTarget
    mod_id = target.dataset.mod

    postRequest("/mod/#{mod_id}/follow", (response) ->
        if response.success
            $(".mod-#{mod_id}")
                .removeClass('not-following-mod')
                .addClass('following-mod')

            $('#alert-follow').removeClass('hidden')
        else
            showError(response.reason)
    )
, false) for link in document.querySelectorAll('.follow-mod-button')


# Unfollow mods
link.addEventListener('click', (e) ->
    e.preventDefault()

    target = e.currentTarget
    mod_id = target.dataset.mod

    postRequest("/mod/#{mod_id}/unfollow", (response) ->
        if response.success
            $(".mod-#{mod_id}")
                .removeClass('following-mod')
                .addClass('not-following-mod')
        else
            showError(response.reason)
    )
, false) for link in document.querySelectorAll('.unfollow-mod-button')


# Feature and unfeature mods
link.addEventListener('click', (e) ->
    e.preventDefault()

    target = e.currentTarget
    mod_id = target.dataset.mod

    isFeatured = target.classList.contains('feature-button')

    action = if isFeatured then 'feature' else 'unfeature'

    postRequest("/mod/#{mod_id}/#{action}", (response) ->
        if response.success
            if isFeatured
                target.classList.remove('feature-button')
                target.classList.add('unfeature-button')
                target.textContent = 'Unfeature this mod'
            else
                target.classList.remove('unfeature-button')
                target.classList.add('feature-button')
                target.textContent = 'Feature this mod'
        else
            showError(response.reason)
    )
, false) for link in document.querySelectorAll('.feature-button, .unfeature-button')


# Lower feature priority
link.addEventListener('click', (e) ->
    e.preventDefault()

    mod_id = e.currentTarget.dataset.mod

    postRequest("/mod/#{mod_id}/feature-down", (response) ->
        if response.success
            window.location.reload()
        else
            showError(response.reason)
    )
, false) for link in document.querySelectorAll('.lower-feature-priority-button')


# Raise feature priority
link.addEventListener('click', (e) ->
    e.preventDefault()

    mod_id = e.currentTarget.dataset.mod

    postRequest("/mod/#{mod_id}/feature-up", (response) ->
        if response.success
            window.location.reload()
        else
            showError(response.reason)
    )
, false) for link in document.querySelectorAll('.raise-feature-priority-button')


# Cookie utilities
readCookie = (name) ->
    nameEQ = name + '='

    for c in document.cookie.split(';')
        c = c.trim()

        if c.indexOf(nameEQ) is 0
            return decodeURIComponent(c.substring(nameEQ.length))

    null

window.readCookie = readCookie


createCookie = (name, value, days) ->
    expires = ''

    if days?
        date = new Date()
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000)
        expires = '; expires=' + date.toUTCString()

    cookie = encodeURIComponent(name) + '=' + encodeURIComponent(value) +
        expires + '; path=/; SameSite=Lax'

    if window.location.protocol is 'https:'
        cookie += '; Secure'

    document.cookie = cookie

window.createCookie = createCookie


# First-visit cookie
createCookie('first_visit', 'false', 365 * 10)


# Smooth scrolling
$('a[data-scroll]').on 'click', (e) ->
    e.preventDefault()

    target = e.currentTarget
    selector = target.hash

    return unless selector

    destination = $(selector)

    return unless destination.length

    $('html, body').animate(
        scrollTop: destination.offset().top - 20
    , 1500)


# Donation alert dismissal
donationAlert = document.querySelector('#alert-donate > button.close')

if donationAlert?
    donationAlert.addEventListener('click', ->
        createCookie('dismissed_donation', 'true')
    , false)
