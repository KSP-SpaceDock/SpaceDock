const fs = require('fs');
const path = require('path');
const sass = require('node-sass');
const browserify = require('browserify');
const coffeeify = require('coffeeify');
const babelify = require('babelify');
const uglifyify = require('uglifyify');
const tildeImporter = require('node-sass-tilde-importer');

const paths = {
    input: {
        styles: 'styles',
        scripts: 'coffee'
    },
    output: {
        styles: 'build',
        scripts: 'build',
        fonts: 'build'
    }
};

const staticDeps = [
    [ 'node_modules/bootstrap-table/dist/bootstrap-table.min.css',paths.output.styles ],
    [ 'node_modules/chosen-js/chosen.min.css', paths.output.styles ],
    [ 'node_modules/@devhau/md-editor/dist/md-editor.min.css', paths.output.styles ],

    [ 'node_modules/jquery/dist/jquery.min.js', paths.output.scripts ],
    [ 'node_modules/bootstrap-sass/assets/javascripts/bootstrap.min.js', paths.output.scripts ],
    [ 'node_modules/bootstrap-table/dist/bootstrap-table.min.js', paths.output.scripts ],
    [ 'node_modules/bootstrap-table/dist/extensions/editable/bootstrap-table-editable.min.js', paths.output.scripts ],
    [ 'node_modules/bootstrap-table/dist/locale/bootstrap-table-en-US.min.js', paths.output.scripts ],
    [ 'node_modules/underscore/underscore-min.js', paths.output.scripts ],
    [ 'node_modules/jscroll/dist/jquery.jscroll.min.js', paths.output.scripts ],
    [ 'node_modules/chosen-js/chosen.jquery.min.js', paths.output.scripts ],
    [ 'node_modules/@devhau/md-editor/dist/md-editor.min.js', paths.output.scripts ],
    [ 'node_modules/typeahead.js/dist/typeahead.bundle.min.js', paths.output.scripts ],

    [ 'node_modules/bootstrap-sass/assets/fonts/bootstrap/glyphicons-halflings-regular.eot', paths.output.fonts ],
    [ 'node_modules/bootstrap-sass/assets/fonts/bootstrap/glyphicons-halflings-regular.svg', paths.output.fonts ],
    [ 'node_modules/bootstrap-sass/assets/fonts/bootstrap/glyphicons-halflings-regular.ttf', paths.output.fonts ],
    [ 'node_modules/bootstrap-sass/assets/fonts/bootstrap/glyphicons-halflings-regular.woff', paths.output.fonts ],
    [ 'node_modules/bootstrap-sass/assets/fonts/bootstrap/glyphicons-halflings-regular.woff2', paths.output.fonts ],
    [ 'node_modules/font-awesome/fonts/fontawesome-webfont.ttf', paths.output.fonts ],
    [ 'node_modules/font-awesome/fonts/fontawesome-webfont.woff2', paths.output.fonts ]
];

for (let path in paths.output) {
    if (paths.output.hasOwnProperty(path)) {
        const outputDir = paths.output[path];
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir);
            console.log(`Created "${outputDir}" directory`);
        }
    }
}

for (const [fromFile, toDir] of staticDeps) {
    const toFile = fs.statSync(toDir).isDirectory()
        ? path.join(toDir, path.basename(fromFile))
        : toDir;
    fs.copyFileSync(fromFile, toFile);
    console.log(`Copied ${fromFile} to ${toFile}`);
}

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        let dirPath = path.join(dir, f);
        let isDirectory = fs.statSync(dirPath).isDirectory();
        isDirectory
            ? walkDir(dirPath, callback)
            : callback(path.join(dir, f));
    });
}

walkDir(paths.input.styles, inputFile => {
    if (!inputFile.endsWith('.scss'))
        return;
    const ext = path.extname(inputFile);
    const basename = path.basename(inputFile, ext);
    const outFile = path.join(paths.output.styles, `${basename}.css`);
    sass.render({
        file: inputFile,
        outfile: outFile,
        outputStyle: 'compressed',
        importer: tildeImporter,
    }, (err, result) => {
        if (err) {
            console.log(err);
        } else {
            fs.writeFile(outFile, result.css, 'utf8', err => {
                if (err) {
                    console.log(err);
                } else {
                    console.log(`Rendered ${inputFile} to ${outFile}`);
                }
            });
        }
    });
});

walkDir(paths.input.scripts, inputFile => {
    if (!inputFile.endsWith('.coffee'))
        return;
    const ext = path.extname(inputFile);
    const basename = path.basename(inputFile, ext);
    const outFile = path.join(paths.output.scripts, `${basename}.js`);
    browserify([inputFile], {
        extensions: [ '.js', '.coffee' ],
        transform: [ coffeeify, babelify, [uglifyify, {global:true}] ],
    }).bundle((err, result) => {
        if (err) {
            console.log(err);
        } else {
            fs.writeFile(outFile, result, 'utf8', err => {
                if (err) {
                    console.log(err);
                } else {
                    console.log(`Compiled ${inputFile} to ${outFile}`);
                }
            });
        }
    });
});
