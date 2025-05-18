
import React, { useState } from 'react';
import { Send, Loader2, Mail, Phone } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

const ContactForm = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!name || !email || !message) {
      toast({
        title: "Missing information",
        description: "Please fill in all fields.",
        variant: "destructive",
      });
      return;
    }
    
    if (!email.includes('@')) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address.",
        variant: "destructive",
      });
      return;
    }
    
    // Simulate form submission
    setIsLoading(true);
    
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Message sent",
        description: "We'll get back to you as soon as possible.",
      });
      
      // Reset form
      setName('');
      setEmail('');
      setMessage('');
    }, 1500);
  };
  
  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="name" className="block text-sm font-medium">
            Name
          </label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full"
            placeholder="Your name"
          />
        </div>
        
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full"
            placeholder="your.email@example.com"
          />
        </div>
        
        <div className="space-y-2">
          <label htmlFor="message" className="block text-sm font-medium">
            Message
          </label>
          <Textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
            className="w-full resize-none"
            placeholder="Your message..."
          />
        </div>
        
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Send className="mr-2 h-5 w-5" />
              Send Message
            </>
          )}
        </Button>
      </form>

      <div className="pt-6 border-t border-border">
        <h3 className="text-lg font-medium mb-4">Contact Us Directly</h3>
        <div className="space-y-3">
          <a href="mailto:contact@soundmatch.ai" className="flex items-center text-primary hover:underline">
            <Mail className="mr-2 h-5 w-5" />
            contact@soundmatch.ai
          </a>
          <a href="tel:+15551234567" className="flex items-center text-primary hover:underline">
            <Phone className="mr-2 h-5 w-5" />
            +1 (555) 123-4567
          </a>
        </div>
      </div>
    </div>
  );
};

export default ContactForm;
