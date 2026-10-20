const fs = require('fs');
const path = require('path');
const sass = require('node-sass');
const browserify = require('browserify');
const coffeeify = require('coffeeify');
const babelify = require('babelify');
const tildeImporter = require('node-sass-tilde-importer');
const tailwindcss = require('tailwindcss');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');

const paths = {
    input: {
        styles: 'styles',
        scripts: 'coffee'
    },
    output: {
        styles: 'build',
        scripts: 'build'
    }
};

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        let dirPath = path.join(dir, f);
        let isDirectory = fs.statSync(dirPath).isDirectory();
        isDirectory
            ? walkDir(dirPath, callback)
            : callback(path.join(dir, f));
    });
}

for (let path in paths.output) {
    if (paths.output.hasOwnProperty(path)) {
        const outputDir = paths.output[path];
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir);
            console.log(`Created "${outputDir}" directory`);
        }
    }
}

// Process Tailwind CSS
const tailwindInput = path.join(paths.input.styles, 'main.scss');
const tailwindOutput = path.join(paths.output.styles, 'tailwind.css');

sass.render({
    file: tailwindInput,
    outfile: tailwindOutput,
    importer: tildeImporter,
}, (err, result) => {
    if (err) {
        console.log(err);
    } else {
        postcss([tailwindcss, autoprefixer])
            .process(result.css, { from: tailwindInput, to: tailwindOutput })
            .then(result => {
                fs.writeFile(tailwindOutput, result.css, 'utf8', err => {
                    if (err) {
                        console.log(err);
                    } else {
                        console.log(`Processed Tailwind CSS: ${tailwindOutput}`);
                    }
                });
            })
            .catch(err => {
                console.log(err);
            });
    }
});

walkDir(paths.input.styles, inputFile => {
    if (!inputFile.endsWith('.scss'))
        return;
    const ext = path.extname(inputFile);
    const basename = path.basename(inputFile, ext);
    const outFile = path.join(paths.output.styles, `${basename}.css`);
    sass.render({
        file: inputFile,
        outfile: outFile,
        importer: tildeImporter,
    }, (err, result) => {
        if (err)
            console.log(err);
        else fs.writeFile(outFile,
            result.css,
            'utf8',
            err => {
                if (err)
                    console.log(err);
                else
                    console.log(`Rendered ${inputFile} to ${outFile}`);
            });
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
        transform: [ coffeeify, babelify ],
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
