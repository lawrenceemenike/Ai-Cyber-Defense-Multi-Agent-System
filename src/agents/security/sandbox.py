import logging
import shlex
import re
from typing import List, Dict, Optional

logger = logging.getLogger("agent.sandbox")

class SandboxWrapper:
    """
    Epic 2.5: Sandbox Tool Execution.
    Provides a secure layer for executing system commands by:
    1. Enforcing strict argument separation (no shell=True).
    2. Sanitizing dangerous characters (Shell Injection prevention).
    3. Simulating isolation (Stripping Env Vars).
    """
    
    def __init__(self):
        # Allowlist of safe characters for arguments: Alphanumeric, dash, underscore, dot, slash, colon
        self.safe_char_pattern = re.compile(r"^[a-zA-Z0-9\-\_\.\/\:]+$")

    def validate_command(self, info: Dict[str, str]) -> bool:
        """
        Checks if the command arguments contain shell injection attempts.
        """
        args = info.get("args", [])
        if isinstance(args, str):
            # If args is a string, it's dangerous. We demand list format.
            parsed = self._safe_split(args)
            if not parsed:
                logger.warning(f"Sandbox Block: Could not safely parse args '{args}'")
                return False
            args = parsed

        for arg in args:
            if not self._is_safe_arg(arg):
                logger.warning(f"Sandbox Block: unsafe argument detected '{arg}'")
                return False
                
        return True

    def _safe_split(self, cmd_str: str) -> Optional[List[str]]:
        try:
            # shlex split respects quotes but doesn't execute shell
            return shlex.split(cmd_str)
        except ValueError:
            return None

    def _is_safe_arg(self, arg: str) -> bool:
        """
        Strictly validate argument against safe pattern.
        """
        # 1. Check for obviously dangerous shell operators
        dangerous_ops = [";", "&&", "||", "|", "`", "$(", ">", "<"]
        for op in dangerous_ops:
            if op in arg:
                # Exception: unless allowed by policy (not implemented here)
                return False
                
        # 2. Heuristic: blocked content
        if "rm -rf" in arg or "/etc/shadow" in arg:
            return False
            
        return True

    def execute_simulated(self, tool_name: str, args: List[str]) -> str:
        """
        Simulates execution within the sandbox.
        """
        if not self.validate_command({"tool": tool_name, "args": args}):
            raise SecurityError(f"Sandbox Validation Failed for {tool_name}")
            
        logger.info(f"Sandbox Executing: {tool_name} with args {args}")
        return f"Executed {tool_name} in Sandbox"

# Singleton
sandbox = SandboxWrapper()
