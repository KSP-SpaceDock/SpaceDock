#!/bin/sh
rm static/bootstrap-theme.css
ln -s styles/bootstrap-theme.css static/bootstrap-theme.css
python app.py
