import Link from 'next/link';

export default function Home() {
  return (
    <div>
      <h1>Email Security Analysis Tool</h1>
      <Link href="/api/auth">
        <button>Login with Gmail</button>
      </Link>
    </div>
  );
}