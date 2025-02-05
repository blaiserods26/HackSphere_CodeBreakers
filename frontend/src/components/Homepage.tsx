"use client"
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Navbar, Progress, TextInput } from 'flowbite-react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function HomePage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [emailContent, setEmailContent] = useState('');
  const [scanProgress, setScanProgress] = useState(75);

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
      } else {
        setIsAuthenticated(true);
      }
    };
    checkAuth();
  }, [router]);

  const threatData = {
    labels: ['Phishing', 'Spoofing', 'Malware', 'Spam', 'Safe'],
    datasets: [{
      label: 'Email Threats Analysis',
      data: [12, 19, 3, 5, 45],
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 206, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)',
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
      ],
      borderWidth: 1,
    }],
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-slate-900 dark:from-slate-900 dark:to-background">
      {/* Navigation */}
      <Navbar fluid className="bg-transparent">
        <Navbar.Brand href="/">
          <span className="self-center whitespace-nowrap text-xl font-semibold text-cyan-500">
            EmailGuard
          </span>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Navbar.Link href="/" active className="text-foreground dark:text-white">
            Home
          </Navbar.Link>
          <Navbar.Link href="/pricing" className="text-foreground dark:text-white">
            Pricing
          </Navbar.Link>
          <Navbar.Link href="/profile" className="text-foreground dark:text-white">
            Profile
          </Navbar.Link>
        </Navbar.Collapse>
      </Navbar>

      {/* Dashboard */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Stats Section */}
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-cyan-500/20">
              <h2 className="text-2xl font-bold mb-4 text-foreground dark:text-white">
                Scan Statistics
              </h2>
              <div className="flex items-center justify-center">
                <div className="relative w-40 h-40">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-cyan-500">{scanProgress}%</span>
                  </div>
                  <Progress
                    progress={scanProgress}
                    size="lg"
                    color="cyan"
                    className="w-40 h-40 rounded-full"
                  />
                </div>
              </div>
              <p className="text-center mt-4 text-gray-300">
                Total Emails Scanned: 1,234
              </p>
            </div>

            {/* Threat Analysis Chart */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-cyan-500/20">
              <h2 className="text-2xl font-bold mb-4 text-foreground dark:text-white">
                Threat Analysis
              </h2>
              <Bar data={threatData} />
            </div>
          </div>

          {/* Email Input Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-cyan-500/20">
            <h2 className="text-2xl font-bold mb-4 text-foreground dark:text-white">
              Email Analysis
            </h2>
            <textarea
              className="w-full h-96 p-4 rounded-lg bg-slate-800 text-white border border-cyan-500/20 focus:border-cyan-500 focus:ring-cyan-500"
              placeholder="Paste your email content here..."
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
            />
            <Button gradientDuoTone="cyanToBlue" className="w-full mt-4">
              Analyze Email
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
