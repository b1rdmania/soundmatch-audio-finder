import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Link } from 'react-router-dom'; // Keep link if needed, or remove

const WhitePaper: React.FC = () => { // Keep component name as WhitePaper
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16">
        <div className="container px-4 md:px-6 max-w-3xl mx-auto">
          {/* --- Start Content from TechOverview --- */}
          <h1 className="text-3xl font-bold mb-6 border-b pb-2">Project White Paper</h1> {/* Updated Title */}
          
           {/* Hackathon Note */}
          <div className="bg-primary/10 border border-primary/20 text-primary p-4 rounded-md mb-6 text-sm">
            <h2 className="font-semibold mb-2">Hackathon Project - Seeking Partners!</h2>
            <p>
              This project is being developed for a hackathon and we are actively looking for enthusiastic partners to join the team! 
              If you're interested in AI, music technology, web development (React/FastAPI), or data services like MusicBrainz and Jamendo, please reach out!
            </p>
          </div>

          {/* Project Goal */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-3">Project Goal</h2>
            <p className="text-muted-foreground leading-relaxed">
              SoundMatch AI aims to be an intelligent platform that helps content creators, developers, and music enthusiasts discover copyright-free music similar to a provided track or audio file. Users can search by song/artist or upload an MP3 file. The core idea is to leverage metadata analysis and AI-driven similarity matching to provide relevant and usable music recommendations.
            </p>
          </section>

          {/* Technology Stack */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-3">Technology Stack</h2>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li><strong>Frontend:</strong> React, Vite, TypeScript, Tailwind CSS, shadcn-ui</li>
              <li><strong>Backend:</strong> Python, FastAPI</li>
              <li><strong>Audio Recognition:</strong> Shazam (via third-party wrapper)</li>
              <li><strong>Metadata Sources:</strong> Musixmatch, MusicBrainz, Discogs, Wikipedia</li>
              <li><strong>AI Analysis & Keywords:</strong> Google Gemini (gemini-1.5-flash)</li>
              <li><strong>Royalty-Free Music Search:</strong> Jamendo API</li>
              <li><strong>Deployment:</strong> Vercel (Frontend), Railway (Backend)</li>
              </ul>
          </section>

          {/* Development Progress */}
          <section className="mb-8">
             <h2 className="text-2xl font-semibold mb-3">Development Progress So Far</h2>
             <div className="space-y-4 text-muted-foreground">
                <div>
                    <h3 className="font-semibold text-foreground mb-1">Backend API (FastAPI)</h3>
                    <ul className="list-disc list-inside space-y-1 pl-4 text-sm">
                        <li>Implemented endpoints for `/search` (title/artist) and `/process-file` (upload).</li>
                        <li>Integrated Musixmatch client with fallback search logic.</li>
                        <li>Integrated Shazam client for audio recognition.</li>
                        <li>Integrated MusicBrainz client for MBID and tags.</li>
                        <li>Integrated Discogs client for release year, styles, genres, and cover art URL.</li>
                        <li>Integrated Wikipedia client for fetching summaries.</li>
                        <li>Integrated Gemini client for AI analysis, refining the prompt to synthesize data from all sources and use internal knowledge.</li>
                        <li>Integrated Jamendo client for royalty-free search based on Gemini keywords.</li>
                        <li>Configured CORS, environment variables, logging.</li>
                </ul>
                </div>
                <div>
                    <h3 className="font-semibold text-foreground mb-1">Frontend (React)</h3>
                     <ul className="list-disc list-inside space-y-1 pl-4 text-sm">
                        <li>Set up application structure with Vite and TypeScript.</li>
                        <li>Created main pages and routing.</li>
                        <li>Developed `UploadForm` component.</li>
                        <li>Refactored `Results` page to display cover art, detailed metadata summary, Wikipedia summary, and remove raw data dumps.</li>
                        <li>Added audio playback controls (play/pause/seek) for Jamendo results.</li>
                        <li>Implemented dynamic "Analyzing..." loading state.</li>
                        <li>Styled with Tailwind CSS and `shadcn-ui`.</li>
                    </ul>
                </div>
                 <div>
                    <h3 className="font-semibold text-foreground mb-1">Deployment & Infrastructure</h3>
                    <ul className="list-disc list-inside space-y-1 pl-4 text-sm">
                        <li>Frontend deployed to Vercel, Backend to Railway.</li>
                        <li>Configured necessary environment variables.</li>
                    </ul>
                </div>
                <div>
                    <h3 className="font-semibold text-foreground mb-1">Troubleshooting & Refinement</h3>
                    <ul className="list-disc list-inside space-y-1 pl-4 text-sm">
                        <li>Resolved CORS issues.</li>
                        <li>Iteratively fixed backend API integration errors.</li>
                        <li>Removed discontinued AcousticBrainz integration, replacing with richer sources.</li>
                        <li>Refined Gemini prompt multiple times to improve analysis specificity.</li>
                        <li>Improved frontend layout and data presentation.</li>
                    </ul>
                </div>
            </div>
          </section>

           {/* Next Steps */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-3">Next Steps / Known Limitations</h2>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Improve Wikipedia Search Term strategy.</li>
              <li>Refine Gemini Prompt further based on testing diverse tracks.</li>
              <li>Enhance Jamendo Keyword Strategy (beyond simple keyword matching).</li>
              <li>Implement `/process-link` functionality.</li>
              <li><strong>Advanced Similarity (Potential V2 / Premium Feature):</strong> Consider FAISS or other vector similarity if keyword search proves insufficient.</li>
              <li>Expand Music Sources (integrate more royalty-free libraries).</li>
              <li>Add comprehensive unit and integration tests.</li>
              <li>Optimize API calls for performance and scalability.</li>
              <li>Further UI/UX Polish (loading indicators, mobile responsiveness).</li>
            </ul>
          </section>
          {/* --- End Content from TechOverview --- */}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default WhitePaper; // Export as WhitePaper
