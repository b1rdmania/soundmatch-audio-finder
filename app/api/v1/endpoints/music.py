from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List, Optional
import requests
from app.core.config import settings
from app.core.logging import logger
from app.services.metadata.musicbrainz import musicbrainz_client
from app.services.metadata.jamendo import jamendo_service
from app.services.metadata.musixmatch import musixmatch_service
from app.services.recognition.shazam import zyla_shazam_client
from app.services.ai.gemini_service import gemini_service
from app.services.metadata.discogs_service import discogs_service
from app.services.metadata.wikipedia_service import wikipedia_service
from app.core.exceptions import RecognitionAPIError, AIServiceError, MusixmatchAPIError, MetadataAPIError
import tempfile
import os
import time
import asyncio
from fastapi import status
import subprocess
import aiofiles
from .dependencies import get_musixmatch_service, get_jamendo_service, get_gemini_service, get_musicbrainz_service, get_discogs_service, get_wikipedia_service, get_acoustid_client
from app.services.audio_identification.acoustid_service import AcoustIDClient, AcoustIDError
import re
from app.utils.id3_extractor import extract_id3_tags

router = APIRouter()

@router.post("/search")
async def search_and_analyze(title: str = Form(...), artist: str = Form(...)) -> Dict[str, Any]:
    """
    Search Musixmatch for a track using title and artist, analyze with Gemini,
    find similar tracks on Jamendo.
    
    Args:
        title: Song title
        artist: Artist name
        
    Returns:
        Dictionary containing search result, analysis, and similar tracks
    """
    logger.info(f"Processing search for title: '{title}', artist: '{artist}'")
    
    musixmatch_metadata: Optional[Dict] = None
    musicbrainz_data: Optional[Dict] = None
    discogs_data: Optional[Dict] = None
    wikipedia_summary: Optional[str] = None
    gemini_analysis: Optional[Dict] = None
    jamendo_tracks: List[Dict] = []

    try:
        # 1. Try searching Musixmatch using the precise matcher.track.get
        logger.info("Attempting Musixmatch search with matcher.track.get...")
        musixmatch_metadata = await musixmatch_service.get_track_metadata(title=title, artist=artist)
        logger.info(f"Musixmatch matcher.track.get succeeded for: {title} by {artist}")

    except MusixmatchAPIError as e:
        logger.warning(f"Musixmatch matcher.track.get failed: {e}. Falling back to track.search...")
        # Fallback: Try using the general track.search endpoint
        try:
            fallback_query = f"{title} {artist}"
            musixmatch_metadata = await musixmatch_service.search_track_by_query(fallback_query)
            if musixmatch_metadata:
                logger.info(f"Musixmatch fallback search succeeded for query: {fallback_query}")
                logger.info(f"Musixmatch fallback metadata received: {musixmatch_metadata}")
            else:
                # If fallback also finds nothing, raise 404 with better message
                logger.warning(f"Musixmatch fallback search also found no track for query: {fallback_query}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Track not found: '{title}' by '{artist}'. Please check spelling or try again."
                )
        except MusixmatchAPIError as fallback_e:
            # If fallback search itself fails with an API error
            logger.error(f"Musixmatch fallback search also failed: {fallback_e}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Metadata service failed during fallback search: {fallback_e}")
        except Exception as fallback_exc: # Catch any other unexpected error during fallback
            logger.exception(f"Unexpected error during Musixmatch fallback search: {fallback_exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during the metadata fallback search.")

    # Ensure metadata was found either by primary or fallback method
    if not musixmatch_metadata:
        # This case should technically be covered by the exceptions above, but as a safeguard:
        logger.error(f"Logic error: No Musixmatch metadata found after primary and fallback attempts for '{title}' '{artist}'")
        raise HTTPException(status_code=500, detail="Failed to retrieve metadata after fallback attempts.")

    # Determine best title/artist AFTER Musixmatch step
    lookup_title = musixmatch_metadata.get('title', title)
    lookup_artist = musixmatch_metadata.get('artist', artist)
    
    # --- 2. Get MusicBrainz Data (Tags, MBID) --- 
    try:
        musicbrainz_data = await musicbrainz_client.get_musicbrainz_data(title=lookup_title, artist=lookup_artist)
        if musicbrainz_data:
            logger.info(f"Successfully retrieved MusicBrainz data: {musicbrainz_data}")
        else:
            logger.info(f"No suitable MusicBrainz data found for {lookup_title} by {lookup_artist}.")
    except MetadataAPIError as e: 
        logger.error(f"Error searching MusicBrainz for data: {e}. Proceeding without it.")
        musicbrainz_data = None 
    except Exception as e: 
         logger.exception(f"Unexpected error searching MusicBrainz: {e}. Proceeding without it.")
         musicbrainz_data = None

    # --- 3. Get Discogs Data --- 
    try:
        discogs_data = await discogs_service.get_release_data(title=lookup_title, artist=lookup_artist)
        if discogs_data:
            logger.info(f"Successfully retrieved Discogs data: {discogs_data}")
        else:
            logger.info(f"No suitable Discogs data found for {lookup_title} by {lookup_artist}.")
    except MetadataAPIError as e: # Discogs client might raise this on error
        logger.error(f"Error searching Discogs for data: {e}. Proceeding without it.")
        discogs_data = None 
    except Exception as e: 
         logger.exception(f"Unexpected error searching Discogs: {e}. Proceeding without it.")
         discogs_data = None

    # --- 4. Get Wikipedia Summary --- 
    try:
        # Construct a search term - add " (song)" suffix
        wiki_search_term = f"{lookup_title} ({lookup_artist} song)" # Try adding artist context too
        # Alternative: wiki_search_term = f"{lookup_title} (song)" # Simpler, maybe better?
        wikipedia_summary = await wikipedia_service.get_wikipedia_summary(wiki_search_term)
        if wikipedia_summary:
             logger.info(f"Successfully retrieved Wikipedia summary for: {wiki_search_term}")
        else:
             logger.info(f"No Wikipedia summary found for: {wiki_search_term}. Trying title only...")
             # Fallback: Try searching just the title + (song)
             wiki_search_term_fallback = f"{lookup_title} (song)"
             wikipedia_summary = await wikipedia_service.get_wikipedia_summary(wiki_search_term_fallback)
             if wikipedia_summary:
                 logger.info(f"Successfully retrieved Wikipedia summary on fallback: {wiki_search_term_fallback}")
             else:
                 logger.info(f"No Wikipedia summary found on fallback either: {wiki_search_term_fallback}")

    except Exception as e:
         logger.exception(f"Unexpected error fetching Wikipedia summary: {e}. Proceeding without it.")
         wikipedia_summary = None

    # --- Analyze with Gemini (using only Musixmatch data) --- 
    try:
        # Combine data for Gemini analysis
        analysis_input = {**musixmatch_metadata} # Start with Musixmatch data
        if musicbrainz_data and musicbrainz_data.get("tags"):
            # Add MB tags under a specific key to avoid collision
            analysis_input["musicbrainz_tags"] = musicbrainz_data["tags"]
            logger.info("Including MusicBrainz tags in Gemini prompt.")
        else:
            logger.info("No MusicBrainz tags to include in Gemini prompt.")
        
        if discogs_data: # ADD Discogs data if available
            if discogs_data.get("styles"):
                 analysis_input["discogs_styles"] = discogs_data["styles"]
                 logger.info("Including Discogs styles in Gemini prompt.")
            if discogs_data.get("year"):
                 analysis_input["discogs_year"] = discogs_data["year"]
                 logger.info("Including Discogs year in Gemini prompt.")
        
        logger.info(f"Starting Gemini analysis with combined data: {analysis_input.get('title')}...")
        gemini_analysis = await gemini_service.analyze_song_and_generate_keywords(analysis_input)
        logger.info(f"Gemini analysis successful for {analysis_input.get('title', 'Unknown Title')} by {analysis_input.get('artist', 'Unknown Artist')}. Keywords: {gemini_analysis['keywords']}")
        keywords = gemini_analysis.get("keywords")

        if not keywords:
             logger.error("Gemini failed to generate keywords.")
             return {
                 "source_track": musixmatch_metadata, 
                 "musicbrainz_data": musicbrainz_data,
                 "discogs_data": discogs_data,
                 "wikipedia_summary": wikipedia_summary,
                 "analysis": gemini_analysis, 
                 "similar_tracks": []
             }

        # --- 5. Find similar tracks on Jamendo --- 
        logger.info(f"Original Gemini keywords: {keywords}")
        
        # Prepend Musixmatch genres to the keywords for Jamendo search priority
        jamendo_search_keywords = list(keywords) # Create a copy
        musixmatch_genres = musixmatch_metadata.get("genres", [])
        if musixmatch_genres: 
            # Add genres at the beginning of the list
            jamendo_search_keywords = musixmatch_genres + jamendo_search_keywords 
            logger.info(f"Prepending Musixmatch genres. Keywords for Jamendo: {jamendo_search_keywords}")
        else:
            logger.info("No Musixmatch genres to prepend.")
        
        # Limit the total number of keywords if it gets too long? Optional.
        # MAX_JAMENDO_KEYWORDS = 10 
        # jamendo_search_keywords = jamendo_search_keywords[:MAX_JAMENDO_KEYWORDS]
            
        logger.info(f"Searching Jamendo with keywords: {jamendo_search_keywords}")
        # jamendo_tracks = await jamendo_service.find_similar_tracks_by_keywords(keywords=keywords, limit=10) # OLD
        jamendo_tracks = await jamendo_service.find_similar_tracks_by_keywords(keywords=jamendo_search_keywords, limit=10) # NEW
        
        logger.info("Search query processing complete.")

        return {
            "source_track": musixmatch_metadata, 
            "musicbrainz_data": musicbrainz_data,
            "discogs_data": discogs_data,
            "wikipedia_summary": wikipedia_summary,
            "analysis": gemini_analysis,
            "similar_tracks": jamendo_tracks
        }

    except AIServiceError as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        # Return partial results if Gemini fails
        return {
            "source_track": musixmatch_metadata, 
            "musicbrainz_data": musicbrainz_data,
            "discogs_data": discogs_data,
            "wikipedia_summary": wikipedia_summary,
            "analysis": {"description": "AI analysis failed.", "keywords": []}, 
            "similar_tracks": []
        }
    except HTTPException as http_exc: # Re-raise HTTP exceptions from Musixmatch step
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error during analysis or Jamendo search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during AI analysis or similarity search."
        )

