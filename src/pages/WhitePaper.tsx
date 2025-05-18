
import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { FileText, Zap, Code } from 'lucide-react';

const WhitePaper: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16 bg-gradient-to-b from-secondary/30 to-background">
        <div className="container px-4 md:px-6 max-w-3xl mx-auto">
          <div className="mb-8 animate-slide-up">
            <h1 className="text-3xl font-bold tracking-tight mb-3">SoundMatch AI - Technical White Paper</h1>
            <p className="text-lg text-muted-foreground mb-4">
              A comprehensive technical overview of our AI-driven music matching platform
            </p>
            <Separator className="my-6" />
          </div>
          
          {/* Hackathon Note */}
          <div className="bg-primary/10 border border-primary/20 text-primary p-6 rounded-xl mb-8 text-sm animate-fade-in">
            <h2 className="font-semibold text-xl mb-3 flex items-center">
              <Zap className="mr-2 h-5 w-5" />
              Hackathon Project - Seeking Partners!
            </h2>
            <p className="leading-relaxed mb-2">
              This project is being developed for a hackathon and we are actively looking for enthusiastic partners to join the team! 
              If you're interested in AI, music technology, web development (React/FastAPI), or data services like MusicBrainz and Jamendo, please reach out!
            </p>
            <Link 
              to="/about" 
              className="text-primary hover:text-primary/80 font-medium inline-flex items-center mt-2"
            >
              Contact Us <span className="ml-1">→</span>
            </Link>
          </div>

          {/* Project Goal */}
          <section className="mb-10 bg-card rounded-xl p-6 border shadow-sm animate-slide-up">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <FileText className="mr-2 h-5 w-5 text-primary" />
              Project Goal
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              SoundMatch AI aims to be an intelligent platform that helps content creators, developers, and music enthusiasts discover copyright-free music similar to a provided track or audio file. Users can search by song/artist or upload an MP3 file. The core idea is to leverage metadata analysis and AI-driven similarity matching to provide relevant and usable music recommendations.
            </p>
          </section>

          {/* Technology Stack */}
          <section className="mb-10 bg-card rounded-xl p-6 border shadow-sm animate-slide-up" style={{animationDelay: "0.1s"}}>
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <Code className="mr-2 h-5 w-5 text-primary" />
              Technology Stack
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium mb-2 text-lg">Frontend</h3>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground pl-2">
                  <li>React with TypeScript</li>
                  <li>Vite build system</li>
                  <li>Tailwind CSS</li>
                  <li>shadcn-ui components</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-lg">Backend</h3>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground pl-2">
                  <li>Python with FastAPI</li>
                  <li>Shazam API integration</li>
                  <li>Google Gemini AI</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-lg">Data Services</h3>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground pl-2">
                  <li>Musixmatch</li>
                  <li>MusicBrainz</li>
                  <li>Discogs</li>
                  <li>Wikipedia</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-lg">Infrastructure</h3>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground pl-2">
                  <li>Vercel (Frontend)</li>
                  <li>Railway (Backend)</li>
                  <li>Jamendo API (Royalty-Free Music)</li>
                </ul>
              </div>
            </div>
          </section>
          
          {/* Development Progress */}
          <section className="mb-10 bg-card rounded-xl p-6 border shadow-sm animate-slide-up" style={{animationDelay: "0.2s"}}>
             <h2 className="text-2xl font-semibold mb-4">Development Progress</h2>
             <div className="space-y-6 text-muted-foreground">
                <div className="space-y-3">
                    <h3 className="font-medium text-foreground text-lg flex items-center">
                      <span className="inline-block w-2 h-2 rounded-full bg-primary mr-2"></span>
                      Backend API (FastAPI)
                    </h3>
                    <ul className="list-disc list-inside space-y-1.5 pl-4 text-sm">
                        <li>Implemented endpoints for <code className="text-xs bg-muted px-1 py-0.5 rounded">/search</code> (title/artist) and <code className="text-xs bg-muted px-1 py-0.5 rounded">/process-file</code> (upload).</li>
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
                <div className="space-y-3">
                    <h3 className="font-medium text-foreground text-lg flex items-center">
                      <span className="inline-block w-2 h-2 rounded-full bg-primary mr-2"></span>
                      Frontend (React)
                    </h3>
                    <ul className="list-disc list-inside space-y-1.5 pl-4 text-sm">
                        <li>Set up application structure with Vite and TypeScript.</li>
                        <li>Created main pages and routing.</li>
                        <li>Developed <code className="text-xs bg-muted px-1 py-0.5 rounded">UploadForm</code> component.</li>
                        <li>Refactored <code className="text-xs bg-muted px-1 py-0.5 rounded">Results</code> page to display cover art, detailed metadata summary, Wikipedia summary, and remove raw data dumps.</li>
                        <li>Added audio playback controls (play/pause/seek) for Jamendo results.</li>
                        <li>Implemented dynamic "Analyzing..." loading state.</li>
                        <li>Styled with Tailwind CSS and <code className="text-xs bg-muted px-1 py-0.5 rounded">shadcn-ui</code>.</li>
                    </ul>
                </div>
                <div className="space-y-3">
                    <h3 className="font-medium text-foreground text-lg flex items-center">
                      <span className="inline-block w-2 h-2 rounded-full bg-primary mr-2"></span>
                      Deployment & Infrastructure
                    </h3>
                    <ul className="list-disc list-inside space-y-1.5 pl-4 text-sm">
                        <li>Frontend deployed to Vercel, Backend to Railway.</li>
                        <li>Configured necessary environment variables.</li>
                    </ul>
                </div>
                <div className="space-y-3">
                    <h3 className="font-medium text-foreground text-lg flex items-center">
                      <span className="inline-block w-2 h-2 rounded-full bg-primary mr-2"></span>
                      Troubleshooting & Refinement
                    </h3>
                    <ul className="list-disc list-inside space-y-1.5 pl-4 text-sm">
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
          <section className="mb-10 bg-card rounded-xl p-6 border shadow-sm animate-slide-up" style={{animationDelay: "0.3s"}}>
            <h2 className="text-2xl font-semibold mb-4">Next Steps & Known Limitations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-muted-foreground">
              <div>
                <h3 className="font-medium text-foreground mb-2">Short Term</h3>
                <ul className="list-disc list-inside space-y-1.5 pl-2 text-sm">
                  <li>Improve Wikipedia Search Term strategy</li>
                  <li>Refine Gemini Prompt further</li>
                  <li>Enhance Jamendo Keyword Strategy</li>
                  <li>Implement <code className="text-xs bg-muted px-1 py-0.5 rounded">/process-link</code> functionality</li>
                  <li>Add comprehensive unit and integration tests</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-foreground mb-2">Long Term Vision</h3>
                <ul className="list-disc list-inside space-y-1.5 pl-2 text-sm">
                  <li><strong>Advanced Similarity:</strong> FAISS or vector similarity for Premium</li>
                  <li>Expand Music Sources beyond Jamendo</li>
                  <li>Optimize API calls for performance</li>
                  <li>Further UI/UX Polish</li>
                  <li>Build recommendation engine based on user preferences</li>
                </ul>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <Link 
                to="/invest" 
                className="text-primary hover:text-primary/80 font-medium inline-flex items-center"
              >
                Learn about investing in SoundMatch <span className="ml-1">→</span>
              </Link>
            </div>
          </section>

        </div>
      </main>
      <Footer />
    </div>
  );
};

export default WhitePaper;
