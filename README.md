# SoundMatch AI - Find Similar Copyright-Free Music

**Version 1.0.0 - MVP Release**

This project helps content creators, developers, and music enthusiasts discover copyright-free music similar to a provided track or audio file. Initially developed as a hackathon project, this v1.0.0 marks the first stable MVP release.

We welcome contributions! If you're interested in AI, music technology, web development (React/FastAPI), or data services, please check out our "Next Steps" or open an issue with your ideas.

## Project Goal

SoundMatch AI aims to be an intelligent platform that helps content creators, developers, and music enthusiasts discover copyright-free music similar to a provided track or audio file.

Users can:
- **Search by song/artist:** Enter a known song, and the app will find similar royalty-free alternatives.
- **Upload an MP3:** Analyze an existing audio file to find similar royalty-free tracks.
- **Paste a link:** Analyze a YouTube link to find similar royalty-free tracks.

The core idea is to leverage metadata analysis (using MusicBrainz) and similarity searching (using Jamendo) to provide relevant and usable music recommendations.

## Technology Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS, shadcn-ui
- **Backend:** Python, FastAPI
- **Audio Fingerprinting:** AcoustID (with Chromaprint)
- **Metadata APIs:**
    - MusicBrainz (`musicbrainzngs` library)
    - Discogs API
    - (Musixmatch API was also integrated for lyrics/metadata enrichment)
- **Royalty-Free Music Source:** Jamendo API
- **AI Content Analysis/Tagging:** Google Gemini Pro (via `google-generativeai` library)
- **Audio Input Sources:** MP3 Upload, YouTube Link (via `google-api-python-client` for metadata/processing)
- **Deployment:** Vercel (Frontend), Railway (Backend)

## Development Progress So Far

We have made significant progress in building the core infrastructure and functionality:

- **Backend API (FastAPI on Railway):**
    - Set up FastAPI application structure.
    - Implemented API endpoints for:
        - `/search`: Takes title/artist, fetches metadata from Musixmatch (with fallback search), MusicBrainz, Discogs, and Wikipedia. Analyzes combined data with Gemini to generate description/keywords, then searches Jamendo.
        - `/process-file`: Accepts an MP3 upload, recognizes it using AcoustID (with ID3 tag fallback), fetches metadata from Musixmatch/MusicBrainz/Discogs/Wikipedia, analyzes with Gemini, and searches Jamendo.
        - *`/process-link`: (Future Feature) Accepts a music URL.*
    - Integrated Musixmatch client with fallback logic (`matcher.track.get` -> `track.search`).
    - Integrated AcoustID client (with Chromaprint's fpcalc) for audio fingerprinting and recognition.
    - Integrated MusicBrainz client to fetch recording MBID and tags.
    - Integrated Discogs client to fetch release year, styles, genres, and **cover art URL**.
    - Integrated **Wikipedia client** to fetch introductory summaries.
    - Integrated **Gemini client (gemini-1.5-flash)**:
        - Refined prompt significantly to **synthesize data from all sources (Musixmatch, MusicBrainz, Discogs)**.
        - Instructed Gemini to use its **internal knowledge base** to enhance descriptions (e.g., specific instruments, production).
        - Improved keyword generation strategy for more specific Jamendo searches.
    - Integrated Jamendo client for searching copyright-free music based on Gemini keywords.
    - Configured CORS, environment variables, logging, and basic error handling.
    - Created Docker configurations for potential containerization.
- **Frontend (React on Vercel):**
    - Set up React application using Vite and TypeScript.
    - Created main pages (Index, Upload, Results) and routing.
    - Developed the `UploadForm` component.
    - Significantly **refactored the `Results` page**:
        - Displays the source track with **cover art** (from Discogs/Shazam).
        - Shows a detailed summary including data from Musixmatch, Discogs (genres, styles, year), and linked IDs (Discogs, MusicBrainz).
        - Displays the **Wikipedia summary** in a dedicated section.
        - Removed the raw technical data dumps.
        - Added **audio playback controls** (play/pause/seek) for Jamendo results.
        - Implemented a dynamic "Analyzing..." loading state.
    - Integrated API client (`axios`) to communicate with the backend.
    - Styled with Tailwind CSS and `shadcn-ui`.
    - Added user feedback (toasts) for playback errors.
- **Deployment & Infrastructure:**
    - Frontend successfully deployed to Vercel.
    - Backend successfully deployed to Railway.
    - Configured environment variables for all services.
- **Troubleshooting & Refinement:**
    - Resolved CORS issues.
    - Iteratively fixed backend API errors related to various service integrations (Musixmatch, MusicBrainz, Discogs, Gemini, Jamendo) and error handling logic.
    - Addressed initial **limitations with AcousticBrainz** (unreliable/discontinued data) by **removing it** and integrating richer sources (Discogs/MusicBrainz).
    - Refined Gemini prompt multiple times to improve analysis specificity and keyword quality based on synthesized metadata.
    - Improved frontend layout and data presentation based on available information.

## Next Steps / Known Limitations

- **Improve Wikipedia Search Term:** Experiment with different search terms (e.g., `"Song Title (song)"`) for better Wikipedia summary results.
- **Refine Gemini Prompt Further:** Continue tuning the prompt based on analysis quality for diverse tracks.
- **Enhance Jamendo Keyword Strategy:** Explore techniques beyond simple keyword search on Jamendo (e.g., using tags, filtering by license).
- **Link Processing:** Implement `/process-link` functionality.
- **Advanced Similarity (Future):** Consider FAISS or vector similarity if keyword search proves insufficient.
- **Expand Music Sources:** Integrate more royalty-free libraries.
- **Testing:** Add comprehensive unit and integration tests.
- **Scalability & Performance:** Optimize API calls, especially concurrent requests to external services.
- **UI/UX Polish:** Add more loading indicators, refine playback controls, improve mobile responsiveness.

## Getting Started Locally

To run this project locally:

1.  **Clone the repository:**
    ```bash
    git clone <YOUR_GIT_URL>
    cd soundmatch-audio-finder
    ```
2.  **Set up Backend:**
    - Navigate to the backend directory (if structure dictates, otherwise root).
    - Create a Python virtual environment: `python -m venv .venv`
    - Activate the virtual environment: `source .venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
    - Install backend dependencies: `pip install -r requirements.txt`
    - Install Chromaprint for audio fingerprinting: 
      - macOS: `brew install chromaprint`
      - Ubuntu/Debian: `apt-get install libchromaprint-tools`
      - Windows: Download from [AcoustID website](https://acoustid.org/chromaprint)
    - Create a `.env` file based on `.env.example` and add your API keys:
      - `ACOUSTID_APP_API_KEY`: Get from [AcoustID Applications](https://acoustid.org/applications)
      - `MUSIXMATCH_API_KEY`: Get from [Musixmatch Developer Dashboard](https://developer.musixmatch.com/)
      - Other API keys as needed
    - Run the backend server: `uvicorn app.main:app --reload --port 8000`
3.  **Set up Frontend:**
    - Navigate to the frontend directory (if structure dictates, otherwise root).
    - Install frontend dependencies: `npm install`
    - Create a `.env.local` file and add `VITE_API_URL=http://localhost:8000/api/v1` (or your backend URL).
    - Run the frontend development server: `npm run dev`

The frontend should be accessible at `http://localhost:5173` (or another port specified by Vite).

**Join Us!**

If you're excited about this project and want to contribute during the hackathon, please reach out!
