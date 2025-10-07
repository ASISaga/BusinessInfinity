
import os
import sys
import subprocess

class InstallPackage:
    def run(self, dir_path):
        import time
        result = {
            'dir': dir_path,
            'exit_code': None,
            'output': ''
        }
        if not os.path.isdir(dir_path):
            result['exit_code'] = 2
            result['output'] = f"[ERROR] Directory missing: {dir_path}"
            return result
        # Prefer uv if available, else fallback to pip
        import shutil
        uv_path = shutil.which('uv')
        if uv_path:
            cmd = ['uv', 'pip', 'install', '-e', dir_path]
            print(f"[INFO] Using uv for install: {dir_path}")
        else:
            cmd = [sys.executable, '-m', 'pip', 'install', '-vvv', '-e', dir_path]
            print(f"[INFO] Using pip for install: {dir_path}")
        print(f"[INFO] Running command: {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output_lines = []
            start_time = time.time()
            timeout = 300  # 5 minutes per package
            while True:
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
                    output_lines.append(line)
                if proc.poll() is not None:
                    # Process finished
                    break
                if time.time() - start_time > timeout:
                    proc.kill()
                    output_lines.append(f"[ERROR] Timeout after {timeout} seconds for {dir_path}\n")
                    print(f"[ERROR] Timeout after {timeout} seconds for {dir_path}")
                    break
            # Read any remaining output
            for line in proc.stdout:
                print(line, end='')
                output_lines.append(line)
            result['exit_code'] = proc.returncode
            result['output'] = ''.join(output_lines)
        except Exception as e:
            result['exit_code'] = 1
            result['output'] = str(e)
        return result
