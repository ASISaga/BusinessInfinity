

class InstallOrderResolver:
    def __init__(self):
        import os
        self.os = os
        self.WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.MANIFEST = os.path.join(self.ROOT, 'manifest.json')

    def find_modules(self, obj, parent_key=None):
        found = []
        if isinstance(obj, dict):
            if (('local' in obj or 'path' in obj) and 'manifest' in obj):
                name = obj.get('name') or parent_key or obj.get('alias')
                path = obj.get('local') or obj.get('path')
                manifest_path = obj.get('manifest')
                if name and path and manifest_path:
                    found.append({'name': name, 'path': path, 'manifest': manifest_path})
            for k, v in obj.items():
                found.extend(self.find_modules(v, parent_key=k))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(self.find_modules(item, parent_key=parent_key))
        return found

    def resolve(self):
        import json
        import tomli
        if not self.os.path.isfile(self.MANIFEST):
            raise FileNotFoundError(f"manifest.json not found at {self.MANIFEST}")
        with open(self.MANIFEST, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        modules = self.find_modules(manifest)
        name_to_path = {}
        missing_modules = []
        invalid_pyproject = []
        for mod in modules:
            name = mod.get('name')
            path = mod.get('path')
            manifest_path = mod.get('manifest')
            if name and path and manifest_path and manifest_path.endswith('pyproject.toml'):
                abs_path = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, path))
                manifest_abs = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, manifest_path))
                if not self.os.path.isdir(abs_path):
                    missing_modules.append((name, abs_path, 'missing directory'))
                    continue
                if not self.os.path.isfile(manifest_abs):
                    missing_modules.append((name, manifest_abs, 'missing pyproject.toml'))
                    continue
                try:
                    with open(manifest_abs, 'rb') as f:
                        tomli.load(f)
                except Exception as e:
                    invalid_pyproject.append((name, manifest_abs, str(e)))
                    continue
                name_to_path[name] = abs_path
        return list(name_to_path.values()), missing_modules, invalid_pyproject

    class InstallOrderResolver:
        def __init__(self):
            import os
            self.os = os
            self.WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.MANIFEST = os.path.join(self.ROOT, 'manifest.json')

        def find_modules(self, obj, parent_key=None):
            found = []
            if isinstance(obj, dict):
                if (('local' in obj or 'path' in obj) and 'manifest' in obj):
                    name = obj.get('name') or parent_key or obj.get('alias')
                    path = obj.get('local') or obj.get('path')
                    manifest_path = obj.get('manifest')
                    if name and path and manifest_path:
                        found.append({'name': name, 'path': path, 'manifest': manifest_path})
                for k, v in obj.items():
                    found.extend(self.find_modules(v, parent_key=k))
            elif isinstance(obj, list):
                for item in obj:
                    found.extend(self.find_modules(item, parent_key=parent_key))
            return found

        def resolve(self):
            import json
            import tomli
            if not self.os.path.isfile(self.MANIFEST):
                raise FileNotFoundError(f"manifest.json not found at {self.MANIFEST}")
            with open(self.MANIFEST, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            modules = self.find_modules(manifest)
            name_to_path = {}
            missing_modules = []
            invalid_pyproject = []
            for mod in modules:
                name = mod.get('name')
                path = mod.get('path')
                manifest_path = mod.get('manifest')
                if name and path and manifest_path and manifest_path.endswith('pyproject.toml'):
                    abs_path = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, path))
                    manifest_abs = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, manifest_path))
                    if not self.os.path.isdir(abs_path):
                        missing_modules.append((name, abs_path, 'missing directory'))
                        continue
                    if not self.os.path.isfile(manifest_abs):
                        missing_modules.append((name, manifest_abs, 'missing pyproject.toml'))
                        continue
                    try:
                        with open(manifest_abs, 'rb') as f:
                            tomli.load(f)
                    except Exception as e:
                        invalid_pyproject.append((name, manifest_abs, str(e)))
                        continue
                    name_to_path[name] = abs_path
            return list(name_to_path.values()), missing_modules, invalid_pyproject
            missing_modules = []
            invalid_pyproject = []
            for mod in modules:
                name = mod.get('name')
                path = mod.get('path')
                manifest_path = mod.get('manifest')
                if name and path and manifest_path and manifest_path.endswith('pyproject.toml'):
                    abs_path = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, path))
                    manifest_abs = self.os.path.normpath(self.os.path.join(self.WORKSPACE_ROOT, manifest_path))
                    if not self.os.path.isdir(abs_path):
                        missing_modules.append((name, abs_path, 'missing directory'))
                        continue
                    if not self.os.path.isfile(manifest_abs):
                        missing_modules.append((name, manifest_abs, 'missing pyproject.toml'))
                        continue
                    try:
                        with open(manifest_abs, 'rb') as f:
                            tomli.load(f)
                    except Exception as e:
                        invalid_pyproject.append((name, manifest_abs, str(e)))
                        continue
                    name_to_path[name] = abs_path
            return list(name_to_path.values()), missing_modules, invalid_pyproject
