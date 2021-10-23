## Getting started

Please read the [Development Guide](https://github.com/KSP-SpaceDock/SpaceDock/wiki/Development-Guide).
If you are interested in the infrastructure and production setup of SpaceDock, see [Infrastructure](https://github.com/KSP-SpaceDock/SpaceDock/wiki/Infrastructure).


## GIT

### Setup

1) [Fork the repository on GitHub](https://guides.github.com/activities/forking/)
2) Clone your fork: `git clone https://github.com/<YourUsername>/SpaceDock.git`
3) Configure `git pull` to do fast-forward merges only: `git config --global pull.ff=only`


### Adding changes

1) First check out `alpha`: `git checkout alpha`
2) Make sure it is up-to-date: `git pull upstream alpha`
3) Create a new branch: `git checkout -b fix/<one-to-three-word-summary>`
   We tend to prefix our branch names with `fix/` for bugfixes and `feature/` for new features
4) Do your changes here with your favourite text editor or IDE.
5) Add your changes to the index: `git add <path/to/changed/file> <path/to/another/file>`
   Make sure you only add changes that you actually want to commit! `git commit -A` might include files you didn't want to.
6) Create a commit with the staged changes: `git commit -m "A small message about your commit`
7) Push the changes to your GitHub fork: `git push --set-upstream origin fix/<one-to-three-word-summary>`
8) Prepare a pull request on GitHub. If you open your fork on github.com it probably already shows you a button to do this.
   Enter a detailed summary into the PR body text box.
   Include your motivation for the feature, a way to reproduce the bug if possible, and other points that might be important or helpful for reviewers.
   Go through your diff one more time to make sure everything is included, do a "self-review".

There are more extensive guides available at https://guides.github.com/, e.g.
- https://github.com/git-guides
- https://guides.github.com/introduction/git-handbook/
- https://guides.github.com/introduction/flow/
