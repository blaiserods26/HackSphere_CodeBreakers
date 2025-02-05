import { useEffect, useState } from 'react';

export default function AnalyzeEmails() {
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const res = await fetch('/api/analyze-emails');
        const data = await res.json();
        setResults(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchResults();
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!results) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Email Analysis Results</h1>
      <p>Total Emails Analyzed: {results.total_emails_analyzed}</p>
      {results.results.map((result: any, index: number) => (
        <div key={index} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
          <h3>Email {index + 1}</h3>
          <p>Snippet: {result.snippet}</p>
          {/* Add more analysis results as needed */}
        </div>
      ))}
      <br />
      <Link href="/">
        <button>Back to Home</button>
      </Link>
    </div>
  );
}