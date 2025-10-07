

import os
from pathlib import Path
from resolve_install_order import InstallOrderResolver
from precheck_package import PrecheckPackage
from install_package import InstallPackage
from summarize_results import Summarizer

class InstallOrchestrator:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.egg_info = self.root / 'BusinessInfinity' / 'BusinessInfinity.egg-info'
        os.makedirs(self.egg_info, exist_ok=True)
        self.resolver = InstallOrderResolver()
        self.prechecker = PrecheckPackage()
        self.installer = InstallPackage()
        self.summarizer = Summarizer()

    def run(self):
        install_order, missing, invalid = self.resolver.resolve()
        results = []
        for dir_path in install_order:
            repo_name = os.path.basename(dir_path)
            log_file = self.egg_info / f"{repo_name}.log"
            precheck = self.prechecker.run(dir_path, str(self.egg_info))
            if precheck:
                for msg in precheck:
                    print(msg)
                log_file.write_text('\n'.join(precheck))
                results.append({'dir': dir_path, 'exit_code': 2, 'output': '\n'.join(precheck)})
                continue
            install_result = self.installer.run(dir_path)
            log_file.write_text(install_result['output'])
            results.append({'dir': dir_path, 'exit_code': install_result['exit_code'], 'output': install_result['output']})
        print(self.summarizer.summarize(results))

if __name__ == "__main__":
    InstallOrchestrator().run()
