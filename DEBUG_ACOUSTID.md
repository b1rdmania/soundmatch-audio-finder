# AcoustID Debugging Guide

## Issues Found

1. **Missing API Key**: The main issue was that the `ACOUSTID_APP_API_KEY` environment variable was not set in the environment, causing the client initialization to fail.

2. **Error Handling**: The code didn't gracefully handle the case when the API key was missing, resulting in HTTP 500 errors rather than providing fallback mechanisms.

3. **Dependency Injection**: The `acoustid_client` was being injected into the `/process-file` endpoint, but would raise an exception if the API key was not set.

## Solutions Implemented

1. **Graceful API Key Handling**:
   - Updated `acoustid_service.py` to conditionally initialize the global client only if the API key is available
   - Updated `dependencies.py` to properly handle missing API keys with clear error messages

2. **Fallback Mechanisms**:
   - Updated the `/process-file` endpoint to handle missing AcoustID client
   - Added fallback to ID3 tag extraction when AcoustID is not available
   - Added final fallback to using the filename to extract artist/title when all else fails

3. **Documentation**:
   - Updated the README with instructions for installing Chromaprint and setting up the AcoustID API key
   - Created example `.env` file to make it clear what environment variables are needed

## How to Set Up AcoustID

1. **Install Chromaprint**:
   - macOS: `brew install chromaprint`
   - Ubuntu/Debian: `apt-get install libchromaprint-tools`
   - Windows: Download from [AcoustID website](https://acoustid.org/chromaprint)

2. **Get an API Key**:
   - Register at [acoustid.org](https://acoustid.org/)
   - Create a new application at [acoustid.org/applications](https://acoustid.org/applications)
   - Add the API key to your `.env` file: `ACOUSTID_APP_API_KEY="your_key_here"`

3. **Verify Installation**:
   - Run `which fpcalc` to ensure Chromaprint is installed and in your PATH
   - Run the test script: `python test_acoustid.py` with the API key set

## Debugging Tips

If you're still having issues:

1. **Check API Key**: Ensure the API key is correctly set in your environment
2. **Check Chromaprint**: Ensure `fpcalc` is in your PATH and executable
3. **Test with a Known File**: Try running the fingerprinting on a known audio file
4. **Check Logs**: Look for errors in the logs that might indicate issues with the AcoustID client or the `fpcalc` command

Remember that the endpoint will now work even if AcoustID is not available, by falling back to ID3 tags or filename parsing. 