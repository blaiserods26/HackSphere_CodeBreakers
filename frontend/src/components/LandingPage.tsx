
import { Button, Card } from 'flowbite-react';
import { Router } from 'react-router-dom';

export default function LandingPage() {
   
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-slate-900 dark:from-slate-900 dark:to-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
          <div className="lg:w-1/2 space-y-6">
            <h1 className="text-4xl md:text-6xl font-bold text-foreground dark:text-white bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-500">
              Secure Your Inbox with Advanced Email Spoofing Detection
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Protect yourself from sophisticated email threats using our cutting-edge AI-powered detection system
            </p>
            <div className="flex gap-4">
              <Button gradientDuoTone="cyanToBlue" size="xl">
                Get Started
              </Button>
              <Button outline gradientDuoTone="cyanToBlue" size="xl">
                Learn More
              </Button>
            </div>
          </div>
          <div className="lg:w-1/2">
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg blur opacity-75 animate-pulse"></div>
              <div className="relative bg-background dark:bg-slate-800 rounded-lg p-6">
                <img
                  src="/email-security.svg"
                  alt="Email Security"
                  className="w-full h-auto"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-foreground dark:text-white">
          Advanced Protection Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="border border-cyan-500/20 hover:border-cyan-500/50 transition-all duration-300">
              <div className="flex flex-col items-center text-center">
                <div className="text-cyan-500 mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2 text-foreground dark:text-white">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-2xl p-8 md:p-12">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold mb-6 text-foreground dark:text-white">
              Ready to Secure Your Email Communications?
            </h2>
            <p className="text-lg mb-8 text-gray-600 dark:text-gray-300">
              Join thousands of users who trust our platform for their email security needs
            </p>
            <Button gradientDuoTone="cyanToBlue" size="xl">
              Start Free Trial
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

const features = [
  {
    icon: '🔍',
    title: 'Real-time Detection',
    description: 'Instant analysis of incoming emails for spoofing attempts using advanced algorithms'
  },
  {
    icon: '🛡️',
    title: 'AI-Powered Security',
    description: 'Machine learning models trained to identify sophisticated phishing attempts'
  },
  {
    icon: '📊',
    title: 'Detailed Analytics',
    description: 'Comprehensive reports and insights about detected threats and patterns'
  },
  {
    icon: '🔐',
    title: 'DMARC Integration',
    description: 'Seamless integration with DMARC, SPF, and DKIM authentication protocols'
  },
  {
    icon: '⚡',
    title: 'Quick Response',
    description: 'Immediate alerts and automated actions for suspicious emails'
  },
  {
    icon: '🔄',
    title: 'Continuous Updates',
    description: 'Regular updates to protection mechanisms against emerging threats'
  }
];
