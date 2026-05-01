"""
Script executor service - wraps all existing Python scripts
Preserves all original logic without modification
"""
import subprocess
import os
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ScriptExecutor:
    """
    Executes existing PPT Master Python scripts
    Does NOT modify any script logic - only wraps execution
    """
    
    def __init__(self, scripts_base_path: str, projects_base_path: str):
        self.scripts_dir = Path(scripts_base_path)
        self.projects_dir = Path(projects_base_path)
        
        if not self.scripts_dir.exists():
            raise ValueError(f"Scripts directory not found: {scripts_base_path}")
    
    def execute(
        self,
        script_path: str,
        args: List[str],
        callback: Optional[Callable[[str], None]] = None,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a Python script and capture output
        
        Args:
            script_path: Relative path to script from scripts_dir
            args: Command line arguments
            callback: Optional callback for real-time output
            cwd: Working directory (defaults to scripts_dir)
        
        Returns:
            Dict with stdout, stderr, returncode
        """
        full_script_path = self.scripts_dir / script_path
        
        if not full_script_path.exists():
            raise FileNotFoundError(f"Script not found: {full_script_path}")
        
        command = ["python3", str(full_script_path)] + args
        working_dir = cwd or str(self.scripts_dir)
        
        logger.info(f"Executing: {' '.join(command)}")
        logger.info(f"Working directory: {working_dir}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Read stdout in real-time
            if process.stdout:
                for line in process.stdout:
                    line = line.rstrip()
                    stdout_lines.append(line)
                    if callback:
                        callback(line)
                    logger.debug(f"STDOUT: {line}")
            
            # Wait for completion and get stderr
            _, stderr = process.communicate()
            if stderr:
                stderr_lines = stderr.split('\n')
                for line in stderr_lines:
                    if line.strip():
                        logger.warning(f"STDERR: {line}")
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": '\n'.join(stdout_lines),
                "stderr": stderr,
                "command": ' '.join(command)
            }
            
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": ' '.join(command)
            }
    
    # ========== Source Document Conversion ==========
    
    def pdf_to_md(self, pdf_file: str) -> Dict[str, Any]:
        """Convert PDF to Markdown"""
        return self.execute("source_to_md/pdf_to_md.py", [pdf_file])
    
    def doc_to_md(self, doc_file: str) -> Dict[str, Any]:
        """Convert DOCX/DOC to Markdown"""
        return self.execute("source_to_md/doc_to_md.py", [doc_file])
    
    def excel_to_md(self, excel_file: str) -> Dict[str, Any]:
        """Convert Excel to Markdown"""
        return self.execute("source_to_md/excel_to_md.py", [excel_file])
    
    def ppt_to_md(self, ppt_file: str) -> Dict[str, Any]:
        """Convert PowerPoint to Markdown"""
        return self.execute("source_to_md/ppt_to_md.py", [ppt_file])
    
    def web_to_md(self, url: str) -> Dict[str, Any]:
        """Convert web page to Markdown"""
        return self.execute("source_to_md/web_to_md.py", [url])
    
    # ========== Project Management ==========
    
    def init_project(self, project_name: str, format: str = "ppt169") -> Dict[str, Any]:
        """Initialize a new project"""
        return self.execute(
            "project_manager.py",
            ["init", project_name, "--format", format]
        )
    
    def import_sources(
        self,
        project_path: str,
        sources: List[str],
        move: bool = False
    ) -> Dict[str, Any]:
        """Import source files into project"""
        args = ["import-sources", project_path] + sources
        if move:
            args.append("--move")
        return self.execute("project_manager.py", args)
    
    def validate_project(self, project_path: str) -> Dict[str, Any]:
        """Validate project structure"""
        return self.execute("project_manager.py", ["validate", project_path])
    
    # ========== Image Processing ==========
    
    def analyze_images(self, images_dir: str) -> Dict[str, Any]:
        """Analyze images in directory"""
        return self.execute("analyze_images.py", [images_dir])
    
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        image_size: str = "1K",
        output_dir: str = None
    ) -> Dict[str, Any]:
        """Generate image using AI"""
        args = [
            prompt,
            "--aspect_ratio", aspect_ratio,
            "--image_size", image_size
        ]
        if output_dir:
            args.extend(["-o", output_dir])
        return self.execute("image_gen.py", args)
    
    # ========== Quality Check ==========
    
    def check_svg_quality(self, project_path: str) -> Dict[str, Any]:
        """Run SVG quality checker"""
        return self.execute("svg_quality_checker.py", [project_path])
    
    # ========== Post-Processing Pipeline ==========
    
    def split_notes(self, project_path: str) -> Dict[str, Any]:
        """Split total.md into individual note files"""
        return self.execute("total_md_split.py", [project_path])
    
    def finalize_svg(self, project_path: str) -> Dict[str, Any]:
        """Finalize SVG files"""
        return self.execute("finalize_svg.py", [project_path])
    
    def export_pptx(
        self,
        project_path: str,
        svg_source: str = "final"
    ) -> Dict[str, Any]:
        """Export to PPTX"""
        return self.execute(
            "svg_to_pptx.py",
            [project_path, "-s", svg_source]
        )
    
    # ========== Chart Calibration (Standalone) ==========
    
    def find_chart_pages(self, project_path: str) -> List[str]:
        """Find SVG files containing charts"""
        svg_output_dir = Path(project_path) / "svg_output"
        if not svg_output_dir.exists():
            return []
        
        chart_files = []
        for svg_file in svg_output_dir.glob("*.svg"):
            with open(svg_file, 'r', encoding='utf-8') as f:
                if 'chart-plot-area' in f.read():
                    chart_files.append(str(svg_file))
        
        return chart_files
    
    def calculate_chart_positions(
        self,
        chart_type: str,
        data: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate chart element positions"""
        args = ["calc", chart_type, "--data", data]
        
        # Add type-specific arguments
        if chart_type == "bar":
            if "area" in kwargs:
                args.extend(["--area", kwargs["area"]])
            if "bar_width" in kwargs:
                args.extend(["--bar-width", str(kwargs["bar_width"])])
            if "value_range" in kwargs:
                args.extend(["--value-range", kwargs["value_range"]])
        
        elif chart_type == "line":
            if "area" in kwargs:
                args.extend(["--area", kwargs["area"]])
            if "y_range" in kwargs:
                args.extend(["--y-range", kwargs["y_range"]])
        
        elif chart_type in ["pie", "radar"]:
            if "center" in kwargs:
                args.extend(["--center", kwargs["center"]])
            if "radius" in kwargs:
                args.extend(["--radius", str(kwargs["radius"])])
            if chart_type == "pie" and "inner_radius" in kwargs:
                args.extend(["--inner-radius", str(kwargs["inner_radius"])])
        
        return self.execute("svg_position_calculator.py", args)
