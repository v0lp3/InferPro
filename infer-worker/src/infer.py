import json
import os.path
import subprocess


class InferReport:
    bug_type: str = None
    source_path: str = None
    bug_trace: list[dict] = None

    def __init__(self: "InferReport", vulnerability: dict, source_path: str):
        self.bug_type = vulnerability["bug_type"]
        self.qualifier = vulnerability["qualifier"]
        self.procedure_line = vulnerability["procedure_start_line"]
        self.source_path = os.path.join(source_path, vulnerability["file"])
        self.line = vulnerability["line"]
    
    def __repr__(self) -> str:
        return f"InferReport(bug={self.bug_type}, src={self.source_path}, line={self.line}, procedure_line={self.procedure_line})"


class Infer:
    @staticmethod
    def run_analyzer(
        source_path: str, source_filename: str
    ) -> list[InferReport]:

        cmd = "infer run --bufferoverrun --buck-clang --uninit --racerd --quandary --liveness --biabduction -- gcc".split(" ")

        subprocess.run(
            cmd + [source_filename],
            cwd=source_path,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        report_path = os.path.join(source_path, "infer-out", "report.json")

        if not os.path.exists(report_path):
            return None

        with open(report_path) as f:
            full_report = json.load(f)

        results = []

        for vulnerability in full_report:
            infer_report = InferReport(vulnerability, source_path)
            results.append(infer_report)

        return results
