
import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Separator } from '@/components/ui/separator';
import { Mail, Music, Headphones, Mic2, Speaker } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const About = () => {
  const faqs = [
    {
      question: "How accurate is the AI matching?",
      answer: "Our AI analyzes multiple aspects of music including rhythm, melody, instrumentation, and energy levels to find similar tracks. While not perfect, it provides highly relevant matches based on the audio characteristics of your reference track."
    },
    {
      question: "What music libraries do you search?",
      answer: "We search through a curated collection of copyright-free music libraries including royalty-free platforms, Creative Commons sources, and public domain archives to find the best matches for your reference track."
    },
    {
      question: "Can I use the recommended tracks commercially?",
      answer: "Yes, all tracks in our results are copyright-free, but different tracks may have different license requirements. Always check the specific license type displayed with each track. Some may require attribution, while others might be completely free to use."
    },
    {
      question: "How do I give proper attribution?",
      answer: "For tracks that require attribution, you should include the artist name and song title in your project credits. The exact requirements can vary, so we recommend checking the specific license details provided with each track."
    },
    {
      question: "Are there any usage limitations?",
      answer: "While the tracks are copyright-free, some may have restrictions on using them in specific contexts or for particular projects. Always review the complete license terms before using a track in your commercial projects."
    }
  ];
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16 bg-gradient-to-b from-secondary/30 to-background">
        <div className="container px-4 md:px-6">
          <div className="mb-12 animate-slide-up max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center justify-center p-2 bg-secondary/20 rounded-full mb-4">
              <Headphones className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight mb-3">About SoundMatch AI</h1>
            <p className="text-xl text-muted-foreground">
              Finding copyright-free alternatives to your favorite music
            </p>
            <Separator className="my-8 max-w-md mx-auto" />
          </div>
          
          <section className="max-w-3xl mx-auto mb-16 animate-slide-up">
            <Card className="border-none shadow-lg">
              <CardContent className="p-8">
                <div className="flex items-start gap-6 mb-6">
                  <div className="mt-1">
                    <Music className="h-8 w-8 text-primary" />
                  </div>
                  <div>
                    <p className="text-lg text-muted-foreground mb-6">
                      SoundMatch AI is an innovative platform that helps creators find copyright-free music that sounds similar to their favorite tracks. Our powerful AI analyzes the audio characteristics of your reference song and searches through extensive libraries of free-to-use music to find the closest matches.
                    </p>
                    <p className="text-lg text-muted-foreground">
                      Whether you're a content creator, streamer, marketer, or game developer, our technology helps you find the perfect soundtrack for your projects while avoiding copyright issues. No more worrying about DMCA strikes or licensing fees – just great music that matches your creative vision.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
          
          <section className="max-w-3xl mx-auto mb-16">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center p-2 bg-secondary/20 rounded-full mb-4">
                <Mic2 className="h-6 w-6 text-primary" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight">How It Works</h2>
            </div>
            
            <Card className="border-none shadow-lg">
              <CardContent className="p-8">
                <p className="text-lg mb-8 text-center">
                  SoundMatch AI uses advanced audio processing technologies to find similar music:
                </p>
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="bg-secondary/10 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-medium">1</div>
                      <h3 className="text-xl font-semibold">Input Processing</h3>
                    </div>
                    <p className="text-muted-foreground">We accept MP3 uploads or extract audio from Spotify and YouTube links.</p>
                  </div>
                  <div className="bg-secondary/10 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-medium">2</div>
                      <h3 className="text-xl font-semibold">Feature Extraction</h3>
                    </div>
                    <p className="text-muted-foreground">Our AI analyzes tempo, rhythm, melody, timbre, and energy profiles using machine learning models.</p>
                  </div>
                  <div className="bg-secondary/10 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-medium">3</div>
                      <h3 className="text-xl font-semibold">Similarity Search</h3>
                    </div>
                    <p className="text-muted-foreground">We compare against our database of copyright-free music to find the closest matches.</p>
                  </div>
                  <div className="bg-secondary/10 rounded-xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-medium">4</div>
                      <h3 className="text-xl font-semibold">Results Delivery</h3>
                    </div>
                    <p className="text-muted-foreground">You receive a curated list of similar tracks with previews and download options.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
          
          <section className="max-w-3xl mx-auto mb-16">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center p-2 bg-secondary/20 rounded-full mb-4">
                <Speaker className="h-6 w-6 text-primary" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight">Frequently Asked Questions</h2>
            </div>
            
            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <div key={index} className="bg-card rounded-xl border shadow-sm overflow-hidden">
                  <details className="group">
                    <summary className="flex justify-between items-center p-6 cursor-pointer list-none">
                      <h3 className="font-medium text-lg">{faq.question}</h3>
                      <span className="transition-transform duration-300 group-open:rotate-180">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="h-5 w-5"
                        >
                          <polyline points="6 9 12 15 18 9" />
                        </svg>
                      </span>
                    </summary>
                    <div className="px-6 pb-6 pt-0 animate-slide-down">
                      <p className="text-muted-foreground">{faq.answer}</p>
                    </div>
                  </details>
                </div>
              ))}
            </div>
          </section>
          
          <section className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center p-2 bg-secondary/20 rounded-full mb-4">
                <Mail className="h-6 w-6 text-primary" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight">Get In Touch</h2>
            </div>
            
            <Card className="border-none shadow-lg">
              <CardContent className="p-8">
                <div className="text-center py-6">
                  <p className="text-lg text-muted-foreground mb-6">
                    Have questions, feedback, or need assistance with SoundMatch AI? We'd love to hear from you!
                  </p>
                  <a 
                    href="mailto:hello@soundmatch.app" 
                    className="inline-flex items-center text-primary text-xl font-medium hover:underline p-4 bg-secondary/20 rounded-full"
                  >
                    <Mail className="mr-2 h-6 w-6" />
                    hello@soundmatch.app
                  </a>
                </div>
              </CardContent>
            </Card>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default About;
