
class Summarizer:
    def summarize(self, results):
        failures = [r for r in results if r['exit_code'] == 1]
        not_packages = [r for r in results if r['exit_code'] == 2]
        summary_lines = []
        if results:
            summary_lines.append("Install summary for editable Python packages:\n")
            for r in results:
                status = 'SUCCESS' if r['exit_code'] == 0 else ('NOT A PACKAGE' if r['exit_code'] == 2 else 'FAILED')
                summary_lines.append(f"{r['dir']}: {status}")
            summary_lines.append("")
            if failures:
                summary_lines.append("Some installs failed. See logs for details.")
            elif not_packages:
                summary_lines.append("Some directories are not Python packages.")
            else:
                summary_lines.append("All editable Python packages installed successfully.")
        return '\n'.join(summary_lines)

    # CLI entry point removed
