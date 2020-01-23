editor = new Editor()
editor.render()

window.upload_bg = (files, box) ->
    file = files[0]
    p = document.createElement('p')
    p.textContent = 'Uploading...'
    p.className = 'status'
    box.appendChild(p)
    box.querySelector('a').classList.add('hidden')
    progress = box.querySelector('.upload-progress')

    MediaCrush.upload(file, (media) ->
        progress.classList.add('fade-out')
        progress.style.width = '100%'
        p.textContent = 'Processing...'
        media.wait(() ->
            MediaCrush.get(media.hash, (media) ->
                p.textContent = 'Done'
                path = null
                for file in media.files
                    if file.type == 'image/png' or file.type == 'image/jpeg'
                        path = file
                if path == null
                    p.textContent = 'Please upload images only.'
                else
                    document.getElementById('background').value = path.file
                    document.getElementById('header-well').style.backgroundImage = 'url("https://mediacru.sh/' + path.file + '")'
                    setTimeout(() ->
                        box.removeChild(p)
                        box.querySelector('a').classList.remove('hidden')
                    , 3000)
            )
        )
    , (e) ->
        if e.lengthComputable
            progress.style.width = (e.loaded / e.total) * 100 + '%'
    )

pack_list = window.pack_list
new_mod = null

engine = new Bloodhound({
    name: 'mods',
    remote: '/api/typeahead/mod?query=%QUERY',
    datumTokenizer: (d) -> Bloodhound.tokenizers.whitespace(d.name),
    queryTokenizer: Bloodhound.tokenizers.whitespace
})
engine.initialize()
    .done( ->
        $("#mod-typeahead").typeahead(null, {
            displayKey: 'name',
            source: engine.ttAdapter()
        }).on("typeahead:selected typeahead:autocompleted", (e, m) ->
            new_mod = m
        )
    )

document.getElementById('add-mod-button').addEventListener('click', (e) ->
    e.preventDefault()
    if new_mod == null
        # TODO: error
        return
    pack_list.push(new_mod.id)
    container = document.createElement('div')
    container.className = 'pack-item'
    if new_mod.background != "" and new_mod.background != null
        new_mod.background = 'https://cdn.mediacru.sh' + new_mod.background
    else
        new_mod.background = '/static/background.png'
    container.style.backgroundImage = 'url(' + new_mod.background + ')'
    container.style.backgroundPosition = '0 ' + new_mod.bg_offset_y + 'px'
    container.dataset.mod = new_mod.id
    container.innerHTML = """
    <div class="well well-sm">
        <div class="pull-right">
            <button class="close down" data-mod="#{ new_mod.id }" style="font-size: 10pt; line-height: 24px; padding-left: 4px"><span class="glyphicon glyphicon-chevron-down"></span></button>
            <button class="close remove" data-mod="#{ new_mod.id }">&times;</button>
            <button class="close up" data-mod="#{ new_mod.id }" style="font-size: 10pt; line-height: 22px; padding-right: 6px"><span class="glyphicon glyphicon-chevron-up"></span></button>
        </div>
        <h3>
            <a href="#{new_mod.url}">#{new_mod.name}</a>
            #{new_mod.versions[0].friendly_version}
            <span class="badge">KSP
            #{new_mod.versions[0].ksp_version}</span>
        </h3>
        <p>#{new_mod.short_description}</p>
    </div>
    """
    container.querySelector('button.remove').addEventListener('click', remove_mod)
    document.getElementById('mods-list-box').appendChild(container)
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)
    new_mod = null
)

move_up = (e) ->
    e.preventDefault()
    d = document.querySelector('.pack-item[data-mod="' + e.target.dataset.mod + '"]')
    p = d.parentElement
    prev = d.previousElementSibling
    d.parentElement.removeChild(d)
    p.insertBefore(d, prev)
    i = pack_list.indexOf(parseInt(e.target.dataset.mod))
    pack_list.splice(i, 1)
    i -= 1
    i = 0 if i < 0
    pack_list.splice(i, 0, parseInt(e.target.dataset.mod))
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)

move_down = (e) ->
    e.preventDefault()
    d = document.querySelector('.pack-item[data-mod="' + e.target.dataset.mod + '"]')
    p = d.parentElement
    next = d.nextSibling.nextElementSibling
    d.parentElement.removeChild(d)
    p.insertBefore(d, next)
    i = pack_list.indexOf(parseInt(e.target.dataset.mod))
    pack_list.splice(i, 1)
    i += 1
    i = pack_list.length - 1 if i >= pack_list.length
    pack_list.splice(i, 0, parseInt(e.target.dataset.mod))
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)

remove_mod = (e) ->
    e.preventDefault()
    d = document.querySelector('.pack-item[data-mod="' + e.target.dataset.mod + '"]')
    d.parentElement.removeChild(d)
    pack_list.splice(pack_list.indexOf(parseInt(e.target.dataset.mod)), 1)
    document.getElementById('mods-form-input').value = JSON.stringify(pack_list)

c.addEventListener('click', remove_mod) for c in document.querySelectorAll('.pack-item .remove')
c.addEventListener('click', move_up) for c in document.querySelectorAll('.pack-item .up')
c.addEventListener('click', move_down) for c in document.querySelectorAll('.pack-item .down')
