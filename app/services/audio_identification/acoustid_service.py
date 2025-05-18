import asyncio
import httpx
import json
import logging
import os
import sys
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACOUSTID_API_URL = "https://api.acoustid.org/v2/lookup"
ACOUSTID_CLIENT_API_KEY = os.getenv("ACOUSTID_APP_API_KEY")

class AcoustIDError(Exception):
    """Custom exception for AcoustID client errors."""
    pass

class AcoustIDClient:
    """Client for interacting with fpcalc and the AcoustID API."""

    def __init__(self, api_key: str = ACOUSTID_CLIENT_API_KEY):
        if not api_key:
            raise ValueError("AcoustID Application API Key is required. Set ACOUSTID_APP_API_KEY environment variable.")
        self.api_key = api_key
        self.base_params = {"client": self.api_key, "format": "json"}
        logger.info(f"AcoustIDClient initialized with API key: {self.api_key[:3]}...{self.api_key[-3:]}")

    async def _run_fpcalc(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Runs fpcalc on the audio file to get duration and fingerprint."""
        try:
            # First check if file exists and is accessible
            if not os.path.exists(file_path):
                logger.error(f"Input file does not exist: {file_path}")
                raise AcoustIDError(f"Input file does not exist: {file_path}")
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Processing file: {file_path} (size: {file_size} bytes)")
            
            # Find fpcalc in PATH
            fpcalc_path = 'fpcalc'  # Default to just the command name
            try:
                # Try to get the full path to fpcalc
                process = await asyncio.create_subprocess_exec(
                    'which', 'fpcalc',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0 and stdout:
                    fpcalc_path = stdout.decode().strip()
                    logger.info(f"Found fpcalc at: {fpcalc_path}")
                else:
                    logger.warning("Could not determine full path to fpcalc, using default command name")
            except Exception as e:
                logger.warning(f"Error finding fpcalc path: {e}")
            
            # Debug: log file stats and environment
            logger.info(f"File permissions: {oct(os.stat(file_path).st_mode)[-3:]}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            # Use -json flag for easy parsing
            cmd = [fpcalc_path, '-json', file_path]
            logger.info(f"Executing fpcalc command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                stderr_str = stderr.decode().strip()
                logger.error(f"fpcalc failed for {file_path}. Exit code: {process.returncode}, Error: {stderr_str}")
                raise AcoustIDError(f"fpcalc error: {stderr_str}")

            stdout_str = stdout.decode().strip()
            logger.info(f"fpcalc raw output: {stdout_str[:100]}..." if len(stdout_str) > 100 else stdout_str)
            
            result = json.loads(stdout_str)
            logger.info(f"fpcalc successful for {file_path}. Duration: {result.get('duration')}, Fingerprint length: {len(result.get('fingerprint', ''))}")
            return {"duration": result.get('duration'), "fingerprint": result.get('fingerprint')}

        except FileNotFoundError:
            logger.error("fpcalc command not found. Ensure chromaprint is installed and in PATH.")
            # Add more diagnostic info
            path_env = os.environ.get('PATH', '')
            logger.error(f"Current PATH: {path_env}")
            # Try to find common install locations
            for common_path in ['/usr/bin/fpcalc', '/usr/local/bin/fpcalc', '/bin/fpcalc']:
                if os.path.exists(common_path):
                    logger.info(f"Found fpcalc at alternative location: {common_path}")
            raise AcoustIDError("fpcalc not found. Chromaprint might not be installed correctly.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse fpcalc JSON output: {stdout.decode() if 'stdout' in locals() else 'No output'}")
            raise AcoustIDError("Failed to parse fpcalc output.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while running fpcalc: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception traceback: {sys.exc_info()[2]}")
            raise AcoustIDError(f"An unexpected fpcalc error occurred: {e}")

    async def lookup_fingerprint(self, file_path: str, metadata: Optional[list[str]] = None) -> Optional[Dict[str, Any]]:
        """Gets fingerprint using fpcalc and looks it up via AcoustID API."""
        logger.info(f"Starting fingerprint lookup for file: {file_path}")
        fpcalc_result = await self._run_fpcalc(file_path)
        if not fpcalc_result or not fpcalc_result.get('duration') or not fpcalc_result.get('fingerprint'):
            logger.warning(f"Could not get fingerprint/duration for {file_path}")
            return None

        return await self.lookup_by_fingerprint(
            fpcalc_result['fingerprint'], 
            fpcalc_result['duration'],
            metadata
        )

    async def lookup_by_fingerprint(self, fingerprint: str, duration: float, metadata: Optional[list[str]] = None) -> Optional[Dict[str, Any]]:
        """Looks up a fingerprint via AcoustID API using pre-calculated fingerprint and duration."""
        logger.info(f"Starting lookup for pre-calculated fingerprint, duration: {duration}")

        params = {
            **self.base_params,
            "duration": str(int(duration)), # Duration must be an integer string
            "fingerprint": fingerprint,
        }
        if metadata:
            # e.g., ['recordings', 'releasegroups', 'compress']
            params["meta"] = '+'.join(metadata) 
            logger.info(f"Including metadata in request: {metadata}")

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Querying AcoustID API for pre-calculated fingerprint...")
                # Log request details (excluding the full fingerprint for brevity)
                debug_params = {k: (v[:20] + '...' if k == 'fingerprint' and len(v) > 20 else v) for k, v in params.items()}
                logger.info(f"Request parameters: {debug_params}")
                
                response = await client.get(ACOUSTID_API_URL, params=params, timeout=15.0)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

                logger.info(f"AcoustID API response status: {response.status_code}")
                data = response.json()
                
                if data.get("status") == "ok" and data.get("results"):
                    # Return the first result (usually the highest score)
                    best_result = max(data["results"], key=lambda x: x.get('score', 0), default=None)
                    logger.info(f"AcoustID lookup successful. Score: {best_result.get('score') if best_result else 'N/A'}")
                    
                    # Add more detailed logging about the result
                    if best_result:
                        recording_count = len(best_result.get('recordings', []))
                        logger.info(f"Found {recording_count} recordings for the fingerprint")
                        if recording_count > 0:
                            recording = best_result['recordings'][0]
                            logger.info(f"Best match: '{recording.get('title', 'Unknown')}' by '{recording.get('artists', [{}])[0].get('name', 'Unknown')}'")
                    
                    return best_result 
                else:
                    error_message = data.get("error", {}).get("message", "Unknown error")
                    logger.warning(f"AcoustID lookup failed. Status: {data.get('status')}, Error: {error_message}")
                    # Log the full response for debugging
                    logger.warning(f"Full API response: {data}")
                    return None

            except httpx.HTTPStatusError as e:
                logger.error(f"AcoustID API request failed: {e.response.status_code} - {e.response.text}")
                raise AcoustIDError(f"AcoustID API error: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"AcoustID API request error: {e}")
                raise AcoustIDError(f"AcoustID network error: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during AcoustID lookup: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(f"Exception traceback: {sys.exc_info()[2]}")
                raise AcoustIDError(f"An unexpected AcoustID lookup error: {e}")

# Create the client (only if API key is available)
acoustid_client = None
if ACOUSTID_CLIENT_API_KEY:
    try:
        acoustid_client = AcoustIDClient()
    except ValueError as e:
        logger.warning(f"Could not initialize global AcoustIDClient: {e}")

# Example Usage (for testing)
async def main():
    # Replace with a path to an actual audio file for testing
    test_file_path = "path/to/your/audiofile.mp3"  
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}. Skipping example usage.")
        return

    client = AcoustIDClient()
    try:
        # Lookup basic info + recording IDs and release groups
        result = await client.lookup_fingerprint(
            test_file_path, 
            metadata=['recordings', 'releasegroups', 'compress']
        )
        if result:
            print("\nAcoustID Lookup Result:")
            print(json.dumps(result, indent=2))
        else:
            print("\nNo result found or lookup failed.")
    except AcoustIDError as e:
        print(f"\nError during AcoustID lookup: {e}")
    except ValueError as e:
         print(f"\nConfiguration Error: {e}")


if __name__ == "__main__":
    # Check if ACOUSTID_APP_API_KEY is set
    if not ACOUSTID_CLIENT_API_KEY:
         print("Warning: ACOUSTID_APP_API_KEY environment variable not set. Using default key.")
         print("Please set the environment variable for production use.")
    # asyncio.run(main()) # Commented out to prevent accidental execution
    pass 