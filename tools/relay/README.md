## Common errors

- If you get unknown revision error (`@v0.0.0-00010101000000-000000000000: invalid version: unknown revision 000000000000`), check the package name, import path, module name again. The package name is probably not supposed to be a URL (make it a path instead), module name can be.

- Check your go version, go version in files, GO111MODULES is on or not, your directory containing go.mod file is added in go.work or not.

- If problems with gopls, check `go.work`, check gopls settings.

- If you upgrade a module's version and there are new errors, go to pkg.go.dev, see the changes made between working version and new version, see the changelog on github, and modify accordingly.

- https://stackoverflow.com/questions/57722865/go-modules-pulls-old-version-of-a-package