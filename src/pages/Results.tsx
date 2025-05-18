import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import SearchResult from '@/components/SearchResult';
import { filterOptions, applyFilters } from '@/lib/music-utils';
import { ArrowUp, Filter, Music, Download, Play, Pause } from 'lucide-react';
import { SearchResultProps } from '@/components/SearchResult';
import { toast } from 'react-hot-toast';

// Interface for props passed to AnalyzingDisplay
interface AnalyzingDisplayProps {
  title: string;
  artist: string;
}

// New component for the "Analyzing" display
const AnalyzingDisplay: React.FC<AnalyzingDisplayProps> = ({ title, artist }) => {
  const buildId = "build_" + Math.random().toString(16).slice(8); // Add a random build ID
  // Dynamically generate lines using props
  const lines = [
    `> Initializing SoundMatch Analysis Core v3.2... OK [${buildId}]`, // Add build ID here
    `> Target Locked: ${artist} - ${title}`,
    `> Engaging Musixmatch API [matcher.track.get]...`,
    // Simulate success/fallback/failure - add slight randomness/variation
    `> Musixmatch Query Status: ${Math.random() > 0.1 ? (Math.random() > 0.3 ? 'Exact Match Found.' : 'Fallback Search Initiated... Match Acquired.') : 'Metadata Retrieval Failed.'}`,
    `> Searching MusicBrainz Identifier Index...`,
    // Simulate MB search outcome
    `> MusicBrainz Lookup: ${Math.random() > 0.4 ? 'MBID Located. Tags Extracted (if available).' : 'No Match Found/Low Confidence.'}`,
    `> Preparing Metadata Payload for AI Analysis...`,
    `> Initializing Gemini Language Model [gemini-1.5-flash]... Ready.`,
    `> Generating Sonic Description & Keyword Matrix...`,
    `> Gemini Analysis: ${Math.random() > 0.1 ? 'Synthesis Complete.' : 'Analysis Timed Out/Failed.'}`,
    `> Cross-Referencing Jamendo Royalty-Free Database [fuzzytags]...`,
    `> Compiling Results Vector... DONE`,
    `> Rendering Output Interface... [Display v1.1]` // Keep previous version marker too
  ];
  const [displayedLines, setDisplayedLines] = useState<string[]>([]);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    let index = 0;
    const intervalId = setInterval(() => {
      if (index < lines.length) {
        setDisplayedLines((prev) => [...prev, lines[index]]);
        index++;
      } else {
        clearInterval(intervalId);
      }
    }, 300);

    const cursorInterval = setInterval(() => {
        setShowCursor((prev) => !prev);
    }, 500);

    return () => {
        clearInterval(intervalId);
        clearInterval(cursorInterval);
    };
  }, [lines]); // Dependency array includes lines, which change if title/artist change

  return (
    <div className="font-mono text-sm text-muted-foreground bg-card p-4 rounded-md shadow-lg border min-h-[220px]">
      {/* Displaying analysis steps */}
      {displayedLines.map((line, i) => (
        <p key={i}>{line}</p>
      ))}
      {showCursor && <span className="animate-pulse text-primary">_</span>}
    </div>
  );
};

