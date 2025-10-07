
import os

class PrecheckPackage:
    def run(self, dir_path, egg_info_dir=None):
        errors = []
        if not os.path.isdir(dir_path):
            errors.append(f"[ERROR] Directory missing: {dir_path}")
            return errors
        pyproject = os.path.join(dir_path, 'pyproject.toml')
        if not os.path.isfile(pyproject):
            errors.append(f"[ERROR] pyproject.toml missing in {dir_path}")
        else:
            with open(pyproject, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.strip():
                errors.append(f"[ERROR] pyproject.toml is empty in {dir_path}")
            if '[project]' not in content:
                errors.append(f"[ERROR] pyproject.toml missing [project] section in {dir_path}")
            if 'name =' not in content:
                errors.append(f"[ERROR] pyproject.toml missing name field in {dir_path}")
            if 'version =' not in content:
                errors.append(f"[ERROR] pyproject.toml missing version field in {dir_path}")
        src_dir = os.path.join(dir_path, 'src')
        if not os.path.isdir(src_dir):
            errors.append(f"[ERROR] src directory missing in {dir_path}")
        # Check write permissions
        if egg_info_dir:
            try:
                testfile = os.path.join(egg_info_dir, f"testwrite-{os.path.basename(dir_path)}.txt")
                with open(testfile, 'w') as f:
                    f.write('test')
                os.remove(testfile)
            except Exception:
                errors.append(f"[ERROR] No write permission to {egg_info_dir} for {os.path.basename(dir_path)}")
        return errors

    # CLI entry point removed
