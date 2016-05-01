from SpaceDock.app import app
from SpaceDock.config import _cfg, _cfgi

import os
import scss
import coffeescript
from shutil import rmtree, copyfile

app.static_folder = os.path.join(os.getcwd(), "static")


def prepare():
    rmtree(app.static_folder, ignore_errors=True)
    os.makedirs(app.static_folder, exist_ok=True)
    compiler = scss.Scss(scss_opts={
        'style': 'compressed' if not app.debug else None
    }, search_paths=[
        os.path.join(os.getcwd(), 'styles')
    ])

    # Compile styles (scss)
    d = os.walk('styles')
    for f in list(d)[0][2]:
        if os.path.splitext(f)[1] == ".scss":
            with open(os.path.join('styles', f)) as r:
                output = compiler.compile(r.read())

            parts = f.rsplit('.')
            css = '.'.join(parts[:-1]) + ".css"

            with open(os.path.join(app.static_folder, css), "w") as w:
                w.write(output)
                w.flush()
        else:
            copyfile(os.path.join('styles', f), os.path.join(app.static_folder, f))

    # Compile scripts (coffeescript)
    d = os.walk('scripts')
    for f in list(d)[0][2]:
        outputpath = os.path.join(app.static_folder, os.path.basename(f))
        inputpath = os.path.join('scripts', f)

        if os.path.splitext(f)[1] == ".js":
            copyfile(inputpath, outputpath)
        elif os.path.splitext(f)[1] == ".manifest":
            with open(inputpath) as r:
                manifest = r.read().split('\n')

            javascript = ''
            for script in manifest:
                script = script.strip(' ')

                if script == '' or script.startswith('#'):
                    continue

                bare = False
                if script.startswith('bare: '):
                    bare = True
                    script = script[6:]

                with open(os.path.join('scripts', script)) as r:
                    coffee = r.read().replace("{{ support_mail }}", _cfg('support-mail'))
                    if script.endswith('.js'):
                        javascript += coffee  # straight up copy
                    else:
                        javascript += coffeescript.compile(coffee, bare=bare)
            output = '.'.join(f.rsplit('.')[:-1]) + '.js'

            # TODO: Bug the slimit guys to support python 3
            # if not app.debug:
            #    javascript = minify(javascript)

            with open(os.path.join(app.static_folder, output), "w") as w:
                w.write(javascript)
                w.flush()

    d = os.walk('images')
    for f in list(d)[0][2]:
        outputpath = os.path.join(app.static_folder, os.path.basename(f))
        inputpath = os.path.join('images', f)
        copyfile(inputpath, outputpath)


@app.before_first_request
def compile_first():
    prepare()


@app.before_request
def compile_if_debug():
    if app.debug and _cfg("debug-static-recompile").lower() in ['true', 'yes']:
        prepare()

if __name__ == '__main__':
    app.run(host=_cfg("debug-host"), port=_cfgi('debug-port'), debug=True)