// Helper to format time (seconds) as MM:SS
const formatTime = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes < 10 ? '0' : ''}${minutes}:${secs < 10 ? '0' : ''}${secs}`;
};

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: string;
  audio_url: string;
  download_url: string;
  license: string;
  tags: string[];
  mood: string;
  similarity: number;
  image_url?: string;
}

interface ResultsData {
  musicbrainz_data?: { // ADD MusicBrainz data
      mbid?: string;
      match_score?: number;
      tags?: string[];
      // Add other potential MB fields if fetched later
      [key: string]: any; 
  } | null;
  discogs_data?: { // ADD Discogs data
      discogs_id?: number;
      styles?: string[];
      year?: number;
      genres?: string[]; // Discogs genres
      image_url?: string; // Add Discogs image URL
      [key: string]: any;
  } | null;
  source_track?: { // From text search (Musixmatch)
    title: string;
    artist: string;
    genres?: string[];
    rating?: number;
    explicit?: boolean;
    instrumental?: boolean; // Added this based on Musixmatch parser
    musixmatch_id?: number; // Added this based on Musixmatch parser
    commontrack_id?: number; // Added this based on Musixmatch parser
    album?: string; // Added this based on Musixmatch parser
    updated_time?: string; // Added this based on Musixmatch parser
    // Add other fields from Musixmatch if needed
  } | null;
  recognized_track?: { // From file upload (AcoustID)
    title?: string | null;      // Title from AcoustID/MusicBrainz recording
    subtitle?: string | null;   // Artist from AcoustID/MusicBrainz recording
    acoustid_id?: string | null;// AcoustID's own track ID for the fingerprint cluster
    mbid?: string | null;       // MusicBrainz Recording ID associated with the AcoustID
    score?: number | null;      // AcoustID match confidence score (0.0 to 1.0)
  } | null;
  analysis?: { // From Gemini
    description: string;
    keywords: string[];
  } | null;
  wikipedia_summary?: string | null; // ADD Wikipedia summary
  similar_tracks: Track[];
}

const Results: React.FC = () => {
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const [playingTrack, setPlayingTrack] = React.useState<string | null>(null);
  const audioRef = React.useRef<HTMLAudioElement | null>(null);
  // New state for seek bar
  const [currentTime, setCurrentTime] = React.useState<number>(0);
  const [duration, setDuration] = React.useState<number>(0);
  
  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
    };
    
    window.addEventListener('scroll', handleScroll);
    
    // Simulate analysis delay
    const analysisTimeout = setTimeout(() => {
        setIsAnalyzing(false);
    }, 3500); // New increased delay (3.5 seconds)

    return () => {
        window.removeEventListener('scroll', handleScroll);
        clearTimeout(analysisTimeout); // Clear timeout on unmount
    };
  }, []);
  
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  // Effect to handle audio cleanup when track changes or component unmounts
  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  const handlePlay = (trackId: string, audioUrl: string) => {
    if (playingTrack === trackId) {
      audioRef.current?.pause();
      setPlayingTrack(null);
    } else {
      // Stop currently playing track if any
      if (audioRef.current) {
        audioRef.current.pause();
      }
      // Create new audio element
      audioRef.current = new Audio(audioUrl);
      setPlayingTrack(trackId);
      setCurrentTime(0);
      setDuration(0);

      // Add listeners for seek bar
      audioRef.current.addEventListener('loadedmetadata', () => {
        setDuration(audioRef.current?.duration || 0);
      });
      audioRef.current.addEventListener('timeupdate', () => {
        setCurrentTime(audioRef.current?.currentTime || 0);
      });
       audioRef.current.addEventListener('ended', () => {
         setPlayingTrack(null); // Reset button when track ends
         setCurrentTime(0);
       });

      audioRef.current.play().catch(e => {
        console.error("Error playing audio:", e);
        toast.error(`Error playing track: ${e.message}`)
        setPlayingTrack(null); // Reset state on error
      });
    }
  };

  const handleSeek = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (audioRef.current) {
      const newTime = Number(event.target.value);
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };
  
  const resultsData = location.state?.results as ResultsData | undefined;
  // Ensure sourceTrack for Musixmatch uses the right object based on origin
  const musixmatchDataSource = resultsData?.source_track; // Use source_track if search result
  const recognizedDataSource = resultsData?.recognized_track; // Use recognized_track if upload result
  const sourceTrackForDisplay = musixmatchDataSource || recognizedDataSource; // Fallback for display
  
  const musicbrainz_data = resultsData?.musicbrainz_data;
  const discogs_data = resultsData?.discogs_data;
  const analysis = resultsData?.analysis;
  const wikipedia_summary = resultsData?.wikipedia_summary; // ADD extraction
  const similarTracks = resultsData?.similar_tracks || [];

  // Determine display title/artist *before* the return statement
  const displayTitle = sourceTrackForDisplay?.title || 'Unknown Title';
  const displayArtist = musixmatchDataSource?.artist || recognizedDataSource?.subtitle || 'Unknown Artist';
  // Determine image URL to use - Rely only on Discogs for uploaded files now.
  const sourceImageUrl = discogs_data?.image_url;

  // --- Conditional Rendering Logic ---

  // 1. If analyzing, show the hacker display, passing title/artist
  if (isAnalyzing) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow pt-28 pb-16 flex items-center justify-center">
          <div className="container px-4 md:px-6 max-w-2xl">
             <AnalyzingDisplay title={displayTitle} artist={displayArtist} />
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // 2. If analysis done, but no results/source track, show "Not Found"
  if (!resultsData || !sourceTrackForDisplay) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16">
        <div className="container px-4 md:px-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-4">No Results Found</h1>
              <button
                onClick={() => navigate('/upload')}
                className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // 3. If analysis done and results exist, show the results
  const displayTags = resultsData?.source_track?.genres || analysis?.keywords || [];
  
  // Construct external search URLs
  const searchTerm = encodeURIComponent(`${displayArtist} ${displayTitle}`);
  const wikipediaSearchUrl = `https://en.wikipedia.org/w/index.php?search=${searchTerm}`;
  const discogsSearchUrl = `https://www.discogs.com/search/?q=${searchTerm}&type=all`;
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16">
        <div className="container px-4 md:px-6">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-4">Source Track</h1>
              {/* --- Updated Source Track Card --- */}
              <div className="bg-white rounded-lg p-6 shadow-sm border flex flex-col sm:flex-row items-start gap-6">
                 {/* Image Column */} 
                 {sourceImageUrl ? (
                    <img 
                        src={sourceImageUrl} 
                        alt={`${displayTitle} cover art`} 
                        className="w-full sm:w-32 h-auto sm:h-32 rounded-md object-cover flex-shrink-0 shadow-md border" 
                    />
                 ) : (
                    <div className="w-full sm:w-32 h-32 rounded-md bg-gray-100 flex items-center justify-center text-muted-foreground flex-shrink-0">
                        <Music className="w-12 h-12" />
                    </div>
                 )}
                 {/* Details Column */} 
                 <div className="flex-1">
                    <h2 className="text-xl font-semibold mb-1">{displayTitle}</h2>
                    <p className="text-muted-foreground mb-4">{displayArtist}</p>
                    {displayTags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {displayTags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    {analysis?.description && (
                      <div className="mt-4 pt-4 border-t border-muted">
                        <h3 className="text-lg font-semibold mb-2">AI Analysis:</h3>
                        <p className="text-muted-foreground italic text-sm">{analysis.description}</p>
                      </div>
                    )}
                     {/* Enhanced Details Section (Moved inside card) */} 
                     <div className="mt-4 pt-4 border-t border-muted text-sm">
                         <h4 className="font-semibold mb-2">Summary Details:</h4>
                         <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                             {discogs_data?.year && (
                                 <li><span className="font-medium text-foreground">Year:</span> {discogs_data.year}</li>
                             )}
                             {musixmatchDataSource?.genres && musixmatchDataSource.genres.length > 0 && (
                                 <li><span className="font-medium text-foreground">Genres (Musixmatch):</span> {musixmatchDataSource.genres.join(', ')}</li>
                             )}
                             {discogs_data?.genres && discogs_data.genres.length > 0 && (
                                  <li><span className="font-medium text-foreground">Genres (Discogs):</span> {discogs_data.genres.join(', ')}</li>
                             )}
                             {discogs_data?.styles && discogs_data.styles.length > 0 && (
                                  <li><span className="font-medium text-foreground">Styles (Discogs):</span> {discogs_data.styles.join(', ')}</li>
                             )}
                              {/* Check Musixmatch data specifically for Instrumental/Explicit flags */} 
                              {musixmatchDataSource?.instrumental !== undefined && (
                                  <li><span className="font-medium text-foreground">Instrumental:</span> {musixmatchDataSource.instrumental ? 'Yes' : 'No'}</li>
                              )}
                              {musixmatchDataSource?.explicit !== undefined && (
                                  <li><span className="font-medium text-foreground">Explicit:</span> {musixmatchDataSource.explicit ? 'Yes' : 'No'}</li>
                              )}
                              {musicbrainz_data?.mbid && (
                                 <li>
                                    <span className="font-medium text-foreground">MusicBrainz ID:</span> 
                                    <a href={`https://musicbrainz.org/recording/${musicbrainz_data.mbid}`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline ml-1">{musicbrainz_data.mbid}</a>
                                 </li>
                             )}
                         </ul>
                     </div>
              </div>
                 {/* --- Add Discogs Link under Image (in Image Column) --- */}
                 <div className="w-full sm:w-32 flex-shrink-0 mt-2">
                     {discogs_data?.discogs_id && (
                          <a 
                              href={`https://www.discogs.com/release/${discogs_data.discogs_id}`} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="block text-center text-xs mt-2 text-primary hover:underline"
                          >
                              View on Discogs
                          </a>
                     )}
              </div>
              </div>
            </div>
            
            {/* --- Wikipedia Summary Section --- */}
            {wikipedia_summary && (
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4 flex items-center">
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}> <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /> </svg> 
                         Wikipedia Summary
                    </h2>
                    <div className="bg-white rounded-lg p-6 shadow-sm border">
                        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{wikipedia_summary}</p>
                         <a 
                            href={wikipediaSearchUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-xs text-primary hover:underline mt-3 inline-block"
                         >
                            Read more on Wikipedia...
                         </a>
                    </div>
          </div>
            )}
            
            <div className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">Find out more</h2>
                <div className="bg-white rounded-lg p-4 shadow-sm border flex items-center space-x-4">
                    <a 
                        href={wikipediaSearchUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-sm"
                    >
                        Search on Wikipedia
                    </a>
              </div>
              </div>
              
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold mb-2">Similar Royalty-Free Tracks (from Jamendo)</h2>
              {/* Display Keywords Used */}
              {analysis?.keywords && analysis.keywords.length > 0 && (
                  <div className="mb-4 text-sm text-muted-foreground">
                      <span className="font-medium text-foreground">Keywords used:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                          {analysis.keywords.map((kw, idx) => (
                              <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs font-mono">{kw}</span>
                          ))}
              </div>
            </div>
          )}
          
              {similarTracks.length > 0 ? (
                similarTracks.map((track) => (
                  <div
                    key={track.id}
                    className="bg-gray-50 rounded-lg p-4 shadow-md border border-gray-200 hover:shadow-lg transition-all duration-200 flex space-x-4 items-center"
                  >
                    {track.image_url && (
                        <img 
                            src={track.image_url} 
                            alt={`${track.title} artwork`} 
                            className="w-16 h-16 rounded-md object-cover flex-shrink-0 shadow-sm"
                        />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 pr-4">
                          <h3 className="font-semibold truncate">{track.title}</h3>
                          <p className="text-muted-foreground text-sm truncate">{track.artist}</p>
                          {track.tags && track.tags.length > 0 && (
                             <div className="flex flex-wrap gap-1 mt-2">
                               {track.tags.slice(0, 5).map((tag, index) => (
                                 <span
                                   key={index}
                                   className="px-2 py-0.5 bg-secondary/10 text-secondary rounded-full text-xs"
                                 >
                                   {tag}
                                 </span>
            ))}
          </div>
                          )}
                          <p className="mt-2 text-xs text-muted-foreground">License: {track.license}</p>
                        </div>
                        <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-2 mt-2 md:mt-0"> {/* Container for controls */} 
                          <button
                            onClick={() => handlePlay(track.id, track.audio_url)}
                            className="p-2 rounded-full text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-colors"
                            title={playingTrack === track.id ? "Pause" : "Play"}
                          >
                            {playingTrack === track.id ? (
                              <Pause className="h-5 w-5" />
                            ) : (
                              <Play className="h-5 w-5" />
                            )}
                          </button>
                          {/* --- Seek Bar --- */}
                          {playingTrack === track.id && (
                            <div className="flex items-center space-x-2 w-full md:w-auto">
                                <span className="text-xs text-muted-foreground w-10 text-right">{formatTime(currentTime)}</span>
                                <input 
                                    type="range"
                                    min="0"
                                    max={duration}
                                    value={currentTime}
                                    onChange={handleSeek}
                                    className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer range-sm dark:bg-gray-700 accent-primary"
                                />
                                <span className="text-xs text-muted-foreground w-10">{formatTime(duration)}</span>
                            </div>
                          )}
                          {/* --- Download Button --- */}
                          <a
                            href={track.download_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 rounded-full text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-colors"
                            title="Download"
                          >
                            <Download className="h-5 w-5" />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                 <p className="text-muted-foreground">No similar tracks found on Jamendo based on the analysis.</p>
              )}
            </div>
          </div>
        </div>
      </main>
      
      {showBackToTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 p-3 bg-primary text-primary-foreground rounded-full shadow-lg transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary/20 animate-slide-up"
          aria-label="Back to top"
        >
          <ArrowUp className="h-6 w-6" />
        </button>
      )}
      
      <Footer />
    </div>
  );
};

export default Results;