@router.post("/process-file")
async def process_file(
    file: UploadFile = File(...),
    musixmatch_service: MusixmatchService = Depends(get_musixmatch_service),
    jamendo_service: JamendoService = Depends(get_jamendo_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    musicbrainz_client: MusicBrainzClient = Depends(get_musicbrainz_service),
    discogs_service: DiscogsService = Depends(get_discogs_service),
    wikipedia_service: WikipediaService = Depends(get_wikipedia_service),
    acoustid_client: Optional[AcoustIDClient] = None
) -> Dict[str, Any]:
    """
    Recognize uploaded audio with AcoustID/fpcalc, enrich with Musixmatch/MusicBrainz/Discogs/Wikipedia, 
    analyze with Gemini, find similar tracks on Jamendo.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing from upload")

    logger.info(f"Processing uploaded file: {file.filename}")

    # --- Check if AcoustID client is available ---
    acoustid_available = True
    if acoustid_client is None:
        try:
            # Try to get AcoustID client (this may raise an exception if API key is not set)
            from app.api.v1.endpoints.dependencies import get_acoustid_client
            acoustid_client = get_acoustid_client()
        except ValueError as e:
            logger.warning(f"AcoustID client not available: {e}")
            acoustid_available = False
        except Exception as e:
            logger.error(f"Error initializing AcoustID client: {e}")
            acoustid_available = False

    # --- Save uploaded file temporarily for fpcalc --- 
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1] or '.tmp') as tmp_file:
        try:
            async with aiofiles.open(tmp_file.name, 'wb') as f:
                content = await file.read()
                await f.write(content)
            tmp_file_path = tmp_file.name
            logger.info(f"Saved uploaded file temporarily to: {tmp_file_path}")

            # --- 1. Recognize with AcoustID (if available) --- 
            acoustid_result: Optional[Dict] = None
            recognized_track: Optional[Dict] = None # This will hold the mapped result
            
            if acoustid_available:
                try:
                    logger.info(f"Starting AcoustID recognition for {tmp_file_path}...")
                    # Request recordings and release groups for metadata
                    acoustid_result = await acoustid_client.lookup_fingerprint(
                        tmp_file_path, 
                        metadata=['recordings', 'releasegroups', 'compress']
                    )
                    logger.info(f"AcoustID lookup result: {acoustid_result}")

                    if acoustid_result and acoustid_result.get('score', 0) > 0.5:
                        logger.info(f"AcoustID recognized track with score: {acoustid_result['score']}")
                        
                        if acoustid_result.get('recordings'):
                            recording = acoustid_result['recordings'][0]
                            logger.info(f"Recording details: {recording}")
                            recognized_track = {
                                "title": recording.get('title'),
                                "subtitle": recording.get('artists', [{}])[0].get('name'),
                                "acoustid_id": acoustid_result.get('id'),
                                "mbid": recording.get('id'),
                                "score": acoustid_result.get('score')
                            }
                            logger.info(f"Mapped AcoustID result: {recognized_track}")
                        else:
                            logger.warning("AcoustID result found, but no recording metadata available.")
                            logger.warning(f"Available keys in result: {acoustid_result.keys()}")
                            
                            # Create a recognized track with just the AcoustID ID
                            if acoustid_result.get('id'):
                                recognized_track = {
                                    "title": f"Unknown Track (AcoustID: {acoustid_result.get('id')[:8]}...)",
                                    "subtitle": "Unknown Artist",
                                    "acoustid_id": acoustid_result.get('id'),
                                    "score": acoustid_result.get('score')
                                }
                                logger.info(f"Created fallback recognized track: {recognized_track}")
                            else:
                                recognized_track = None
                                logger.warning("No usable data in AcoustID result")
                    else:
                        logger.warning(f"AcoustID did not recognize the track or score too low ({acoustid_result.get('score') if acoustid_result else 'N/A'}).")
                        recognized_track = None

                    logger.info(f"Final recognized_track: {recognized_track}")
                    
                except AcoustIDError as e:
                    logger.error(f"AcoustID error: {e}")
                    # Continue without AcoustID identification
                    acoustid_available = False
                except Exception as e:
                    logger.error(f"Unexpected error during AcoustID processing: {e}", exc_info=True)
                    # Continue without AcoustID identification
                    acoustid_available = False
            else:
                logger.warning("AcoustID client not available, skipping audio identification")
                
            # --- Try ID3 tags fallback if AcoustID failed or is not available ---
            if not recognized_track:
                try:
                    logger.info("Attempting to extract ID3 tags from the uploaded file...")
                    title, artist, additional_metadata = extract_id3_tags(tmp_file_path)
                    
                    if title and artist:
                        recognized_track = {
                            "title": title,
                            "subtitle": artist,
                            "source": "ID3 Tags",
                            "score": 1.0,  # High confidence since it's from the file's own metadata
                            "additional_metadata": additional_metadata
                        }
                        logger.info(f"Found track info from ID3 tags: {recognized_track}")
                except Exception as e:
                    logger.error(f"Error extracting ID3 tags: {e}")
                            
            # --- Final fallback: use filename as track info ---
            if not recognized_track:
                # Extract title from filename as last resort
                filename_no_ext = os.path.splitext(file.filename)[0]
                # Try to split by common delimiters
                parts = re.split(r' - |\s*-\s*|\s*by\s*|\s*\|\s*', filename_no_ext, 1)
                
                if len(parts) > 1:
                    # Assume format is "Artist - Title" or "Title - Artist"
                    # Heuristic: longer part is more likely to be title
                    if len(parts[0]) > len(parts[1]):
                        title, artist = parts[0], parts[1]
                    else:
                        artist, title = parts[0], parts[1]
                else:
                    title = filename_no_ext
                    artist = "Unknown Artist"
                    
                recognized_track = {
                    "title": title,
                    "subtitle": artist,
                    "source": "Filename",
                    "score": 0.1  # Low confidence
                }
                logger.info(f"Using filename as fallback for track info: {recognized_track}")
            
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error processing uploaded file: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                logger.info(f"Cleaned up temporary file: {tmp_file_path}")

    # --- Metadata Fetching (Musixmatch, MusicBrainz, Discogs, Wikipedia) --- 
    # Use recognized title/artist for lookups
    lookup_title = recognized_track.get('title')
    lookup_artist = recognized_track.get('subtitle') # Artist mapped to subtitle
    mbid_from_acoustid = recognized_track.get('mbid')

    musixmatch_metadata: Optional[Dict] = None
    musicbrainz_data: Optional[Dict] = None
    discogs_data: Optional[Dict] = None
    wikipedia_summary: Optional[str] = None

    # 2. Enrich with Musixmatch (using recognized title/artist)
    if lookup_title and lookup_artist:
        try:
            logger.info(f"Fetching Musixmatch metadata for: {lookup_title} by {lookup_artist}")
            musixmatch_metadata = await musixmatch_service.get_track_metadata(title=lookup_title, artist=lookup_artist)
            if musixmatch_metadata:
                logger.info(f"Found Musixmatch metadata: {musixmatch_metadata}")
            else:
                logger.info("No additional metadata found on Musixmatch.")
        except MusixmatchAPIError as e:
            logger.warning(f"Musixmatch API error, proceeding without enrichment: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Musixmatch fetch: {e}", exc_info=True)

    # 3. Get MusicBrainz Data (Prioritize MBID from AcoustID if available)
    # TODO: Refactor MusicBrainz client to allow lookup by MBID directly?
    # For now, stick to title/artist lookup, but log if we had an MBID.
    if mbid_from_acoustid:
        logger.info(f"AcoustID provided MBID: {mbid_from_acoustid}. Using title/artist for MusicBrainz lookup for now.")
        # Potential future enhancement: lookup by MBID directly
    
    if lookup_title and lookup_artist:
        try:
            musicbrainz_data = await musicbrainz_client.get_musicbrainz_data(title=lookup_title, artist=lookup_artist)
            if musicbrainz_data:
                logger.info(f"Successfully retrieved MusicBrainz data for {lookup_title}")
            else:
                logger.info(f"No suitable MusicBrainz data found via title/artist lookup for {lookup_title}.")
        except Exception as e:
             logger.exception(f"Unexpected error searching MusicBrainz: {e}. Proceeding without it.")
             musicbrainz_data = None
    else:
         logger.warning("Insufficient title/artist info from AcoustID to search MusicBrainz.")
         musicbrainz_data = None
         
    # 4. Get Discogs Data 
    # Use best available title/artist (Musixmatch if found, else AcoustID)
    final_lookup_title = musixmatch_metadata.get('title') if musixmatch_metadata else lookup_title
    final_lookup_artist = musixmatch_metadata.get('artist') if musixmatch_metadata else lookup_artist
    if final_lookup_title and final_lookup_artist:
        try:
            logger.info(f"Searching Discogs for: {final_lookup_title} by {final_lookup_artist}")
            discogs_data = await discogs_service.get_release_data(title=final_lookup_title, artist=final_lookup_artist)
            if discogs_data:
                logger.info(f"Successfully retrieved Discogs data: {discogs_data}")
            else:
                logger.info(f"No suitable Discogs data found for {final_lookup_title} by {final_lookup_artist}.")
        except MetadataAPIError as e: 
            logger.error(f"Error searching Discogs for data: {e}. Proceeding without it.")
            discogs_data = None
        except Exception as e: 
            logger.exception(f"Unexpected error searching Discogs: {e}. Proceeding without it.")
            discogs_data = None
    else:
        logger.warning("Insufficient title/artist to search Discogs.")

    # 5. Get Wikipedia Summary
    if final_lookup_title and final_lookup_artist:
        try:
            wiki_search_term = f"{final_lookup_title} ({final_lookup_artist} song)"
            wikipedia_summary = await wikipedia_service.get_wikipedia_summary(wiki_search_term)
            if wikipedia_summary:
                 logger.info(f"Successfully retrieved Wikipedia summary for: {wiki_search_term}")
            else:
                 logger.info(f"No Wikipedia summary found for: {wiki_search_term}. Trying title only...")
                 wiki_search_term_fallback = f"{final_lookup_title} (song)"
                 wikipedia_summary = await wikipedia_service.get_wikipedia_summary(wiki_search_term_fallback)
                 if wikipedia_summary:
                     logger.info(f"Successfully retrieved Wikipedia summary on fallback: {wiki_search_term_fallback}")
                 else:
                     logger.info(f"No Wikipedia summary found on fallback either: {wiki_search_term_fallback}")
        except Exception as e:
             logger.exception(f"Unexpected error fetching Wikipedia summary: {e}. Proceeding without it.")
             wikipedia_summary = None
    else:
        logger.warning("Insufficient title/artist to search Wikipedia.")

    # --- Analyze with Gemini --- 
    gemini_analysis: Optional[Dict] = None
    jamendo_tracks: List[Dict] = []
    try:
        # Combine data for Gemini analysis
        # Prioritize Musixmatch data if available, otherwise use recognized data
        analysis_input = musixmatch_metadata if musixmatch_metadata else recognized_track
        if not analysis_input:
            logger.error("No data available for Gemini analysis after AcoustID and Musixmatch.")
            raise HTTPException(status_code=500, detail="Failed to gather base data for analysis.")

        # Ensure essential keys exist if using recognized_track directly
        if analysis_input is recognized_track: # If Musixmatch failed, map recognized fields
            analysis_input = { 
                "title": recognized_track.get("title"),
                "artist": recognized_track.get("subtitle"), # Artist from subtitle
                # Add other relevant fields? MBID? Score? Tags?
            }
            logger.info("Using AcoustID-recognized data as base for Gemini.")

        # Add MusicBrainz tags if available
        if musicbrainz_data and musicbrainz_data.get("tags"):
            analysis_input["musicbrainz_tags"] = musicbrainz_data["tags"]
            logger.info("Including MusicBrainz tags in Gemini prompt.")
        
        # Add Discogs data if available
        if discogs_data:
            if discogs_data.get("styles"):
                 analysis_input["discogs_styles"] = discogs_data["styles"]
                 logger.info("Including Discogs styles in Gemini prompt.")
            if discogs_data.get("year"):
                 analysis_input["discogs_year"] = discogs_data["year"]
                 logger.info("Including Discogs year in Gemini prompt.")
        
        logger.info(f"Starting Gemini analysis with combined data: {analysis_input.get('title')}...")
        gemini_analysis = await gemini_service.analyze_song_and_generate_keywords(analysis_input)
        logger.info(f"Gemini analysis successful. Keywords: {gemini_analysis['keywords']}")
        keywords = gemini_analysis.get("keywords")

        if not keywords:
             logger.error("Gemini failed to generate keywords.")
             # Return partial results even if keywords fail
             return {
                 "recognized_track": recognized_track, # Return AcoustID result here
                 "source_track": musixmatch_metadata, 
                 "musicbrainz_data": musicbrainz_data,
                 "discogs_data": discogs_data,
                 "wikipedia_summary": wikipedia_summary,
                 "analysis": gemini_analysis, # Will contain description but empty keywords
                 "similar_tracks": []
             }

        # --- 6. Find similar tracks on Jamendo --- 
        jamendo_search_keywords = list(keywords)
        musixmatch_genres = musixmatch_metadata.get("genres", []) if musixmatch_metadata else []
        if musixmatch_genres:
            jamendo_search_keywords = musixmatch_genres + jamendo_search_keywords
            logger.info(f"Prepending Musixmatch genres. Keywords for Jamendo: {jamendo_search_keywords}")
        
        logger.info(f"Searching Jamendo with keywords: {jamendo_search_keywords}")
        jamendo_tracks = await jamendo_service.find_similar_tracks_by_keywords(keywords=jamendo_search_keywords, limit=10)
        
        logger.info("File processing complete.")

        # --- Final Response --- 
        return {
            "recognized_track": recognized_track, # Result from AcoustID
            "source_track": musixmatch_metadata, # Result from Musixmatch (enrichment)
            "musicbrainz_data": musicbrainz_data,
            "discogs_data": discogs_data,
            "wikipedia_summary": wikipedia_summary,
            "analysis": gemini_analysis,
            "similar_tracks": jamendo_tracks
        }

    except AIServiceError as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        # Return partial results if Gemini fails
        return {
            "recognized_track": recognized_track,
            "source_track": musixmatch_metadata,
            "musicbrainz_data": musicbrainz_data,
            "discogs_data": discogs_data,
            "wikipedia_summary": wikipedia_summary,
            "analysis": {"description": "AI analysis failed.", "keywords": []},
            "similar_tracks": []
        }
    except HTTPException as http_exc: # Re-raise HTTP exceptions (e.g., 404 from AcoustID)
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error during file processing pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during file processing."
        )

# Remove the old /process-link implementation if not needed, or update it similarly
# @router.post("/process-link") ... 