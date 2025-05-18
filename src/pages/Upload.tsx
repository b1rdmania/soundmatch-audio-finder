import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import UploadForm from '@/components/UploadForm';

const Upload = () => {
  const navigate = useNavigate();

  const handleUpload = (data: any) => {
    // Navigate to results page with the data
    navigate('/results', { state: { results: data } });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-28 pb-16 bg-gradient-to-b from-secondary/30 to-background">
        <div className="container px-4 md:px-6">
          <div className="max-w-3xl mx-auto text-center mb-10 animate-slide-up">
            <h1 className="text-3xl font-bold tracking-tight mb-3">Find Your Perfect Sound</h1>
            <p className="text-muted-foreground text-lg">
              Upload a song or paste a YouTube link to discover similar copyright-free music.
            </p>
          </div>
          
          <UploadForm onUpload={handleUpload} />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Upload;
