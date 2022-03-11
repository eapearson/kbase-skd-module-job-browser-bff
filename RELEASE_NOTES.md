# JobBrowserBFF release notes

## 1.2.0

- Update dependences; a transitive dependency (markupsafe) has a breaking change for jinja2 2.x; updating to 3.x fixes it.

## 1.1.2

- Pin markupsafe to 2.0.1 to avoid a breaking change in 2.1.0

## 1.1.1

- Revert Alpine Linux to 3.1.3 [UFI-4]

## 1.1.0

- add filter to exclude parent jobs [UFI-1]
- use virtual environment in image
- update sqlite lib `apsw`

## 1.0.0

- Initial release

## 0.0.0

- Module created by `kb-sdk` init
