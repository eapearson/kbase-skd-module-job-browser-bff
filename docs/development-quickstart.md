# Development QuickStart

## Succinct Steps to Hello

### Set up working directories

Although not required, the documentation suggests and will assume that you are using a specific directory structure to contain your work.

All work will be conducted within a single directory, which we'll refer to as `project`. Within the project directory will be two directories, one for this repo and one for the KBase sdk tools.

The directory structure will eventually look like:

```text
project
  kbase-sdk-module-job-browser-bff
  kb_sdk
```

For now, just create your project directory wherever you like:

```bash
cd ~/wherever-you-like
mkdir project
cd project
```

### Fork, clone and setup this repo

#### Forking

All KBase changes to KBase repos located in the github `kbase` and `kbaseapps` organizations are handled through pull requests (PRs). This implies that you must fork any such repo into your personal (kbase-associated) account.

Many projects start life in the `kbaseIncubator` organization. This github org is designed for the beginning stages of projects and experimental projects. It's rules are a bit more lenient, and you may push commits up directly.

It is still good practice to use PRs to get your changes into this upstream repo, but since incubator projects are often iterating rapidly it is acceptable also to push commits up directly.

For instance, this repo's upstream, root location is `https://github.com/kbaseapps/kbase-sdk-module-job-browser-bff`. If developer `mmouse` wants to make changes to this repo they should first fork it to `https://github.com/mmouse/kbase-sdk-module-job-browser-bff`.

- navigate your browser to [https://github.com/kbaseapps/kbase-sdk-module-job-browser-bff](https://github.com/kbaseapps/kbase-sdk-module-job-browser-bff).
- use the fork button on the upper right hand side of the browser page to create your own personal fork

#### Cloning

SDK modules tend to operate off of a single master branch. You may have occasion to use a feature or fix branch to ensure your changes are restricted to such an effort.

- make sure you are in a terminal and in the `project` directory
- clone your fork of the repo:  
    ```bash
    git clone https://github.com/mmouse/kbase-sdk-module-job-browser-bff
    ```
    > An alterative, and the method I use for my forks, is to use an ssh url which will use an ssl certificate registered in your github account, and avoid the need to log in to github to push up commits:
    ```
    git clone ssh://git@github.com/mmouse/kbase-sdk-module-job-browser-bff
    ```
- you'll notice that there is now a directory within `projects` named `kbase-sdk-module-job-browser-bff`.
- set up the upstream url 
    - It is useful, but not necessary to also set up a connection to the upstream repo. If you are working on the repo concurrently with another developer, it is highly advisable to do this; if you are working alone, it is not necessary.
    - `cd kbase-sdk-module-job-browser-bff`
    - `git remote add upstream https://github.com/kbaseapps/kbase-sdk-module-job-browser-bff`
    - `git remote set-url --push upstream nopush`
      - This prevents accidental pushes to the upstream repo.

### Clone and build KBase's SDK

Certain, but not all, changes to the service require the `kb-sdk` tool provided by the `kb_sdk` repo.

- make sure you are in a terminal and in the `project` directory

### Build and run tests

## Modify spec

## 